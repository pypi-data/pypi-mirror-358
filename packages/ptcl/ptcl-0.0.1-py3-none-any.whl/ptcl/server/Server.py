import ssl
import os
import socket
import threading
from ..socket import AbstractSocket

class Server:
    """
        This class is currently here only conceptually, it is Gemini generated.
        This will be changed.
    """

    def __init__(self, host: str, port: int, handler_class: type[AbstractSocket],
                 use_ssl: bool = False, certfile: str = None, keyfile: str = None):
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

        if self._use_ssl:
            if not certfile or not keyfile:
                raise ValueError("Both 'certfile' and 'keyfile' must be provided when 'use_ssl' is True.")
            if not os.path.exists(certfile) or not os.path.exists(keyfile):
                raise FileNotFoundError(f"SSL certificate or key file not found: '{certfile}', '{keyfile}'")

            self._ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            self._ssl_context.load_cert_chain(certfile, keyfile)
            self._ssl_context.set_ciphers('HIGH:!aNULL:!kRSA:!PSK:!SRP:!DSS:!RC4')
            self._ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2

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
            print(f"Server listening on {self._host}:{self._port} {'with SSL/TLS' if self._use_ssl else ''}...")
            print("Waiting for incoming connections...")

            while True:
                # Accept a new client connection
                # This call blocks until a client connects.
                # 'conn' is the new, dedicated socket for this client.
                # 'addr' is the client's (IP, port) pair.
                conn, addr = self._server_socket.accept()

                # If SSL is enabled, wrap the accepted connection
                current_conn = conn
                if self._use_ssl:
                    try:
                        current_conn = self._ssl_context.wrap_socket(conn, server_side=True)
                        print(f"Main thread: SSL/TLS Handshake successful with {addr}")
                    except ssl.SSLError as e:
                        print(f"Main thread: SSL/TLS Handshake failed with {addr}: {e}")
                        conn.close()  # Close the raw socket if handshake fails
                        continue  # Go back to accept the next connection
                    except Exception as e:
                        print(f"Main thread: Error wrapping socket for {addr}: {e}")
                        conn.close()
                        continue

                # Instantiate the user's custom ConnectionHandler class
                # This object will manage the communication for this specific client.
                handler_instance = self._handler_class(current_conn, addr)

                # Start a new thread to run the handler's __call__ method.
                # The __call__ method contains the infinite loop for receiving/transforming/sending.
                handler_thread = threading.Thread(
                    target=handler_instance,  # Calling the instance runs its __call__ method
                    name=f"ClientHandler-{addr[1]}"  # Custom thread name for debugging
                )
                handler_thread.daemon = True  # Allows the main program to exit cleanly
                handler_thread.start()

        except KeyboardInterrupt:
            print("\nServer shutting down due to user interrupt.")
        except Exception as e:
            print(f"An unexpected error occurred in the main server loop: {e}")
        finally:
            # Ensure the main listening socket is closed when the server stops
            if self._server_socket:
                self._server_socket.close()
                print("Server listening socket closed.")