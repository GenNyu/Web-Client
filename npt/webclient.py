import socket
from os import error

HOST = 'www.bing.com'
PORT = 80

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client.connect((HOST, PORT))
    print(f'* Running on http://{HOST}:{PORT}')
except socket.error as e:
    print(f'socket error: {e}')

def _read_file(Name_file, data):
    f = open(Name_file, 'rb+')
    f.write(data)
    f.close()

request = f"GET / HTTP/1.0\r\nHost: {HOST}\r\n\r\n"
client.send(request.encode())
data = client.recv(10000)
request_line = request.split('\r\n')[0]
request_method = request_line.split(' ')[0]
request_url = (request_line.split(' ')[1]).strip('/')
if request_method == 'GET':
    if request_url == '':
        #index_page
        url = 'index.html'
        pass
_read_file(url, data)

client.close()
