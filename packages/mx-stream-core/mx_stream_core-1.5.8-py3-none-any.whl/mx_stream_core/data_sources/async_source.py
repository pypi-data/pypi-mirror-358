import os
from pyspark.sql.types import StructType, StructField, StringType

from mx_stream_core.config.kafka import default_kafka_bootstrap_server
from mx_stream_core.data_sources.base import BaseDataSource
from mx_stream_core.infrastructure.kafka import create_topic_if_needed
from mx_stream_core.infrastructure.spark import spark, get_checkpoint_path
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, from_json, coalesce, from_unixtime, expr, when

kafka_event_schema = StructType([
    StructField("event", StringType(), True),
    StructField("timestamp", StringType(), True),
    StructField("data", StringType(), True),
    StructField("id", StringType(), True),
])


class AsyncSource(BaseDataSource):
    """
    Class to represent an asynchronous data source
    :param topics: Kafka topic name
    """

    def __init__(self, topics, kafka_bootstrap_server=None, checkpoint_location=None):
        self.topics = topics
        self.kafka_bootstrap_server = kafka_bootstrap_server
        self.checkpoint_location = checkpoint_location
        self.query = None

    def get(self) -> DataFrame:
        kafka_bootstrap_server = self.kafka_bootstrap_server if self.kafka_bootstrap_server else default_kafka_bootstrap_server
        max_offsets_per_trigger = os.getenv("MAX_OFFSETS_PER_TRIGGER", 100000)
        print(f"max_offsets_per_trigger: {max_offsets_per_trigger}")
        
        for topic in self.topics.split(","):
            print(f"topic: {topic}")
            create_topic_if_needed(topic)
        
        df = spark.readStream.format("kafka") \
            .option("kafka.bootstrap.servers", kafka_bootstrap_server) \
            .option("subscribe", self.topics) \
            .option("startingOffsets", "earliest") \
            .option("maxOffsetsPerTrigger", max_offsets_per_trigger) \
            .option("includeHeaders", "true") \
            .load()
        df = df.select(
            col("topic").alias("topic"),
            col("headers").alias("headers"),
            col("value").cast("string"),
            col("timestamp").cast("timestamp").alias("kafka_timestamp")
        ).withColumn(
            "batch_id",
            expr("CAST(element_at(filter(headers, x -> x.key = 'batch_id'), 1).value AS STRING)")
        ).withColumn(
            "start_time",
            expr("CAST(element_at(filter(headers, x -> x.key = 'start_time'), 1).value AS STRING)")
        ).withColumn(
            "batch_id",
            when(col("batch_id").isNull(), "unknown").otherwise(col("batch_id"))
        ).withColumn(
            "start_time",
            when(col("start_time").isNull(), col("kafka_timestamp")).otherwise(col("start_time"))
        ).withColumn(
            "decoded", from_json(col("value"), kafka_event_schema)
        ).select(
            col("topic"),
            col("decoded.data").alias("data"),
            col("kafka_timestamp"),
            col("batch_id"),
            col("start_time"),
            coalesce(
                from_unixtime(col("decoded.timestamp").cast("long") / 1000).cast("timestamp"),
                col("kafka_timestamp")
            ).alias("timestamp")
        ).filter(col("timestamp").isNotNull())
        return df

    def foreach(self, func, processing_time=None):
        df = self.get()
        stream_writer = df.writeStream.option("checkpointLocation", get_checkpoint_path(self.checkpoint_location))

        # If processing_time is provided, add the trigger option
        if processing_time:
            stream_writer = stream_writer.trigger(processingTime=processing_time)

        self.query = stream_writer.foreachBatch(lambda df, ep: func(df)).start()

    def awaitTermination(self):
        if self.query:
            self.query.awaitTermination()
