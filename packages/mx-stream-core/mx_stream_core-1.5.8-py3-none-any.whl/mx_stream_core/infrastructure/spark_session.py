import os
import sys

from pyspark.sql import SparkSession

def create_spark_session(s3_endpoint, s3_access_key_id, s3_secret_access_key):
  # Set Python environment variables
  os.environ['PYSPARK_PYTHON'] = sys.executable
  os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable
  
  return (SparkSession.builder
    .appName("DeltaLakeWriter")
    .master("local[*]")
    # Core configurations
    .config("spark.driver.memory", "2g")
    .config("spark.executor.memory", "2g")
    # Delta Lake configuration
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
    # Dependencies
    .config("spark.jars.packages", 
            "org.apache.hadoop:hadoop-aws:3.3.1,"
            "com.amazonaws:aws-java-sdk-bundle:1.12.261,"
            "io.delta:delta-spark_2.12:3.1.0,"
            "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1")
    # S3 configuration
    .config("spark.hadoop.fs.s3a.endpoint", s3_endpoint)
    .config("spark.hadoop.fs.s3a.access.key", s3_access_key_id)
    .config("spark.hadoop.fs.s3a.secret.key", s3_secret_access_key)
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
    .config("spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")
    .config("spark.delta.logStore.class", "org.apache.spark.sql.delta.storage.S3SingleDriverLogStore")
    .getOrCreate())
