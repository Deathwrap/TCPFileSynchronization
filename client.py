import socket
import os
import threading
from datetime import datetime
from tqdm import tqdm
import sys
import win32file
import win32con
import hashlib
import queue
import shutil

SYNC_DATE = 0
FILE_TYPE = 1
FILE_SIZE = 2
FILE_PATH = 3
FILE_NAME = 4
ACTION = 5

CREATE = 1
DELETE = 2
UPDATE = 3
RENAMED = 4

FILE_LIST_DIRECTORY = 0x0001

block = False
observerBlock = False

fileQueue = queue.Queue()
targetPath = ""
basePath = os.path.dirname(os.path.realpath(__file__))

BUFFER = 4096
observerStopFlag = False

sync_socket = socket

def recieve_handler():
    global block
    global sync_socket
    global observerBlock
    while True:
        #print(f"block = {block}")
        if not block:
            data = recieve_message(sync_socket)
            command = data[:3]
            match(command):
                case "000":
                    block = True
                case "001":
                    observerBlock = True
                    send_message(sync_socket, "000")
                    
                    data = recieve_message(sync_socket)
                    sync_time = datetime.strptime(data, '%Y-%m-%d %H:%M:%S.%f')
                    send_message(sync_socket, "date - ok")

                    data = recieve_message(sync_socket)
                    file_type = int(data)
                    send_message(sync_socket, "filetype - ok")

                    if file_type != 0:
                        data = recieve_message(sync_socket)
                        file_size = int(data)
                        send_message(sync_socket, "filesize - ok")

                    filel_path = recieve_message(sync_socket)
                    file_path = os.path.join(targetPath, filel_path)
                    send_message(sync_socket, "filepath - ok")

                    file_name = recieve_message(sync_socket)
                    send_message(sync_socket, "filename - ok")

                    if file_type != 0:
                        print(sync_time, file_type, file_size, file_path, file_name)
                    else:
                        print(sync_time, file_type, file_path, file_name)


                    if file_type == 0:
                        path = os.path.join(targetPath, file_path)
                        if not os.path.exists(path):
                            os.makedirs(os.path.join(targetPath, file_path))
                            send_message(sync_socket, "Папка успешно создана")
                        else:
                            send_message(sync_socket, "Oops")
                    
                    else:
                        if os.path.exists(file_path) and file_size == os.path.getsize(os.path.realpath(file_path)):
                            send_message(sync_socket, "identical")
                        else:
                            send_message(sync_socket, "not-identical")
                            #print(f'Файл или папка {PATH+file_name} не существует.')
                            directory = os.path.dirname(file_path)
                        
                            if not os.path.exists(directory):
                                # Если не существует, создать директорию
                                os.makedirs(directory)
                            
                            with open(file_path, 'wb') as file:
                                received_data = 0
                                while received_data < file_size:
                                    data = sync_socket.recv(BUFFER)
                                    if not data:
                                        break
                                    file.write(data)
                                    received_data += len(data)
                            
                            print(f"Файл '{file_name}' успешно получен от клиента.")
                            file_size = os.path.getsize(os.path.realpath(file_path))
                            msg = str(file_size)
                            send_message(sync_socket, msg)
                    observerBlock = False
                case "002":
                    observerBlock = True
                    send_message(sync_socket, "000")
                    
                    data = recieve_message(sync_socket)
                    sync_time = datetime.strptime(data, '%Y-%m-%d %H:%M:%S.%f')
                    send_message(sync_socket, "date - ok")

                    data = recieve_message(sync_socket)
                    file_type = int(data)
                    send_message(sync_socket, "filetype - ok")

                    if file_type != 0:
                        data = recieve_message(sync_socket)
                        file_size = int(data)
                        send_message(sync_socket, "filesize - ok")

                    filel_path = recieve_message(sync_socket)
                    file_path = os.path.join(targetPath, filel_path)
                    send_message(sync_socket, "filepath - ok")

                    file_name = recieve_message(sync_socket)
                    send_message(sync_socket, "filename - ok")

                    if file_type != 0:
                        print(sync_time, file_type, file_size, file_path, file_name)
                    else:
                        print(sync_time, file_type, file_path, file_name)

                    if file_type == 0:
                        path = os.path.join(targetPath, file_path)
                        if os.path.exists(path):
                            os.makedirs(os.path.join(targetPath, file_path))
                            send_message(sync_socket, "Папка успешно создана")
                            shutil.rmtree(path)
                        else:
                            send_message(sync_socket, "Oops")
                    
                    else:
                        
                    observerBlock = False
                case "003":
                    pass
    
def check_and_send_file_handler():
    global block
    global fileQueue
    global sync_socket
    global observerBlock
    while True:
        if not fileQueue.empty():
            file = fileQueue.get()
            match str(file[ACTION]):
                case "1":
                    send_message(sync_socket, "00" + str(file[ACTION]))
                    while not block:
                        pass
                    send_message(sync_socket, str(file[SYNC_DATE]))
                    print(recieve_message(sync_socket))

                    send_message(sync_socket, str(file[FILE_TYPE]))
                    print(recieve_message(sync_socket))

                    if file[FILE_TYPE] != 0:
                        send_message(sync_socket, str(file[FILE_SIZE]))
                        print(recieve_message(sync_socket))
                        filePath = os.path.join(targetPath, file[FILE_PATH])
                        fileSize = os.path.getsize(filePath)

                    send_message(sync_socket, str(file[FILE_PATH]))
                    print(recieve_message(sync_socket))

                    fileName = file[FILE_NAME]
                    send_message(sync_socket, str(file[FILE_NAME]))
                    print(recieve_message(sync_socket))

                    if file[FILE_TYPE] != 0:
                        identicalAnswer = recieve_message(sync_socket)
                        if identicalAnswer != "identical":
                            
                            with open(filePath, 'rb') as file:
                                # Создаем объект tqdm для отслеживания прогресса передачи файла
                                progress_bar = tqdm(total=fileSize, unit='B', unit_scale=True, file=sys.stdout, desc="", postfix=f"Файл/папка: '{fileName}'")
                                while True:
                                    data = file.read(BUFFER)
                                    if not data:
                                        break
                                    sync_socket.send(data)
                                    # Обновляем прогресс после отправки данных
                                    progress_bar.update(len(data))
                                    # Закрываем прогресс-бар после передачи файла
                                progress_bar.close()
                        size = recieve_message(sync_socket)  # получение данных
                        if int(size) == fileSize:
                            print(f"Файл '{fileName}' успешно отправлен клиенту.")
                    else:
                        print(recieve_message(sync_socket))
                    block = False
                case 2:
                    send_message(sync_socket, "00" + str(file[ACTION]))
                    while not block:
                        pass

                    send_message(sync_socket, str(file[SYNC_DATE]))
                    print(recieve_message(sync_socket))





def calculate_file_hash(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as file:
        while True:
            data = file.read(65536)  # Читаем файл по блокам
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()

def scan_directory(path):
    for root, dirs, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            print(f"scan_directory: file_path = {file_path}")
            add_fileQueue(CREATE, file_path)

def add_fileQueue(action, path):
    global basePath
    global targetPath
    global fileQueue
    relative_path = os.path.relpath(path, targetPath)
    print(f"add_fileQueue: relative_path = {relative_path}")
    if os.path.isdir(path):
        print(f"add_fileQueue: {path} является папкой.")
        file_type = 0
        file_size= 0
        file_name = os.path.basename(path)
    else:
        file_type = 1
        file_size = os.path.getsize(path)
        file_name = os.path.basename(path)
    status = 0
    sync_time = datetime.now()

    fileQueue.put([sync_time, file_type, file_size, relative_path, file_name, action, status])
    return 0

def send_message(dest_socket: socket, msg: str):
    msg_size = len(msg.encode("utf-8")).to_bytes(4, byteorder="big")
    dest_socket.send(msg_size)
    dest_socket.send(msg.encode())

def recieve_message(from_socket: socket):
    msg_size_bytes = from_socket.recv(4)
    msg_size = int.from_bytes(msg_size_bytes, byteorder="big")
    data = from_socket.recv(msg_size)
    return data.decode()

def observer():
    global targetPath
    global observerBlock
    global observerStopFlag
    while True:
        if not observerBlock:
            print(f"observer: if not obseverBlock, obStFl = {observerStopFlag}, obBl = {observerBlock}")
            hDir = win32file.CreateFile(
                targetPath,
                FILE_LIST_DIRECTORY,
                win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
                None,
                win32con.OPEN_EXISTING,
                win32con.FILE_FLAG_BACKUP_SEMANTICS,
                None
            )
            while not observerBlock:
                print(f"observer: while not observerBlock, obStFl = {observerStopFlag}, obBl = {observerBlock}")

                results = win32file.ReadDirectoryChangesW(
                    hDir,
                    1024,
                    True,
                    win32con.FILE_NOTIFY_CHANGE_FILE_NAME |
                    win32con.FILE_NOTIFY_CHANGE_DIR_NAME |
                    win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES |
                    win32con.FILE_NOTIFY_CHANGE_SIZE |
                    win32con.FILE_NOTIFY_CHANGE_LAST_WRITE |
                    win32con.FILE_NOTIFY_CHANGE_SECURITY,
                    None,
                    None
                )
                if not observerBlock:
                    print(f"observer: if not observerBlock 2, obStFl = {observerStopFlag}, obBl = {observerBlock}")

                    for action, file in results:
                        file_path = os.path.join(targetPath, file)
                        print(f"observer: action = {action}, file_path = {file_path}")
                        add_fileQueue(action, file_path)
            win32file.CloseHandle(hDir)

# Создаем сокет клиента
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("***Введите адрес сервера: ")
address = input("---> ")
print("***Введите порт сервера: ")
port = int(input("---> "))

client_socket.connect((address, port))

try:
        msg = recieve_message(client_socket)
        print(msg)
        choice = input()
        send_message(client_socket, choice)
        match (int(choice)):
            case 1:
                while True:
                    msg = recieve_message(client_socket)
                    print(msg)
                    send_msg = input("---> ")
                    match (send_msg):
                        case "/connectUser":
                            client_socket.close()
                            sync_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            desired_address = input("***Введите адресс: ")
                            desired_port = input("***Введите порт: ")
                            sync_socket.connect((desired_address, int(desired_port)))
                            flag = False
                            targetPath = ""
                            while flag != True:
                                path = input("***Введите папку, которая должна быть синхронизирована: ")
                                targetPath = os.path.join(basePath, path)
                                if not os.path.exists(targetPath) or not os.path.isdir(targetPath):
                                    print("***Такой папки не существует или это не папка***")
                                else:
                                    flag = True
                            scan_directory(targetPath)
                            recieve_thread = threading.Thread(target=recieve_handler)
                            send_thread = threading.Thread(target=check_and_send_file_handler)
                            observer_thread = threading.Thread(target=observer)
                            recieve_thread.start()
                            send_thread.start()
                            observer_thread.start()

                        case _:
                            send_message(client_socket, send_msg)
                            
            case 2:
                flag = False
                targetPath = ""
                while flag != True:
                    path = input("***Введите папку, в которой будет происходить синхронизация: ")
                    targetPath = os.path.join(basePath, path)
                    if os.path.exists(targetPath):
                        print("***Такая папку уже существует***")
                    else:
                        os.makedirs(targetPath)
                        flag = True
                address, port = client_socket.getsockname()
                client_socket.close()
                new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                new_socket.bind(('',port))
                new_socket.listen(1)
                print("***Ожидание...***")
                sync_socket, addr = new_socket.accept() 
                print(f"***{addr} присоединился***")
                recieve_thread = threading.Thread(target=recieve_handler)
                send_thread = threading.Thread(target=check_and_send_file_handler)
                send_thread.start()
                recieve_thread.start()
                observer_thread = threading.Thread(target=observer)
                observer_thread.start()

except Exception as e:
        print(f"***Ошибка: {e}***")