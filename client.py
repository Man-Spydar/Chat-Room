import errno
import socket
import sys
import winsound
import subprocess
import os
from enum import Enum

# Load client configuration
with open("client_config.txt", "r") as f:
    lines = f.readlines()
    IP = lines[0].split("=")[1].strip()
    PORT = int(lines[1].split("=")[1].strip())
    PERSONAL_FONT_COLOR = lines[2].split("=")[1].strip()
    PEER_FONT_COLOR = lines[3].split("=")[1].strip()
    SERVER_MESSAGE_FONT_COLOR = lines[4].split("=")[1].strip()

class Color(Enum):
    BLACK = 0
    RED = 1
    GREEN = 2
    YELLOW = 3
    BLUE = 4
    MAGENTA = 5
    CYAN = 6
    WHITE = 7

exec(f'PERSONAL_FONT_COLOR = Color.{PERSONAL_FONT_COLOR.upper()}.value')
exec(f'PEER_FONT_COLOR = Color.{PEER_FONT_COLOR.upper()}.value')

# fix multi word alias'

HEADER_LENGTH = 10



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


print("Enter an alias to use in the chat.")
alias = input("Alias: ")

# Create socket and connect
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))
client_socket.setblocking(True)

# Send alias to server
alias_bytes = ("[R]" + alias).encode('utf-8')
alias_header = f"{len(alias_bytes):<{HEADER_LENGTH}}".encode('utf-8')
client_socket.send(alias_header + alias_bytes)


'''
# Receive number of previous messages
line_count = receive_message(client_socket)
line_count = int(line_count['data'])

# Receive and display message history
for _ in range(line_count):
    msg = receive_message(client_socket)
    print(msg['data'].decode('utf-8'))
'''

# Switch to non-blocking mode for chat
client_socket.setblocking(False)

print("\n"*30)
print("Connected.\n")



import ctypes

user32 = ctypes.windll.user32

# Structure to hold window rectangle
class RECT(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long),
    ]

# Find the Windows Terminal window
hWnd = user32.FindWindowW("CASCADIA_HOSTING_WINDOW_CLASS", None)

if hWnd:
    rect = RECT()
    if user32.GetWindowRect(hWnd, ctypes.byref(rect)):
        width = rect.right - rect.left
        height = rect.bottom - rect.top


x, y = rect.left, rect.top

subprocess.Popen(
    [
        "cmd.exe",
        "/k",
        f'python {os.getcwd()}\\clientSender.py {alias} {x} {y + height} {width} {IP} {PORT}'
    ],
    creationflags=subprocess.CREATE_NEW_CONSOLE
)


while True:
    try:

        try:
            while True:
                alias_header = client_socket.recv(HEADER_LENGTH)
                if not len(alias_header):
                    print("Connection closed by server.")
                    sys.exit()

                alias_length = int(alias_header.decode('utf-8').strip())
                sender_alias = client_socket.recv(alias_length).decode('utf-8')

                msg_header = client_socket.recv(HEADER_LENGTH)
                msg_length = int(msg_header.decode('utf-8').strip())
                message = client_socket.recv(msg_length).decode('utf-8')

                color = f"\x1b[3{PERSONAL_FONT_COLOR}m" if sender_alias == alias else f"\x1b[9{PEER_FONT_COLOR}m"
                print(f"{color}{sender_alias}: \x1b[0m{message}")


                winsound.PlaySound('SystemExit', winsound.SND_ALIAS)

        except IOError as e:
            if e.errno not in (errno.EAGAIN, errno.EWOULDBLOCK):
                sys.exit()
            continue

    except:
        client_socket.close()
        sys.exit()
