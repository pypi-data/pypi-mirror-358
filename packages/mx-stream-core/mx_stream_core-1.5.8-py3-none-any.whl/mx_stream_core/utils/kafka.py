import os

from mx_stream_core.infrastructure.kafka import create_kafka_topic_name


class KafkaUtil:
    @staticmethod
    def get_kafka_bootstrap_server():
        return os.getenv('KAFKA_HOST', 'kafka:9092')

    @staticmethod
    def create_ingestor_topic(entity: str):
        return create_kafka_topic_name('ingestor', entity)

    @staticmethod
    def create_aggregator_topic(entity: str):
        return create_kafka_topic_name('aggregator', entity)

    @staticmethod
    def create_cleaner_topic(entity: str):
        return create_kafka_topic_name('cleaner', entity)

    @staticmethod
    def create_transformation_topic(entity: str):
        return create_kafka_topic_name('transformation', entity)

    @staticmethod
    def create_unification_topic(entity: str):
        return create_kafka_topic_name('unification', entity)

    @staticmethod
    def create_customization_topic(entity: str):
        return create_kafka_topic_name('customization', entity)

    @staticmethod
    def create_summarizer_topic(entity: str):
        return create_kafka_topic_name('summarizer', entity)