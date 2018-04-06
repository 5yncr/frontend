import os
import platform
import socket

import bencode

HANDLE_FRONTEND_REQUEST = 'handle_frontend_request'
TIMEOUT = 5.0
UNIX_ADDRESS = './unix_socket'
TCP_ADDRESS = ('localhost', 12345)


def send_message(msg):
    """
    Sends message to backend over socket connection and waits for a response
    :param msg: dictionary of info to be sent to backend
    :return:
    """

    # Convert dictionary to send-able type
    data_string = bencode.encode(msg)

    op_sys = platform.system()
    if op_sys == 'Windows':
        response_string = _tcp_send_message(data_string)
    else:
        response_string = _unix_send_message(data_string)

    response = bencode.decode(response_string)

    return response


def _tcp_send_message(msg):
    """
    Sends message to backend over tcp socket and awaits a response
    :param msg:
    :return:
    """

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(TIMEOUT)
    s.connect(TCP_ADDRESS)

    # Send request
    s.sendall(msg)
    s.shutdown(socket.SHUT_WR)

    # Read response from backend
    response = b''
    while True:
        data = s.recv(4096)
        if not data:
            break
        else:
            response += data

    s.close()
    return response


def _unix_send_message(msg):
    """
    Sends message to backend over unix socket and awaits a response
    :param msg:
    :return:
    """

    try:
        os.unlink(UNIX_ADDRESS)
    except OSError:
        # does not yet exist, do nothing
        pass

    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.settimeout(TIMEOUT)
    s.bind(UNIX_ADDRESS)

    # Send request
    s.sendall(msg)
    s.shutdown(socket.SHUT_WR)

    # Read response from backend
    response = b''
    while True:
        data = s.recv(4096)
        if not data:
            break
        else:
            response += data

    s.close()
    return response


if __name__ == '__main__':
    request = {
        'drop_id': 'test',
        'action': 'handle_share_drop',
    }
    respond = send_message(request)
    print(respond.get('message'))
