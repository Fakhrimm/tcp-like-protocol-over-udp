# client.py
from lib.connection import Connection
from lib.handler import FileReceiver
from lib.arg import ClientArg
from lib.constants import TIMEOUT
from socket import timeout as socket_timeout

import logging
import sys
import socket

def main():
    logging.basicConfig(format="[i] [Client] %(message)s", level=logging.INFO)

    args = ClientArg()

    file_path = args.file_path  

    connection = Connection("127.0.0.1", args.port_client)

    tcp = FileReceiver(connection, args.host_server, args.port_server, file_path)
    tcp.connect()

    while not tcp.closed:
        try:
            message = connection.receive()
            tcp.handle_message(message)
<<<<<<< HEAD
    except socket_timeout:
        pass
    finally:
        try:
            logging.info("Socket status before closing: %s", connection.socket.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR))
        except OSError:
            logging.info("Socket is already closed.")

        connection.close()
        sys.exit(0)
=======
        except socket_timeout:
            continue

    connection.close()

>>>>>>> d6d65097f3dc314fd72344e326082adb4d5fbbe0

if __name__ == "__main__":
    main()
