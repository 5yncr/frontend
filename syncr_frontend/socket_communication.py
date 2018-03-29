import socket as s

import bencode


class Socket:
    """
    Socket class used to communicate with backend
    """

    sock = None

    def __init__(self, sock=None):
        if sock is None:
            self.sock = s.socket(s.AF_INET, s.SOCK_STREAM)
            self.sock.settimeout(10.0)
        else:
            self.sock = sock

    def connect(self, host, port):
        """
        Connect to specified connection
        :param host: host to connect to
        :param port: post to connect to
        :return: error message or None
        """
        try:
            self.sock.connect((host, port))
        except Exception as e:
            return e
        return None

    def send_message(self, msg):
        """
        Send a connection to backend over a socket
        :param msg: dictionary of info to be sent to backend
        :return:
        """

        # Convert dictionary to send-able type
        data_string = bencode.encode(msg)

        # Send data to backend
        sent = self.sock.sendall(data_string)
        if sent is not None:
            self.sock.close()
            raise RuntimeError("socket connection broke")

    def receive_message(self):
        """
        Listen for a return message from
        :return:
        """
        chunks = []

        while True:
            try:
                chunk = self.sock.recv(2048)
            except Exception as e:
                print("Receiving Message error:", e)
                self.sock.close()
                return None
            if chunk == '':
                break
            chunks.append(chunk)

        # Un-pickle data
        data_string = ''.join(chunks)
        return bencode.decode(data_string)

    def close(self):
        """
        Close the current socket
        :return:
        """
        self.sock.close()
        self.sock = None
