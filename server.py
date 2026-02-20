import socket
import select
import time
import winsound

HEADER_LENGTH = 10

# Load server configuration
with open("server_config.txt", "r") as f:
    lines = f.readlines()

    IP = lines[0].split("=")[1].strip()
    PORT = int(lines[1].split("=")[1].strip())

# Create server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((IP, PORT))
server_socket.listen()

sockets_list = [server_socket]
clients = {}

''' DEBUG '''
print(f"Listening on {IP}:{PORT}...")


def receive_message(client_socket):
    try:
        header = client_socket.recv(HEADER_LENGTH)
        if not len(header):
            return False

        length = int(header.decode('utf-8').strip())
        data = client_socket.recv(length)
        return {'header': header, 'data': data}
    except:
        return False


while True:
    read_sockets, _, exception_sockets = select.select(
        sockets_list, [], sockets_list
    )

    for notified_socket in read_sockets:

        # New connection
        if notified_socket == server_socket:
            client_socket, client_address = server_socket.accept()

            alias = receive_message(client_socket)
            if alias is False:
                continue

            sockets_list.append(client_socket)
            clients[client_socket] = alias

            # Send message history
            '''           
            try:
                with open("Data/Messages.txt", "r") as f:
                    lines = [line for line in f if line.strip()]
            except FileNotFoundError:
                lines = []

            count = str(len(lines)).encode('utf-8')
            count_header = f"{len(count):>{HEADER_LENGTH}}".encode('utf-8')
            client_socket.send(count_header + count)

            for line in lines:
                msg = line.encode('utf-8')
                msg_header = f"{len(msg):>{HEADER_LENGTH}}".encode('utf-8')
                client_socket.send(msg_header + msg)
            '''

            localtime = time.asctime(time.localtime())

            ''' DEBUG '''
            print(
                f"New connection from {client_address[0]}:{client_address[1]} "
                f"as {alias['data'].decode('utf-8')} on {localtime}"
            )

            winsound.PlaySound('SystemHand', winsound.SND_ALIAS)

        # Incoming message
        else:
            message = receive_message(notified_socket)
            if message is False:
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                continue

            alias = clients[notified_socket]

            # Broadcast message
            for client_socket in clients:
                if client_socket != notified_socket and alias['data'][0:3] != b'[R]':
                    client_socket.send(
                        alias['header'] + alias['data'] +
                        message['header'] + message['data']
                    )

            '''
            # Save to history
            with open("Data/Messages.txt", "a") as f:
                f.write(
                    f"{alias['data'].decode('utf-8')}: "
                    f"{message['data'].decode('utf-8')}\n"
                )
            '''

    # Handle exceptions
    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        del clients[notified_socket]
