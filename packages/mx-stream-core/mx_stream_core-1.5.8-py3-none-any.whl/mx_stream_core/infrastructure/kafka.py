import json
import os
import time

from kafka import KafkaProducer, KafkaAdminClient
from kafka.admin import NewTopic
from kafka.errors import UnknownTopicOrPartitionError, TopicAlreadyExistsError

from pyspark.sql import DataFrame
from pyspark.sql.functions import col, from_json, to_json, struct, unix_millis, expr, when
from typing_extensions import deprecated

from mx_stream_core.config.kafka import default_kafka_bootstrap_server
from mx_stream_core.config.app import service_name

# Create Producer instance
_producer = None


def get_kafka_producer():
    """
    Get a Kafka producer
    :return:
    """
    global _producer
    if _producer is None:
        _producer = KafkaProducer(
            bootstrap_servers=default_kafka_bootstrap_server,
            value_serializer=lambda v: str(v).encode('utf-8')
        )
    return _producer


def read_stream_from_kafka(spark, topic, schema, kafka_bootstrap_server=None) -> DataFrame:
    """
    Read a stream from Kafka
    :param kafka_bootstrap_server:
    :param spark: SparkSession
    :param topic: Kafka topic
    :param schema: Schema of the data
    :return:
    """

    server = default_kafka_bootstrap_server
    if kafka_bootstrap_server is not None:
        server = kafka_bootstrap_server
    max_offsets_per_trigger = os.getenv("MAX_OFFSETS_PER_TRIGGER", 100000)
    print(f"max_offsets_per_trigger: {max_offsets_per_trigger}")
    create_topic_if_needed(topic)
    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", server) \
        .option("subscribe", topic) \
        .option("startingOffsets", "earliest") \
        .option("maxOffsetsPerTrigger", max_offsets_per_trigger) \
        .option("includeHeaders", "true") \
        .load()
    df = df.select(
            col("value").cast("string").alias("json_string"),
            unix_millis(col("timestamp")).alias("kafka_timestamp"),
            col("headers")
        )

    df = df.withColumn(
        "batch_id",
        expr("CAST(element_at(filter(headers, x -> x.key = 'batch_id'), 1).value AS STRING)")
    ).withColumn(
        "start_time",
        expr("CAST(element_at(filter(headers, x -> x.key = 'start_time'), 1).value AS STRING)")
    )

    df = df.withColumn(
    "batch_id",
        when(col("batch_id").isNull(), "unknown").otherwise(col("batch_id"))
    ).withColumn(
        "start_time",
        when(col("start_time").isNull(), col("kafka_timestamp")).otherwise(col("start_time"))
    )
    df = df.select(
        from_json(col("json_string"), schema).alias("data"), 
        col("kafka_timestamp"),
        col("batch_id"),
        col("start_time")
    ).select("data.*", "kafka_timestamp", "batch_id", "start_time")
    return df


def write_stream_to_kafka(df, topic, checkpoint_path):
    """
    Write a stream to Kafka
    :param df: DataFrame
    :param topic: Kafka topic
    :param checkpoint_path: Checkpoint path for the stream
    :return:
    """
    # Convert DataFrame to JSON strings
    json = df.select(to_json(struct(
        *df.columns
    )).alias("value"))

    # Write the merged stream to Kafka
    query = json \
        .writeStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", default_kafka_bootstrap_server) \
        .option("topic", topic) \
        .option("checkpointLocation", checkpoint_path) \
        .start()

    return query


def delivery_report(err, msg):
    """
    Reports the result of a message delivery attempt.
    :param err: The error that occurred or None if the message was delivered successfully.
    :param msg: The message that was sent or failed to send.
    :return:
    """
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))


def produce_kafka_message(topic, message):
    """
    Produce a message to Kafka
    :param topic: Kafka topic
    :param message:  Message to send
    :return:
    """
    producer = get_kafka_producer()
    producer.send(topic, value=message).add_errback(delivery_report)
    producer.flush()  # Wait for all messages to be delivered


def produce_kafka_messages(topic, event_name: str, df: DataFrame, headers=None):
    """
    Produce a message to Kafka
    :param df:
    :param event_name:
    :param topic: Kafka topic
    :param message:  Message to send
    :return:
    """
    producer = get_kafka_producer()
    for json_row in df.toJSON().collect():
        row = json.loads(json_row)
        event_action = row['type'] if 'type' in row else 'Unknown' # action of event (e.g. "create", "update", "delete")
        message = {
            "id": row['id'] if 'id' in row else f"{service_name}_{time.time()}",
            "event": event_name,
            "action": event_action,
            "timestamp": row['timestamp'] if 'timestamp' in row else int(time.time() * 1000),
            "data": json_row
        }
        producer.send(topic, value=message, headers=headers).add_errback(delivery_report)
    producer.flush()  # Wait for all messages to be delivered


@deprecated("Use create_ingestor_topic_name or create_transformation_topic_name instead")
def create_topic_name(ingestor_name: str) -> str:
    """
    :deprecated: Use create_ingestor_topic_name or create_transformation_topic_name instead
    Create a topic name
    :param ingestor_name: Name of the ingestor (e.g. "word")
    :return:
    """
    return f'{service_name}_ingestor_{ingestor_name}'


def create_kafka_topic_name(layer_name: str, woker_name: str) -> str:
    """
    Create a topic name
    :return:
    """
    if layer_name is None or woker_name is None:
        raise ValueError("layer_name and woker_name cannot be None")

    return f'{service_name}_{layer_name}_{woker_name}'


def create_ingestor_topic_name(ingestor_name: str) -> str:
    """
    Create a topic name for an ingestor
    :param ingestor_name: Name of the ingestor (e.g. "word")
    :return:
    """
    return f'{service_name}_ingestor_{ingestor_name}'


def create_transformation_topic_name(transformation_name: str) -> str:
    """
    Create a topic name for a transformation
    :param transformation_name: Name of the transformation (e.g. "book")
    :return:
    """
    return f'{service_name}_transformation_{transformation_name}'


def create_unification_topic_name(unification_name: str) -> str:
    """
    Create a topic name for a unification
    :param unification_name: Name of the unification (e.g. "book")
    :return:
    """
    return f'{service_name}_unification_{unification_name}'


def check_topic_existence(topic_name: str):
    admin_client = KafkaAdminClient(
        bootstrap_servers=default_kafka_bootstrap_server,
        client_id='mindx-stream-core'
    )
    result = None
    try:
        topic_descriptions = admin_client.describe_topics([topic_name])
        if len(topic_descriptions) == 0 or \
            'partitions' not in topic_descriptions[0] or \
            len(topic_descriptions[0]['partitions']) == 0:
            result = False
        else:
            result = True
    except UnknownTopicOrPartitionError:
        result = False
    admin_client.close()
    return result


def create_topic_if_needed(topic_name: str):
    if not check_topic_existence(topic_name):
        admin_client = KafkaAdminClient(
            bootstrap_servers=default_kafka_bootstrap_server,
            client_id='mindx-stream-core'
        )
        new_topic = NewTopic(topic_name, num_partitions=1, replication_factor=1)
        try:
            admin_client.create_topics([new_topic])
        except TopicAlreadyExistsError:
            print(f'Topic already exists: {topic_name}')
        admin_client.close()
