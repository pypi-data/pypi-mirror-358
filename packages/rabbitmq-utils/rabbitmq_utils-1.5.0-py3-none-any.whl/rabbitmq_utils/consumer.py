"""
Author:		 Muhammad Tahir Rafique
Date:		 2023-04-14 15:34:40
Project:	 rabbitmq-utils
Description: Provide function to start the rabbitmq consumer.
"""

import ssl
import time

import pika


def callback_test(ch, method, properties, body):
    # GETTING MESSAGE
    message = body.decode()
    print("==================================")
    print(f"INFO: Received Message: \n\n{message}\n")

    # PERFORM YOUR LOGIC HERE
    try:
        import json

        wait_sec = json.loads(message)["wait_time"]
        print(f"INFO: Wating for {wait_sec} seconds.")
        time.sleep(wait_sec)
        print("INFO: Done waiting.")
    except:
        pass

    # ACKNOWLEDGE WORK IS DONE
    ch.basic_ack(delivery_tag=method.delivery_tag)
    print("INFO: Acknowledgment Done.")
    print("==================================")
    print("\n\n")
    return None


class RabbitMQConsumer:
    def __init__(
        self,
        host: str,
        port: str,
        virtual_host: str,
        username: str,
        password: str,
        queue_name: str,
        routing_key: str,
        exchange: str = "",
        exchange_type: str = "topic",
        callback_fun=callback_test,
        max_priority: int | None = None,
        cafile: str | None = None,
        check_hostname: bool = True,
    ) -> None:
        """Constructor."""
        self.host = host
        self.port = port
        self.virtual_host = virtual_host
        self.username = username
        self.password = password
        self.exchange = exchange
        self.queue_name = queue_name
        self.routing_key = routing_key
        self.exchange_type = exchange_type
        self.callback_fun = callback_fun
        self.max_priority = max_priority  # Message priority.
        self.cafile = cafile
        self.check_hostname = check_hostname

        # State Variables
        self.channel = None
        return None

    def make_connection(self):
        """Making connection with rabbitmq."""
        # Making ssl options if required
        if self.cafile:
            context = ssl.create_default_context(cafile=self.cafile)
            context.verify_mode = ssl.CERT_REQUIRED
            context.check_hostname = self.check_hostname
            ssl_options = pika.SSLOptions(context)
        else:
            ssl_options = None

        # Making credentials
        credentials = pika.credentials.PlainCredentials(self.username, self.password)

        # Starting connection
        connection_params = pika.ConnectionParameters(
            host=self.host,
            port=self.port,
            virtual_host=self.virtual_host,
            credentials=credentials,
            ssl_options=ssl_options,
        )
        connection = pika.BlockingConnection(connection_params)
        self.channel = connection.channel()

        # Declear queue
        if self.max_priority:
            self.channel.queue_declare(
                queue=self.queue_name,
                durable=True,
                exclusive=False,
                auto_delete=False,
                arguments={"x-max-priority": self.max_priority},
            )
        else:
            self.channel.queue_declare(
                queue=self.queue_name, durable=True, exclusive=False, auto_delete=False
            )

        # Declear exchange
        if (
            self.exchange != ""
        ):  # No delecration and binding is required for default exchange.
            self.channel.exchange_declare(
                exchange=self.exchange, exchange_type=self.exchange_type, durable=True
            )

            # BINDING QUEUE
            self.channel.queue_bind(
                exchange=self.exchange,
                queue=self.queue_name,
                routing_key=self.routing_key,
            )
        return None

    def start_reveiving(self):
        """Start the consumer consuming process."""
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=self.queue_name, on_message_callback=self.callback_fun
        )
        self.channel.start_consuming()
        return None

    def receive_message(self):
        """Main function of the application."""
        # MAKING CONNECTION
        self.make_connection()

        # STARTING CINSUMPTION
        self.start_reveiving()
        return None
