import socket
from os import error
#--------------------------------------------------------------
#Lấy Host và lấy Path
URL = 'http://web.stanford.edu/class/cs224w/slides/01-intro.pdf'
HOST = URL.split('/')[2]
PATH = URL.split(f'http://{HOST}')[1]
if PATH == '': 
    PATH = '/'
PORT = 80
#--------------------------------------------------------------
#Hàm lưu dữ liệu vào file tương ứng
def _save_file(Name_file, data):
    f = open(Name_file, 'wb+')
    f.write(data)
    f.close()
#--------------------------------------------------------------
#Kiểm tra kết nối
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client.connect((HOST, PORT))
    print(f'* Running on http://{HOST}:{PORT}')
except socket.error as e:
    print(f'socket error: {e}')
#--------------------------------------------------------------
#Tạo request và gửi request tới sever, nhận dữ liệu từ server
request = f"GET {PATH} HTTP/1.0\r\nHost: {HOST}\r\n\r\n"
client.send(request.encode())
data = client.recv(5000000)
headers = data.split(b'\r\n\r\n')[0]
print(headers)
data = data.split(b'\r\n\r\n')[1] #đang lỗi vì muốn cắt headers ra nó cắt lố cmm
#--------------------------------------------------------------
#Cắt request, path để lấy đuôi file, và method (Bằng GET)
request_line = request.split('\r\n')[0]
request_method = request_line.split(' ')[0]
request_line1 = PATH.split('/')[-1]
request_file = request_line1.split('.')[-1]
#--------------------------------------------------------------
#Kiểm tra method có đúng không, và đuôi file tương ứng (.html, .pdf, .ppt)
if request_method == 'GET':
    if  PATH == '/' or request_file == 'html':
        #index_page
        url = 'index.html'
    elif request_file == 'ppt':
        url = 'Intro_Net_91407.ppt'
    elif request_file == 'pdf':
        url = 'intro.pdf'
print(url)
_save_file(url, data) 

# def mysend(self, msg):
#         totalsent = 0
#         while totalsent < contentLength:
#             sent = self.sock.send(msg[totalsent:])
#             if sent == 0:
#                 raise RuntimeError("socket connection broken")
#             totalsent = totalsent + sent

# def myreceive(self):
#         msg = b''
#         while len(msg) < contentLength:
#             chunk = self.sock.recv(contentLength-len(msg))
#             if chunk == b'':
#                 raise RuntimeError("socket connection broken")
#             msg = msg + chunk
#         return msg


client.close()
