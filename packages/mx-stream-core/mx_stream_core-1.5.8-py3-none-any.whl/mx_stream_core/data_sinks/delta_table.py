from delta import DeltaTable
from pyspark.sql import DataFrame
from pyspark.sql.functions import lit, last

from ..data_sinks.base import BaseDataSink
from ..validators.lakehouse_path_validator import LakehousePathValidator

class DeltaTableDataSink(BaseDataSink):
    @classmethod
    def create(cls, delta_location: str, schema=None, input_spark=None, input_validator=None) -> 'DeltaTableDataSink':
        if input_validator:
            validator = input_validator
        else:
            validator = LakehousePathValidator()
        path_is_valid = validator.validate(delta_location)
        if not path_is_valid:
            raise ValueError(f"Invalid path: {delta_location}. Please use the following structure: {validator.path_examples()}")
        return cls(delta_location, schema, input_spark)

    def __init__(self, delta_location: str, schema=None, input_spark=None) -> None:
        self.delta_location = delta_location
        self.schema = schema
        self.spark = input_spark

    def put(self, df: DataFrame) -> None:
        df.write.format('delta').option('mergeSchema', "true").mode('append').save(self.delta_location)

    def get_schema(self):
        return self.schema

    def upsert(self, new_df: DataFrame, sets=None, condition="current.id = new.id") -> None:
        schema = self.schema if self.schema else new_df.schema

        try:
            delta_table = DeltaTable.forPath(self.spark, self.delta_location)
        except:
            self.spark.createDataFrame([], schema) \
                .write \
                .format('delta') \
                .option('mergeSchema', 'true') \
                .mode('overwrite') \
                .save(self.delta_location)
            delta_table = DeltaTable.forPath(self.spark, self.delta_location)

        all_columns = new_df.columns
        all_columns.remove('id')
        agg_exprs = [last(col).alias(col) for col in all_columns]
        new_df = new_df.groupBy("id").agg(*agg_exprs)

        for field in schema.fields:
            if field.name not in new_df.columns:
                new_df = new_df.withColumn(field.name, lit(None).cast(field.dataType))

        delta_table.alias("current") \
            .merge(
            source=new_df.alias("new"),
            condition=condition) \
            .whenMatchedUpdate(set=sets) \
            .whenNotMatchedInsertAll() \
            .execute()

        # Ensure the data is written before proceeding (blocking action)
        self.spark.read.format("delta").load(self.delta_location).count()
