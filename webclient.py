import socket

HOST = "127.0.0.1"  # IP adress server
PORT = 80        # port is used by the server

def create_connection():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    request = "GET / HTTP/1.0\r\nHost: HOST \r\n\r\n"
    client.send(request.encode())
    data = client.recv(10000)
    print(data)
create_connection.close()


