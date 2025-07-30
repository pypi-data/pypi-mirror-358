from pyspark.sql.types import StructType, StructField, TimestampType, StringType, IntegerType

streaming_query_output_schema = StructType([
    StructField("window_start", TimestampType()),
    StructField("window_end", TimestampType()),
    StructField("topic", StringType()),
    StructField("events", StringType()),
    StructField("event_count", StringType()),  # Ly do ?
    StructField("batch_id", StringType()),
    StructField("start_time", StringType())
])

streaming_query_state_schema = StructType([
    StructField("events", StringType()),
    StructField("event_count", IntegerType()),
    StructField("batch_id", StringType()),
    StructField("start_time", StringType())
])
