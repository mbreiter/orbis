import socket as s

END_OF_MESSAGE_DELIMITER = '\n'
MAX_BYTES_TO_RECEIVE = 1
STRING_ENCODING = 'utf-8'


class ClientChannelHandler():
    def __init__(self):
        self.connected = False

    def start_socket_connection(self, port_number, host_name):
        try:
            self.sock = s.socket(s.AF_INET, s.SOCK_STREAM)
            self.sock.connect((host_name, port_number))
            self.connected = True
            print("Connected")
        except s.error:
            print("Cannot connect to  {0} at port {1}. Check to see that the server is running.".format(host_name,
                                                                                                        port_number))

    def close_connection(self):
        self.sock.close()
        self.connected = False
        print("Connection closed")

    def send_message(self, message):
        self.check_socket_connection()
        try:
            # all messages are delimited by a "\n" character
            byte_encoded_message = message.encode(STRING_ENCODING)
            size = len(byte_encoded_message)
            size_bytes = size.to_bytes(4, 'big')

            self.sock.sendall(size_bytes)
            self.sock.sendall(byte_encoded_message)
        except s.error:
            self.close_connection()
            raise Exception("Socket failed to send. Closing socket")

    def receive_message(self):
        self.check_socket_connection()

        size_bytes = self.buffered_recv(4)
        size = int.from_bytes(size_bytes, byteorder='big')

        message_bytes = self.buffered_recv(size)
        received_data = message_bytes.decode(STRING_ENCODING)

        return received_data.strip()

    def buffered_recv(self, size):
        bytes_read = 0
        msg_chunks = []

        while bytes_read < size:
            new_bytes = self.sock.recv(size - bytes_read)
            bytes_read += len(new_bytes)
            msg_chunks.append(new_bytes)

        return b"".join(msg_chunks)

    def check_socket_connection(self):
        if not self.connected:
            raise Exception("Cannot send or receive message on closed socket")
