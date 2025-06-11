from aiokafka import AIOKafkaConsumer
import json
import asyncio
from app.infrastructure.config import get_settings
from app.infrastructure.redis.redis_client import RedisClient

settings = get_settings()

async def consume():
    consumer = AIOKafkaConsumer(
        settings.KAFKA_TOPIC,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    
    await consumer.start()
    try:
        async for msg in consumer:
            print(f"Consumed message: {msg.value}")
            # Here you can add your message processing logic
            # Example: Update Redis cache
            redis_client = await RedisClient.get_redis()
            await redis_client.set(f"kafka_msg_{msg.offset}", json.dumps(msg.value))
    except Exception as e:
        print(f"Error consuming message: {e}")
    finally:
        await consumer.stop()

# You can add more consumer utilities here as needed
