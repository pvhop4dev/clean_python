from aiokafka import AIOKafkaProducer
import json
from app.infrastructure.config import get_settings

settings = get_settings()

class KafkaProducer:
    _instance = None
    _producer = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(KafkaProducer, cls).__new__(cls)
            cls._producer = AIOKafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
        return cls._instance

    @classmethod
    async def get_producer(cls):
        if cls._producer is None:
            cls()
        if not cls._producer._sender.sender_task:
            await cls._producer.start()
        return cls._producer

    @classmethod
    async def close(cls):
        if cls._producer:
            await cls._producer.stop()
            cls._producer = None
            cls._instance = None

# Dependency
async def get_kafka_producer():
    return await KafkaProducer.get_producer()
