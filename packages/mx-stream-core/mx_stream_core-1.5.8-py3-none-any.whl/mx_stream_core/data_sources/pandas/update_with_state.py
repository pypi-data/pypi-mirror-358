import json
import os

import pandas as pd
from pyspark.sql.streaming.state import GroupState


def update_with_state(key, pdf_iterator, state: GroupState):
    """
    Function to handle the state of the group with `applyInPandasWithState`.
    :param key: Key of the group (e.g., (window, topic))
    :param pdf_iterator: Iterator containing pandas DataFrames.
    :param state: State of the group.
    :return: Resulting pandas DataFrame.
    """
    # Step 1: Extract info from passed arguments
    window_info = extract_window_info(key)
    current_state = get_or_create_current_state(state)
    new_events, idle_processing_timeout, batch_id, start_time = extract_new_events(pdf_iterator)

    # Step 2: Merge new event to current_state
    merge_new_events_to_current_state(current_state, new_events, batch_id, start_time)

    # Step 3: Handle window timeout
    # Is the window timed out?
    if state.hasTimedOut:
        # Yes, proceed to close the window
        # Get the data from window to return
        closed_window_data = prepare_closed_window_data(current_state, window_info)
        # Remove events from state for correctness and resource freeing
        state.remove()
    else:
        # No, keep the data in the state for future processing
        set_state_for_next_update(current_state, state)
        set_timeout_for_next_update(idle_processing_timeout, state, window_info)
        # No data to return yet
        closed_window_data = []

    return closed_window_data


def extract_window_info(key):
    return {
        "window_start": key[0].get("start"),
        "window_end": key[0].get("end"),
        "topic": key[1]
    }


def get_or_create_current_state(state: GroupState):
    """Lấy trạng thái hiện tại (nếu có)."""
    current_state = {
        "events": [], 
        "event_count": 0,
        "batch_id": "unknown",  
        "start_time": None
    }
    if state.exists:
        state_value = state.get
        current_state = {
            "events": json.loads(state_value[0]), 
            "event_count": state_value[1],
            "batch_id": state_value[2],          # Lấy batch_id từ state
            "start_time": state_value[3]         # Lấy start_time từ state
        }
    return current_state


def extract_new_events(pdf_iterator):
    """Trích xuất danh sách sự kiện từ các bản ghi mới."""
    windows_df = pd.concat(list(pdf_iterator))
    windows = windows_df.to_dict("records")
    new_events = [window.get("data") for window in windows]
    idle_processing_timeout = extract_idle_processing_timeout(windows)
    # Lấy batch_id và start_time từ tất cả các rows
    batch_ids = set(window.get("batch_id", "unknown") for window in windows)
    start_times = set(window.get("start_time") for window in windows if window.get("start_time") is not None)
    
    # Nếu có nhiều batch_id khác nhau, có thể log warning
    if len(batch_ids) > 1:
        print(f"Warning: Multiple batch_ids found in window: {batch_ids}")
    
    # Lấy giá trị đầu tiên hoặc unknown
    batch_id = next(iter(batch_ids)) if batch_ids else "unknown"
    start_time = next(iter(start_times)) if start_times else None
    
    return new_events, idle_processing_timeout, batch_id, start_time


def extract_idle_processing_timeout(windows):
    idle_processing_timeout = os.getenv("DEFAULT_IDLE_PROCESSING_TIMEOUT", 30000)
    if len(windows) > 0:
        idle_processing_timeout = windows[0].get('idle_processing_timeout')
    return idle_processing_timeout


def merge_new_events_to_current_state(current_state, new_events, batch_id, start_time):
    current_state["events"].extend(new_events)
    current_state["event_count"] += len(new_events)
    if current_state["batch_id"] == "unknown":
        current_state["batch_id"] = batch_id
    if current_state["start_time"] is None:
        current_state["start_time"] = start_time


def prepare_closed_window_data(current_state, window_info):
    batch = pd.DataFrame([{
        **window_info,
        "events": json.dumps(current_state["events"]),
        "event_count": str(current_state["event_count"]),
        "batch_id": current_state["batch_id"] or "unknown",
        "start_time": current_state["start_time"] or str(int(window_info["window_start"].timestamp()))
    }])
    batches = [batch]
    return batches


def set_timeout_for_next_update(idle_processing_timeout, state, window_info):
    current_processing_time = state.getCurrentProcessingTimeMs()
    window_end_ms = window_info.get("window_end").timestamp() * 1000
    timeout_at = window_end_ms - current_processing_time  # Tinh thoi gian timeout
    if timeout_at < 0:
        timeout_at = 1  # Hàm setTimeoutDuration chỉ nhận tham số > 0
    else:
        timeout_at = timeout_at + idle_processing_timeout
    state.setTimeoutDuration(timeout_at)


def set_state_for_next_update(current_state, state):
    current_state["events"] = [json.dumps(item) if not isinstance(item, str) else item for item in
                               current_state["events"]]
    state.update((
        current_state["events"], 
        current_state["event_count"],
        current_state["batch_id"],
        current_state["start_time"]
    ))
