import socket
import threading
import pickle

# Создаем сокет сервера
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('', 8080))
server_socket.listen(5)

print(f"Сервер запущен с адресом {server_socket.getsockname()}")

def send_message(dest_socket: socket, msg):
    msg_size = len(msg.encode("utf-8")).to_bytes(4, byteorder="big")
    dest_socket.send(msg_size)
    dest_socket.send(msg.encode())

def recieve_message(from_socket: socket):
    msg_size_bytes = from_socket.recv(4)
    msg_size = int.from_bytes(msg_size_bytes, byteorder="big")
    data = from_socket.recv(msg_size)
    return data.decode()

# Список клиенто
clients = []

# Функция для обработки сообщений от клиентов
def handle_client(client_socket: socket):
    welcome_msg = "Добро пожаловать в систему для синхронизации файлов\nВыберите, Вы инициатор синхронизации (1) или будете ожидать приглашения(2)?"
    send_message(client_socket, welcome_msg)
    choice = int(recieve_message(client_socket))
    match (choice):
        case 1:
            msg = "Для просмотра команд введите /help"
            send_message(client_socket, msg)
            while True:
                try:
                    data = recieve_message(client_socket)
                    if not data:
                        clients.remove(client_socket)
                        client_socket.close()
                        break
                    match(data):
                        case "/help":
                            msg = "/listUsers - выводит список пользователей\n/connectUser - отправить запрос на синхронизацию файлов"
                            send_message(client_socket, msg)
                        case "/listUsers":
                            msg = ""
                            i = 0
                            for client in clients:
                                if client != client_socket.getpeername():
                                    address, port = client
                                    msg += (f"{address}:{port}\n")
                                    i+=1
                            if i != 0:
                                send_message(client_socket, msg)
                            else:
                                msg = "Кроме вас тут никого нет"
                                send_message(client_socket, msg)
                        case "/connectUser":
                            client_socket.close()
                            return
                            
                        case _:
                            send_message(client_socket, "Введен неверный параметр")
                except Exception as e:
                    print(f"Ошибка при обработке клиента: {e}")
                    client_socket.close()
                    break
        case 2:
            client_socket.close()

    
while True:
    client_socket, addr = server_socket.accept()
    print(f"{addr} присоединился к серверу")
    clients.append(client_socket.getpeername())
    client_thread = threading.Thread(target=handle_client, args=(client_socket,))
    client_thread.start()
