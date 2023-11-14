# TCPFileSynchronization

## Project Description (EN)

This project is a system designed to synchronize files between two computers using the TCP protocol.

## Functionality

- Allows selecting a synchronization initiator or waiting for an invitation to synchronize
- Ability to view a list of users and send requests for file synchronization
- Automatically detects changes in files/folders for transmission between client and server

## Instructions for Use

### Starting the Server

1. Run the server script on one of the computers.
2. Specify the server's address and port for client connection.

### Starting the Client

1. Run the client script on another computer.
2. Enter the server's address and port to connect the client to the server.
3. Choose to become a synchronization initiator or wait for an invitation to synchronize.

### Client Commands

- `/listUsers`: Outputs a list of available users.
- `/connectUser`: Sends a request for file synchronization to another user.
- Other commands may be added according to your application's functionality.

## Environment Requirements and Dependencies

- Python 3.10, Windows 10, 11

# TCPFileSynchronization

## Описание проекта (RUS)

Этот проект представляет собой систему для синхронизации файлов между двумя компьютерами через TCP протокол.

## Функциональность

- Позволяет выбрать инициатора синхронизации или ожидать приглашения на синхронизацию
- Возможность просмотра списка пользователей и отправки запросов на синхронизацию файлов
- Автоматическое обнаружение изменений в файлах/папках для их передачи между клиентом и сервером

## Инструкции по использованию

### Запуск сервера

1. Запустите серверный скрипт на одном из компьютеров.
2. Укажите адрес сервера и порт для подключения клиента.

### Запуск клиента

1. Запустите клиентский скрипт на другом компьютере.
2. Введите адрес и порт сервера для подключения клиента к серверу.
3. Выберите, стать инициатором синхронизации или ожидать приглашения на синхронизацию.

### Команды клиента

- `/listUsers`: Выводит список доступных пользователей.
- `/connectUser`: Отправляет запрос на синхронизацию файлов другому пользователю.
- Другие команды могут быть добавлены в соответствии с функциональностью вашего приложения.

## Требования к окружению и зависимости

- Python 3.10, Windows 10, 11
