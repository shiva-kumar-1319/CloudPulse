import json
import asyncio
from typing import Callable, Awaitable, Any, Optional
import aio_pika
from shared.config.settings import settings
from shared.logging.logger import get_logger

logger = get_logger("rabbitmq-messaging")


class RabbitMQClient:
    """
    Asynchronous RabbitMQ Client using aio-pika.
    Handles exchange creation, queue declarations, publishing, and consuming.
    """
    def __init__(
        self,
        url: str = settings.RABBITMQ_URL,
        exchange_name: str = settings.RABBITMQ_EXCHANGE
    ):
        self.url = url
        self.exchange_name = exchange_name
        self.connection: Optional[aio_pika.abc.AbstractRobustConnection] = None
        self.channel: Optional[aio_pika.abc.AbstractRobustChannel] = None
        self.exchange: Optional[aio_pika.abc.AbstractRobustExchange] = None

    async def connect(self) -> bool:
        """
        Establish connection to RabbitMQ server and setup topic exchange.
        Returns True if connected successfully, False otherwise.
        """
        try:
            self.connection = await aio_pika.connect_robust(self.url, timeout=5.0)
            self.channel = await self.connection.channel()
            # Declare durable topic exchange
            self.exchange = await self.channel.declare_exchange(
                name=self.exchange_name,
                type=aio_pika.ExchangeType.TOPIC,
                durable=True
            )
            logger.info(f"Successfully connected to RabbitMQ exchange '{self.exchange_name}'")
            return True
        except Exception as e:
            logger.warning(f"RabbitMQ connection unavailable ({e}). Running in fallback mode.")
            return False

    async def publish(self, routing_key: str, message_data: dict) -> bool:
        """
        Publish JSON message to topic exchange.
        """
        if not self.exchange:
            connected = await self.connect()
            if not connected or not self.exchange:
                logger.error("Failed to publish message: RabbitMQ unavailable")
                return False

        try:
            body = json.dumps(message_data).encode("utf-8")
            message = aio_pika.Message(
                body=body,
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            )
            await self.exchange.publish(message, routing_key=routing_key)
            logger.info(f"Published message with routing key '{routing_key}'")
            return True
        except Exception as e:
            logger.error(f"Error publishing message to RabbitMQ: {e}")
            return False

    async def consume(
        self,
        queue_name: str,
        routing_key: str,
        callback: Callable[[dict], Awaitable[bool]]
    ):
        """
        Declare queue, bind to exchange with routing key, and start consuming messages.
        """
        if not self.channel:
            connected = await self.connect()
            if not connected or not self.channel:
                logger.error("Cannot start consumer: RabbitMQ connection failed")
                return

        # Declare Dead Letter Exchange & Queue
        dlx_exchange_name = f"{self.exchange_name}.dlx"
        dlq_queue_name = f"{queue_name}.dlq"

        dlx_exchange = await self.channel.declare_exchange(
            name=dlx_exchange_name,
            type=aio_pika.ExchangeType.DIRECT,
            durable=True
        )
        dlq = await self.channel.declare_queue(dlq_queue_name, durable=True)
        await dlq.bind(dlx_exchange, routing_key=dlq_queue_name)

        # Declare main queue with DLX configuration
        queue = await self.channel.declare_queue(
            queue_name,
            durable=True,
            arguments={
                "x-dead-letter-exchange": dlx_exchange_name,
                "x-dead-letter-routing-key": dlq_queue_name
            }
        )
        await queue.bind(self.exchange, routing_key=routing_key)

        logger.info(f"Consumer listening on queue '{queue_name}' with routing key '{routing_key}'")

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process(requeue=False):
                    try:
                        payload = json.loads(message.body.decode("utf-8"))
                        logger.info(f"Received message from '{queue_name}'")
                        success = await callback(payload)
                        if not success:
                            logger.warning(f"Consumer processing returned failure for payload {payload.get('event_id')}")
                    except Exception as err:
                        logger.error(f"Error executing message callback: {err}")
                        raise err  # Triggering exception forces message to DLX if message.process fails

    async def close(self):
        """
        Gracefully close RabbitMQ connection and channel.
        """
        if self.connection and not self.connection.is_closed:
            await self.connection.close()
            logger.info("RabbitMQ connection closed.")
