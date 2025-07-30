"""
Author:		 Muhammad Tahir Rafique
Date:		 2023-04-13 19:54:14
Project:	 rabbitmq-utils
Description: Provide function to send the message to rabbitmq exchange.
"""

import ssl

import pika


class RabbitMQProducer:
    def __init__(
        self,
        host: str,
        port: str,
        virtual_host: str,
        username: str,
        password: str,
        exchange: str = "",
        exchange_type: str = "topic",
        persistent_message: bool = False,
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
        self.exchange_type = exchange_type
        self.cafile = cafile
        self.check_hostname = check_hostname

        # State Variables
        self.channel = None
        self.connection = None
        self._is_sent = None

        # Delivery Mode
        if persistent_message:
            self._delivery_mode = pika.DeliveryMode.Persistent
        else:
            self._delivery_mode = pika.DeliveryMode.Transient
        return None

    def is_sent(self):
        """Getting send status."""
        return self._is_sent

    def set_sent_status(self, status):
        """Setting send status."""
        self._is_sent = status
        return None

    def get_channel(self):
        """Getting channel that have connection."""
        if self.channel is None:
            # Making ssl options if required
            if self.cafile:
                context = ssl.create_default_context(cafile=self.cafile)
                context.verify_mode = ssl.CERT_REQUIRED
                context.check_hostname = self.check_hostname
                ssl_options = pika.SSLOptions(context)
            else:
                ssl_options = None

            # Making credentials
            credentials = pika.credentials.PlainCredentials(
                self.username, self.password
            )

            # Starting connection
            connection_params = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                virtual_host=self.virtual_host,
                credentials=credentials,
                ssl_options=ssl_options,
            )
            self.connection = pika.BlockingConnection(connection_params)
            self.channel = self.connection.channel()

            # Declaring exchange
            if self.exchange != "":
                self.channel.exchange_declare(
                    exchange=self.exchange,
                    exchange_type=self.exchange_type,
                    durable=True,
                )

            # Turn on delivery confirmations
            self.channel.confirm_delivery()
        return self.channel

    def close_connection(self):
        """Close the channel connection."""
        self.connection.close()
        return None

    def send_message(
        self,
        message: str,
        routing_key: str,
        close_connection: bool = True,
        return_exception: bool = False,
        **kwargs,
    ):
        """Send the message to rabbitmq."""
        # GETTING CHANNEL
        channel = self.get_channel()

        # SENDING MESSAGE
        is_sent = False
        try:
            channel.basic_publish(
                exchange=self.exchange,
                routing_key=routing_key,
                body=message,
                mandatory=True,
                properties=pika.BasicProperties(
                    content_type="text/plain",
                    delivery_mode=self._delivery_mode,
                    **kwargs,
                ),
            )
            is_sent = True
            error = None
        except Exception as e:
            is_sent = False
            error = e

        # Updating status
        self.set_sent_status(is_sent)

        # Closing connection if required.
        if close_connection:
            self.close_connection()

        # If exception is required
        if return_exception:
            return is_sent, error
        # Otherwise just return the status.
        return is_sent
