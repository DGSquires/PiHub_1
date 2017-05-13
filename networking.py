import socket


def socket_client(state, host, port=4096):

    """
    :param state: Boolean state of the access request
    :param host: IP address of node to access
    :param port: port of node to access
    :return: 1. Bool for transmission success, 2. new node lock state
    """

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect((host, port))
    except socket.error as e:
        print(e)
        return False, None

    sock.send((str(state)).encode())
    print('message sent: '+state)
    message = sock.recv(4096).decode('utf-8')
    print('message received: '+message)
    sock.close()

    if message is None:
        return False, None
    return True, message
