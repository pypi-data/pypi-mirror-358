import socket
from abc import ABC, abstractmethod
import threading
import ssl

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
                 chunk_size: int = 4096):
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
        print(f"[{threading.current_thread().name}] ConnectionHandler initialized for {self._client_address}")

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

    def __call__(self):
        """
        The system-defined method that handles the request-response cycle
        for the connected client. It continuously receives data,
        applies the user-defined 'transform' method, and sends the result back.
        This method is designed to run in a separate thread.
        """
        thread_name = threading.current_thread().name
        print(f"[{thread_name}] Starting communication loop for {self._client_address}")
        try:
            data = bytes()
            while True:
                # Receive data from the client (adjust buffer size as needed)
                data += self._conn_socket.recv(self._chunk_size)
                if not data:
                    # Client disconnected or sent no more data
                    print(f"[{thread_name}] Client {self._client_address} disconnected.")
                    break

                print(f"[{thread_name}] Received {len(data)} bytes from {self._client_address}")

            # Apply the user-defined transformation
            response_data = self.transform(data)

            # Send the response back
            if response_data is not None:
                self._conn_socket.sendall(response_data)
                print(f"[{thread_name}] Sent {len(response_data)} bytes to {self._client_address}")
            else:
                print(f"[{thread_name}] Transform returned None, no response sent to {self._client_address}.")

        except (socket.error, ConnectionResetError, ssl.SSLError) as e:
            # Handle common connection errors (e.g., client forcibly closed, SSL errors)
            print(f"[{thread_name}] Connection error with {self._client_address}: {e}")
        except Exception as e:
            # Catch any other unexpected errors
            print(f"[{thread_name}] Unexpected error handling client {self._client_address}: {e}")
        finally:
            # Ensure the client's connection socket is closed
            if self._conn_socket:
                self._conn_socket.close()
                print(f"[{thread_name}] Client socket for {self._client_address} closed.")
