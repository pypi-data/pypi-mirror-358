import ssl
import os
import socket
import threading
from ..socket import AbstractSocket
from ..protocol import Protocol
from ..logger import logger_

class Server:
    """
        This class is currently here only conceptually, it is Gemini generated.
        This will be changed.
    """

    def __init__(self, host: str, port: int, handler_class: type[AbstractSocket],
                 protocol: Protocol, use_ssl: bool = False, certfile: str = None,
                 keyfile: str = None):
        """
        Initializes the Server.

        Args:
            host (str): The host IP address to bind to.
            port (int): The port number to listen on.
            handler_class (type[AbstractSocket]): The custom AbstractSocket subclass
                                                     that will handle each client.
            use_ssl (bool): Whether to enable SSL/TLS encryption for connections.
            certfile (str, optional): Path to the server's certificate file (for SSL).
            keyfile (str, optional): Path to the server's private key file (for SSL).
        """
        self._host = host
        self._port = port
        self._handler_class = handler_class
        self._use_ssl = use_ssl
        self._server_socket = None  # The main listening socket
        self._ssl_context = None
        self.protocol = protocol
        self.logger = logger_

        if self._use_ssl:
            if not certfile or not keyfile:
                raise ValueError("Both 'certfile' and 'keyfile' must be provided when 'use_ssl' is True.")
            if not os.path.exists(certfile) or not os.path.exists(keyfile):
                raise FileNotFoundError(f"SSL certificate or key file not found: '{certfile}', '{keyfile}'")

            self._ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            self._ssl_context.load_cert_chain(certfile, keyfile)
            self._ssl_context.set_ciphers('HIGH:!aNULL:!kRSA:!PSK:!SRP:!DSS:!RC4')
            self._ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2

        self.logger.info("Server started.")

    def run(self):
        """
        Starts the server. This method handles binding, listening,
        and continuously accepts new connections, delegating each to a
        new instance of the provided handler_class in a separate thread.
        """
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allows quick restarts

        try:
            self._server_socket.bind((self._host, self._port))
            self._server_socket.listen(5)  # Allow up to 5 queued connections
            self.logger.info(f"Server listening on {self._host}:{self._port} {'with SSL/TLS' if self._use_ssl else ''}...")
            self.logger.info("Waiting for incoming connections...")

            while True:
                conn, addr = self._server_socket.accept()

                # If SSL is enabled, wrap the accepted connection
                current_conn = conn
                if self._use_ssl:
                    try:
                        current_conn = self._ssl_context.wrap_socket(conn, server_side=True)
                        self.logger.info(f"Main thread: SSL/TLS Handshake successful with {addr}")
                    except ssl.SSLError as e:
                        self.logger.warning(f"Main thread: SSL/TLS Handshake failed with {addr}: {e}")
                        conn.close()
                        continue
                    except Exception as e:
                        self.logger.warning(f"Main thread: Error wrapping socket for {addr}: {e}")
                        conn.close()
                        continue

                # This object will manage the communication for this specific client.
                handler_instance = self._handler_class(current_conn, addr, self.protocol)

                # Start a new thread to run the handler's run method.
                # The run method contains the infinite loop for receiving/transforming/sending.
                handler_thread = threading.Thread(
                    target=handler_instance.run,  # Calling the instance runs its run method
                    name=f"ClientHandlerSocket-{addr[1]}"
                )
                handler_thread.daemon = True  # Allows the main program to exit cleanly
                handler_thread.start()
                self.logger.info("Data received and passed to thread.")

        except KeyboardInterrupt:
            self.logger.warning("\nServer shutting down due to user interrupt.")
        except Exception as e:
            self.logger.warning(f"An unexpected error occurred in the main server loop: {e}")
        finally:
            # Ensure the main listening socket is closed when the server stops
            if self._server_socket:
                self._server_socket.close()
                self.logger.info("Server listening socket closed.")