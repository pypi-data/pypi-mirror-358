from pyspark.sql import DataFrame

from .base import BaseDataSource
from ..validators.lakehouse_path_validator import LakehousePathValidator

class DeltaTableDataSource(BaseDataSource):
    @classmethod
    def create(cls, schema, table_path, input_spark=None, input_validator=None) -> 'DeltaTableDataSource':
        # Use validator for factory
        if input_validator:
            validator = input_validator
        else:
            validator = LakehousePathValidator()
        path_is_valid = validator.validate(table_path)
        if not path_is_valid:
            raise ValueError(f"Invalid path: {table_path}. Please use the following structure: \n{validator.path_examples()}")
        return cls(schema, table_path, input_spark)

    def __init__(self, schema, table_path, input_spark=None) -> None:
        self.schema = schema
        self.table_path = table_path
        self.spark = input_spark

    def get(self) -> DataFrame:
        try:
            return self.spark.read.format('delta').load(self.table_path)
        except Exception as e:
            return self.spark.createDataFrame(data=[], schema=self.schema)
