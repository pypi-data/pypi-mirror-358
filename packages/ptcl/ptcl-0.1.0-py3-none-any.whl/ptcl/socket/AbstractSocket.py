import socket
from abc import ABC, abstractmethod
import threading
import ssl
from ..protocol import Protocol
from ..logger import logger_

class AbstractSocket(ABC):
    """
    A base class for handling individual client connections.
    This class is instantiated by the server for each new client.
    Users should inherit from this class and override the 'transform' method.
    The '__call__' method drives the communication loop for this specific client.
    """
    def __init__(self,
                 connected_socket: socket.socket,
                 client_address: tuple,
                 protocol: Protocol,
                 chunk_size: int = 4096, *args, **kwargs):
        """
        Initializes the handler for a single client connection.

        Args:
            connected_socket (socket.socket): The already connected socket object
                                              (can be a regular or SSL-wrapped socket).
            client_address (tuple): The (IP, port) tuple of the connected client.
        """
        self._conn_socket = connected_socket
        self._client_address = client_address
        self._chunk_size = chunk_size
        self.protocol = protocol
        self.logger = logger_
        self.logger.info(f"[{threading.current_thread().name}] ConnectionHandler initialized for {self._client_address}")

    @abstractmethod
    def transform(self, data: bytes) -> bytes:
        """
        Abstract method to be overridden by the user.
        This method defines the custom logic for processing incoming data from a client.

        Args:
            data (bytes): The raw bytes received from the client.

        Returns:
            bytes: The raw bytes to be sent back to the client as a response.
        """
        pass # Must be implemented by any concrete subclass

    def run(self):
        """
        The system-defined method that handles the request-response cycle
        for the connected client. It continuously receives data,
        applies the user-defined 'transform' method, and sends the result back.
        This method is designed to run in a separate thread.
        """
        thread_name = threading.current_thread().name
        self.logger.info(f"[{thread_name}] Starting communication loop for {self._client_address}")
        try:
            while True:
                data = self._conn_socket.recv(self._chunk_size)
                if not data:
                    self.logger.info(f"[{thread_name}] Client {self._client_address} disconnected.")
                    break

                self.logger.info(f"[{thread_name}] Received {len(data)} bytes from {self._client_address}")

                response_data = self.transform(data)

                if response_data is not None:
                    self._conn_socket.send(response_data)
                    self.logger.info(f"[{thread_name}] Sent {len(response_data)} bytes to {self._client_address}")
                else:
                    self.logger.info(f"[{thread_name}] Transform returned None, no response sent to {self._client_address}.")

        except (socket.error, ConnectionResetError, ssl.SSLError) as e:
            self.logger.warning(f"[{thread_name}] Connection error with {self._client_address}: {e}")
        except Exception as e:
            self.logger.warning(f"[{thread_name}] Unexpected error handling client {self._client_address}: {e}")
        finally:
            if self._conn_socket:
                self._conn_socket.close()
                self.logger.info(f"[{thread_name}] Client socket for {self._client_address} closed.")
