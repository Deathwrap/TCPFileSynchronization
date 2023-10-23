import socket
import threading
import pickle

# Создаем сокет сервера
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', 8080))
server_socket.listen(5)

print(f"Сервер запущен с адресом {server_socket.getsockname()}")

# Список клиентов
clients = []

# Функция для обработки сообщений от клиентов
def handle_client(client_socket):
    client_socket.send("Вы успешно подключились к серверу\n".encode())
    client_socket.send("Наберите команду (Список команд /help)".encode())
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                clients.remove(client_socket)
                client_socket.close()
                break
            match(data.decode()):
                case "/help":
                    msg = "/listUsers - выводит список пользователей\n/connectUser - отправить запрос на синхронизацию файлов"
                    client_socket.send(msg.encode())
                case "/listUsers":
                    msg = ""
                    for client in clients:
                        if client != client_socket:
                            address, port = client.getpeername()
                            msg += (f"{address}:{port}\n")
                    client_socket.send(msg.encode())
                case "/connectUser":
                    msg = "Введите адрес клиента: "
                    client_socket.send(msg.encode())
                    desired_address = client_socket.recv(1024).decode()
                    
                    msg = "Введите порт клиента: "
                    client_socket.send(msg.encode())
                    desired_port = int(client_socket.recv(1024).decode())
                    
                    desired_client = None
                    
                    for client in clients:
                        if client != client_socket:
                            address, port = client.getpeername()
                            if address == desired_address and port == desired_port:
                                desired_client = client
                                break
                    if desired_client:
                        desired_client.send("/sendSyncRequest".encode())
                        client_socket.send("Пользователю отправлен запрос".encode())
                        desired_client_response = desired_client.recv(1024)
                        if (desired_client_response.decode() == "y"):
                            desired_client.send("Синхронизация начата".encode())
                            client_socket.send("Синхронизация начата".encode())
                    else:
                        client_socket.send("Такой пользователь не найден".encode())

            for client in clients:
                if client != client_socket:
                    client.send(data)
        except Exception as e:
            print(f"Ошибка при обработке клиента: {e}")
            clients.remove(client_socket)
            client_socket.close()
            break

# Главный цикл сервера
while True:
    client_socket, addr = server_socket.accept()
    print(f"{addr} присоединился к серверу")
    clients.append(client_socket)
    client_thread = threading.Thread(target=handle_client, args=(client_socket,))
    client_thread.start()
