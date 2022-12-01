import socket
import os
from threading import Thread
import time
#--------------------------------------------------------------
#Lấy Host và lấy Path

#--------------------------------------------------------------
def create_request(host,path,method='GET'):
    request =  '{} {} HTTP/1.1\r\nHost: {}\r\nConnection: keep alive\r\n\r\n'.format(method, path, host)
    print(request)
    return request.encode()

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


def _save_file(Name_file, data):
    print("Current working dir : %s" % os.getcwd())
    f = open(Name_file, 'wb+')
    f.write(data)
    f.close()

#--------------------------------------------------------------
def content_url(body):
    content_url_check = b'href="'
    list_file = bytes()
    #Searching for content length in the header
    for line in body.split(b'</td></tr>'):
        if content_url_check in line:
            list_file += (line.split(content_url_check)[1]).split(b'"')[0] + b"|"
    return list_file.decode()
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
    if  PATH == '/' or request_file == 'html' or request_file == "" :
        #index_page
        file_name = 'index.html'
    else: 
        file_name = request_file
    print("Save as file: ", file_name)
    print("----------------------------")
    _save_file(file_name, body)
    if request_file == "":
        return body


def get_folder_content(client, HOST, PATH):
    # Directory
    directory = PATH.split('/')[-2]
    parent_dir = os.getcwd()
    path = os.path.join(parent_dir, directory)
    os.makedirs(path, exist_ok=True)
    print("Directory '% s' created" % directory)
    os.chdir(path)
    body = get_single_content(HOST, PATH, client)
    url_file = content_url(body)
    url_file_cut = url_file.split('|')[0]
    url_file = url_file.split(url_file_cut)[1]
    for line in url_file.split('|'):
        if line != "":
            new_url = "http://"+HOST+PATH+line
            print("Save file at:", new_url)
            new_path = PATH+line
            #get_single_content(HOST, new_path, client)
            thread_num = 10
            receive_t = Thread(target=get_single_content(HOST, new_path, client))
            receive_t.start()

URL = 'http://web.stanford.edu/class/cs143/handouts/'
HOST = URL.split('/')[2]
PATH = URL.split(f'http://{HOST}')[1]
if PATH == '':
    PATH = '/'
PORT = 80

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client.connect((HOST, PORT))
    print(f'* Running on http://{HOST}:{PORT}')
except socket.error as e:
    print(f'socket error: {e}')
print("start work")
start = time.time()
receive_thread = Thread(target=get_folder_content(client, HOST, PATH))
receive_thread.start()
end = time.time()
print(f'Download in {end - start} seconds')
client.close()
input('Press ENTER to exit')
