"""
Author:		 Muhammad Tahir Rafique
Date:		 2023-06-19 16:26:01
Project:	 Rabbitmq Utils
Description: Provide class to make RPC Client.
"""

import uuid

from rabbitmq_utils import RabbitMQProducer


class RPCClient(RabbitMQProducer):
    """RPC Client Class."""

    def __init__(
        self,
        host,
        port,
        virtual_host,
        username,
        password,
        exchange,
        exchange_type="topic",
        timeout=None,
        persistent_message=False,
        cafile: str | None = None,
        check_hostname: bool = True,
    ) -> None:
        super().__init__(
            host,
            port,
            virtual_host,
            username,
            password,
            exchange,
            exchange_type,
            persistent_message,
            cafile,
            check_hostname,
        )

        self.timeout = timeout

        self.channel = self.get_channel()
        result = self.channel.queue_declare(queue="", exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True,
        )

        # STATE VARIABLES
        self.response = None
        self.corr_id = None
        self._code = None
        return None

    def get_code(self):
        """Return the code."""
        return self._code

    def set_code(self, code):
        """Set the code."""
        self._code = code
        return None

    def get_response(self):
        """Returning response."""
        return self.response

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body.decode()
        return None

    def close_connection(self):
        """Close the channel connection."""
        self.connection.close()
        return None

    def receive_response(self):
        """Receiving response."""
        # GETTING RESPONSE
        self.connection.process_data_events(time_limit=self.timeout)

        response = self.get_response()
        if not response:
            self.set_code(408)  # Timeout error occur.
        else:
            self.set_code(200)

        # UPDATING RESPONSE
        self.response = response
        return response

    def send_message(self, message, routing_key, return_response=False):
        """Send the message to rabbitmq."""
        # SENDING RESPONSE
        self.response = None
        self.corr_id = str(uuid.uuid4())
        kwargs = {"reply_to": self.callback_queue, "correlation_id": self.corr_id}

        is_sent = super().send_message(
            message, routing_key, close_connection=False, **kwargs
        )

        # RECEIVING RESPONSE
        if return_response:
            response = self.receive_response()

        # CLOSING CONNECTION
        self.close_connection()

        # RETURNING RESPONSE
        if return_response:
            return is_sent, response
        return is_sent
