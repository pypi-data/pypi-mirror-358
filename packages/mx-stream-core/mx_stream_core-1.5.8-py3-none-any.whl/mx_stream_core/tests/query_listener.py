from pyspark.sql.streaming import StreamingQueryListener
import time


class AsyncQueryListener(StreamingQueryListener):
    def __init__(self, timeout_seconds):
        self.timeout_seconds = timeout_seconds
        self.last_data_time = time.time()
        self.status = "ACTIVE"  # ACTIVE hoặc NO_DATA_RECEIVED

    def onQueryProgress(self, event):
        progress = event.progress
        if progress["numInputRows"] > 0:
            self.last_data_time = time.time()  # Cập nhật khi có dữ liệu mới
            self.status = "ACTIVE"
        elif time.time() - self.last_data_time > self.timeout_seconds:
            self.status = "NO_DATA_RECEIVED"  # Gắn trạng thái nếu không có dữ liệu mới
        print(f"Query ID: {event.id}, Status: {self.status}")

    def onQueryStarted(self, event):
        print(f"Query started: {event.id}")

    def onQueryTerminated(self, event):
        print(f"Query terminated: {event.id}")
