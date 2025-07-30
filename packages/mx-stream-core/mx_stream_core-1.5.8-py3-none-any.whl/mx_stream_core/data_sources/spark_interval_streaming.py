from pyspark.sql import DataFrame
from mx_stream_core.infrastructure.spark import spark
from mx_stream_core.infrastructure.kafka import read_stream_from_kafka
from mx_stream_core.data_sources.base import BaseDataSource


class SparkIntervalStreaming(BaseDataSource):
    def __init__(self, checkpoint_location) -> None:
        self.query = None
        self.checkpoint_location = checkpoint_location

    def get(self) -> DataFrame:
        df = spark.readStream.format("rate").option("rowsPerSecond", 1).load()  # Nguồn dummy

        return df

    def foreach(self, func, processing_time=None):
        df = self.get()
        stream_writer = df.writeStream.option("checkpointLocation", self.checkpoint_location)

        # If processing_time is provided, add the trigger option
        if processing_time:
            stream_writer = stream_writer.trigger(processingTime=processing_time)

        self.query = stream_writer.foreachBatch(lambda _, epoch_id: func()).start()

    def awaitTermination(self):
        if self.query:
            self.query.awaitTermination()
