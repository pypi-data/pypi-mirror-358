from __future__ import annotations

import logging
import socket
from typing import Optional

from bedger.edge import errors
from bedger.edge.config import Config
from bedger.edge.entities import Message, Severity

logger = logging.getLogger("bedger.edge.connection")


class ConnectionManager:
    """Manages a connection to a UNIX socket for sending and receiving messages.

    This class provides context manager support for establishing and tearing
    down a connection to a UNIX socket.

    Attributes:
        _config (Config): The configuration containing the socket path.
        _socket (Optional[socket.socket]): The current socket connection.
    """

    def __init__(self, config: Config = Config()):
        """Initializes the ConnectionManager.

        Args:
            config (Config): Configuration for the connection. Defaults to a new `Config` instance.
        """
        self._config = config
        self._socket: Optional[socket.socket] = None

    def __enter__(self) -> ConnectionManager:
        """Establishes the socket connection when entering the context.

        Returns:
            ConnectionManager: The instance of the ConnectionManager.
        """
        self._connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """Closes the socket connection when exiting the context."""
        self._disconnect()

    def _connect(self) -> None:
        """Establish a connection to the UNIX socket.

        Raises:
            errors.SocketPermissionDeniedError: If the application does not have permission to connect to the socket.
            errors.SocketFileNotFoundError: If the socket file is not found at the specified path.
            errors.SocketConnectionError: If any other error occurs during the connection attempt.
        """
        logger.info(f"Attempting to connect to socket at {self._config.socket_path}")
        try:
            self._socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self._socket.connect(self._config.socket_path)
            logger.info("Successfully connected to the socket")
        except PermissionError:
            logger.error("Permission denied: Unable to connect to the socket. Ensure you have the correct permissions.")
            raise errors.SocketPermissionDeniedError("Permission denied to connect to socket. Are you running as root?")
        except FileNotFoundError:
            logger.error("Socket file not found. Verify the server is running and the socket path is correct.")
            raise errors.SocketFileNotFoundError("Socket file not found. Is the server running?")
        except Exception as e:
            logger.exception(f"Unexpected error while connecting to the socket: {e}")
            raise errors.SocketConnectionError(f"An unexpected error occurred while connecting to the socket: {e}")

    def _disconnect(self) -> None:
        """Close the socket connection gracefully.

        Ensures the socket is closed and cleaned up properly, even in case of errors.
        """
        if self._socket:
            try:
                logger.info("Closing the socket connection")
                self._socket.close()
            except Exception as e:
                logger.warning(f"Error occurred while closing the socket: {e}")
            finally:
                self._socket = None

    def send_event(self, event_type: str, severity: str | Severity, payload: dict) -> None:
        """Send an event message through the socket.

        Args:
            event_type (str): The type of event being sent.
            severity (str | Severity): The severity level of the event.
            payload (dict): The event's payload details.

        Raises:
            errors.SocketNotConnectedError: If no active socket connection exists.
            errors.SocketBrokenPipeError: If the socket connection is lost during message transmission.
            errors.SocketCommunicationError: If any error occurs during socket communication.
        """
        if not self._socket:
            logger.error("Attempted to send a message without an active socket connection.")
            raise errors.SocketNotConnectedError("No active socket connection. Ensure the connection is established.")

        try:
            message = Message(
                event_type=event_type,
                severity=severity,
                details=payload,
            )
            message_json = message.model_dump_json()
            logger.debug(f"Prepared message: {message_json}")

            logger.debug("Sending message")
            self._socket.sendall(message_json.encode())

            ack = self._socket.recv(1024)
            logger.info(f"Received acknowledgment from server: {ack.decode()}")
        except BrokenPipeError:
            logger.error("Broken pipe error: The socket connection was lost during message transmission.")
            raise errors.SocketBrokenPipeError("Socket connection lost. Unable to send message.")
        except socket.error as e:
            logger.error(f"Socket error occurred: {e}")
            raise errors.SocketCommunicationError(f"Socket error during communication: {e}")
        except Exception as e:
            logger.exception(f"Unexpected error while sending the message: {e}")
            raise errors.SocketCommunicationError(f"Unexpected error occurred: {e}")
