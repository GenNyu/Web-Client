import socket
from os import error

HOST = input('Enter the addr: ')
PORT = 80

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client.connect((HOST, PORT))
    print(f'* Running on http://{HOST}:{PORT}')
except socket.error as e:
    print(f'socket error: {e}')
request = f"GET / HTTP/1.0\r\nHost: {HOST}\r\n\r\n"
client.send(request.encode())
data = client.recv(10000).decode()
print(data)


client.close()
