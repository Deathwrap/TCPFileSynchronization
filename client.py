import socket
import threading

# Создаем сокет клиента
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
address = input("Введите адрес сервера: ")
port = int(input("Введите порт сервера: "))
client_socket.connect((address, port))


blockSend = False

# Функция для отправки сообщений
def send_message():
    while True and not blockSend:
        message = input()
        client_socket.send(message.encode())

# Функция для принятия сообщений
def receive_message():
    global blockSend
    while True:
        try:
            data = client_socket.recv(1024)
            match(data.decode()):
                case "/sendSyncRequest":
                    print("Вам отправлен запрос на синхронизацию файлов")
                    blockSend = True
                    choice = input("y/n")
                    match (choice):
                        case "y":
                            basePath = input("Введите место расположения для синхронизированных файлов")
                            client_socket.send("y".encode())
                    blockSend = False
                case _:
                    print(data.decode())
        except Exception as e:
            print(f"Ошибка при приеме сообщения: {e}")
            client_socket.close()
            break

# Создаем потоки для отправки и приема сообщений
send_thread = threading.Thread(target=send_message)
receive_thread = threading.Thread(target=receive_message)

# Запускаем потоки
send_thread.start()
receive_thread.start()
