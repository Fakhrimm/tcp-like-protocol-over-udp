from mimetypes import init
from .connection import MessageInfo, Connection
from .segment import FlagEnum
from .segment import Segment
from .tcp import TCPClient, TCPStatusEnum, TCPServer
from .segment_sender import SenderBuffer
import logging

class FileReceiver(TCPClient):
    def __init__(self, connection: Connection, ip: str, port: int, file_path: str) -> None:
        super().__init__(connection, ip, port)
        self.file_path = file_path
        self.file_data = b""  # Buffer

    def handle_message(self, message: MessageInfo):
        # initial three-way handshake
        if self.status == TCPStatusEnum.WAITING_FIRST_PACKET and message.segment.flag == FlagEnum.SYN_ACK_FLAG:
            super().handle_message(message)
            return

        # data transfer
        elif self.status == TCPStatusEnum.WAITING_FIRST_PACKET and message.segment.flag == FlagEnum.NO_FLAG:
            super().handle_message(message)
            self.handle_data(message.segment)

        elif self.status == TCPStatusEnum.ESTABLISHED and message.segment.flag == FlagEnum.NO_FLAG:
            self.handle_data(message.segment)

        # other is closing the connection
        elif self.status == TCPStatusEnum.CLOSE_WAIT and message.segment.flag == FlagEnum.FIN_FLAG:
            self.close()
            return

    def handle_data(self, segment: Segment):
        if segment.sequence_number == self.server_sequence_number and segment.is_valid():
            self.file_data += segment.data

            self.server_sequence_number += 1

            # send ACK for the received segment
            ack_segment = Segment.ack_segment(0, segment.sequence_number + 1)
            self.connection.send(MessageInfo(self.ip, self.port, ack_segment))

            if len(segment.data) < 1460:
                self.write_to_file()
        else:
            logging.info(f"Ignoring out-of-order or invalid segment with sequence number {segment.sequence_number}")

    def write_to_file(self):
        with open(self.file_path, "wb") as file:
            file.write(self.file_data)

        logging.info(f"File received and saved at: {self.file_path}")
        
class FileSender(TCPServer):
    sender_buffer: SenderBuffer
    receiver_ack_number: int

    def __init__(self, filePath: str, connection: Connection, ip: str, port: int, ack_number: int) -> None:
        super().__init__(connection, ip, port)
        self.receiver_ack_number = ack_number
        self.sender_buffer = SenderBuffer(connection, ip, port, filePath, ack_number)

    def begin_transfer(self):
        print("Begin tranfsfer")
        self.sender_buffer.send(self.receiver_ack_number)

    def handle_message(self, message: MessageInfo):
        self.sender_buffer.send(message.segment.ack)