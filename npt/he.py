import socket
import os
from threading import Thread
import time
#--------------------------------------------------------------
#Tạo request để gửi tới server
def create_request(host,path,method='GET'):
    request =  '{} {} HTTP/1.1\r\nHost: {}\r\nConnection: keep alive\r\n\r\n'.format(method, path, host)
    print(request)
    return request.encode()
#Hàm xác định content_length từ header
def content_length(client):
    end_of_header = b'\r\n\r\n'
    content_length_check = b'Content-Length:'
    header = bytes()
    chunk = bytes()
    #Receiving the header sent from sever
    try:
        while end_of_header not in header:
            chunk = client.recv(1) #We receive the header chunk by chunk so we don't accidentally receive the body
            if not chunk:   
                break
            else:
                header += chunk
    except socket.timeout:
        return -1
    print(header.decode())
    #Searching for content length in the header
    for line in header.split(b'\r\n'):
        if content_length_check in line:
            return int(line[len(content_length_check):])
    return False

#Hàm lưu file
def _save_file(Name_file, data):
    print("Current working dir : %s" % os.getcwd())
    f = open(Name_file, 'wb+')
    f.write(data)
    f.close()
#Hàm lấy những file có trong folder
def content_url(body):
    content_url_check = b'href="'
    list_file = bytes()
    #Searching for content length in the header
    for line in body.split(b'</td></tr>'):
        if content_url_check in line:
            list_file += (line.split(content_url_check)[1]).split(b'"')[0] + b"|"
    return list_file.decode()
#Hàm lưu file đơn
def get_single_content(HOST, PATH, client):
#Tạo request và gửi request tới sever
    request = create_request(HOST, PATH)
    client.sendall(request)
    length = content_length(client)
    if length == -1:
        print("Connection time out while retrieving header\nDownload failed")
        return
    #Receive the body sent from sever
    body = bytes()
    data = bytes()

    try:
        if length!=False: #Receiving the body via content length
            while len(body)<length:
                data = client.recv(4096)
                body += data
        else: #Receiving the body via Transfer-Encoding: chunked
            while True:
                chunk_info = bytes()
                temp = bytes()
                end_line = b'\r\n'
                while end_line not in chunk_info:
                    temp = client.recv(1)
                    chunk_info += temp
                chunk_size = int(chunk_info.decode().split("\r")[0],16)
                if chunk_size == 0 :
                    break
                temp_data = bytes()

                while len(temp_data) < chunk_size:
                    data = client.recv(1)
                    temp_data += data
                data = client.recv(1)
                body += temp_data
    except socket.timeout:
        print("Connection time out while retrieving the body!!!\n Download failed")
        return
    request_file = PATH.split('/')[-1]
    if  PATH == '/' or PATH.count(".") == 0:
        return body
    else: 
        file_name = request_file
    print("Save as file: ", file_name)
    print("----------------------------")
    _save_file(file_name, body)
        
#Hàm lưu folder
def get_folder_content(client, HOST, PATH):
    body = get_single_content(HOST, PATH, client)
    url_file = content_url(body)
    #Chúng ta cần xét trong phần body của sever có url_file hay không, nếu không có thì nó là file .hmtl không thì sẽ là folder
    if url_file.count("|") > 1:
        url_file_cut = url_file.split('|')[0]
        url_file = url_file.split(url_file_cut)[1]
        # Directory
        directory = PATH.split('/')[-2]
        parent_dir = os.getcwd()
        path = os.path.join(parent_dir, directory)
        os.makedirs(path, exist_ok=True)
        print("Directory '% s' created" % directory)
        os.chdir(path)
        for line in url_file.split('|'):  
            if line != "":
                new_url = "http://"+HOST+PATH+line
                print("Save file at:", new_url)
                new_path = PATH+line
                receive_t = Thread(target=get_single_content(HOST, new_path, client))
                receive_t.start() 
    else: 
        if  PATH == '/':
            file_name = "index.html"
            _save_file(file_name, body)
        else:
            file_name = PATH.split('/')[-1]+".html"
            _save_file(file_name, body)
        print("Save as file: ", file_name)
        print("----------------------------")

print("Input http link: ")
URL = input()
HOST = URL.split('/')[2]
PATH = URL.split(f'http://{HOST}')[1]
if PATH == '':
    PATH = '/'
PORT = 80
#Kết nối với server với phương thức TCP và IPv4
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client.connect((HOST, PORT))
    print(f'* Running on http://{HOST}:{PORT}')
except socket.error as e:
    print(f'socket error: {e}')
print("start work")
start = time.time()
#Vì chúng ta không thể biết URL này là folder hay file nên chúng ta sẽ đưa những URL có PATH có đuôi = "/" hoặc không có đuôi file "."
if URL[-1]=="/" or PATH.count(".") == 0:
    receive_thread = Thread(target=get_folder_content(client, HOST, PATH))
    receive_thread.start()
else:
    get_single_content(HOST, PATH, client)
end = time.time()
print(f'Download in {end - start} seconds')
client.close()
input('Press ENTER to exit')
