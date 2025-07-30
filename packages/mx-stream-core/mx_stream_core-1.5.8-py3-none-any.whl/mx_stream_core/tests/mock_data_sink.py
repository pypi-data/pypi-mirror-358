from pyspark.sql import DataFrame
from mx_stream_core.data_sinks.base import BaseDataSink
from pyspark.sql.functions import col, expr


class MockDataSink(BaseDataSink):
    def __init__(self, spark=None, schema=None, current_data_source=None) -> None:
        if current_data_source is None:
            current_data_source = []
        self.schema = schema
        self.df: DataFrame = None
        if schema is not None and spark is not None:
            self.df = spark.createDataFrame(current_data_source, schema=schema)

        super().__init__()

    def put(self, df: DataFrame) -> None:
        if self.schema is None and self.df is None:
            self.df = df
        else:
            self.df = self.df.unionByName(df)

    def show(self):
        if self.df:
            self.df.show()

    def upsert(self, new_df: DataFrame, sets=None, condition="current.id = new.id") -> DataFrame:
        """
        Upsert a DataFrame into this sink. This method will merge the new DataFrame with the data that already exists in this sink based on the condition given. If the condition is not given, it will join based on the 'id' column.

        :param new_df: The DataFrame to be upserted
        :type new_df: DataFrame
        :param sets: The list of columns to be updated. If not given, it will update all columns.
        :type sets: list
        :param condition: The condition of the join. If not given, it will join based on the 'id' column.
        :type condition: str
        :return: The merged DataFrame
        :rtype: DataFrame
        """
        combined_product_items_df = new_df.select(
            *[col(col_name).alias(col_name) for col_name in new_df.columns],
        ).alias('new')

        current_column = self.df.columns
        current_column.remove('id')

        # Sử dụng điều kiện join phức tạp
        merged_df = self.df.alias('current').join(
            combined_product_items_df,
            expr(condition),
            'outer'
        ).selectExpr(
            'COALESCE(current.id, new.id) as id',
            *[f"COALESCE(new.{col_name}, current.{col_name}) as {col_name}" for col_name in current_column]
        )
        self.df = merged_df
        return self.df

    def get(self) -> DataFrame:
        return self.df
