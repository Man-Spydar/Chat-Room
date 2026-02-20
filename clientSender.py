import sys
import socket
import ctypes
import time

alias = sys.argv[1]

x = int(sys.argv[2])
y = int(sys.argv[3])
width = int(sys.argv[4])
IP = sys.argv[5]
PORT = int(sys.argv[6])


user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

hWnd = kernel32.GetConsoleWindow()
if hWnd:
    # Restore in case maximized/minimized
    SW_RESTORE = 9
    user32.ShowWindow(hWnd, SW_RESTORE)
    time.sleep(0.1)

    # Move and resize
    user32.MoveWindow(hWnd, x, y, width, 60, 1)



HEADER_LENGTH = 10

# Create socket and connect
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))
client_socket.setblocking(True)

# Send alias to server
alias_bytes = alias.encode('utf-8')
alias_header = f"{len(alias_bytes):<{HEADER_LENGTH}}".encode('utf-8')
client_socket.send(alias_header + alias_bytes)
try:
    while True:
        text = input(f"Enter a message: ")
        if text.strip():
            message_bytes = text.encode('utf-8')
            message_header = f"{len(message_bytes):<{HEADER_LENGTH}}".encode('utf-8')
            client_socket.send(message_header + message_bytes)
except KeyboardInterrupt:
    print("\nExiting chat.")
finally:
    client_socket.close()