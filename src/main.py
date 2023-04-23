from bottle import Bottle, run, request
import os
import threading
import grequests
from src.node import Node
from time import sleep
from gevent import monkey
monkey.patch_all()


def start_blockchain(current_node, node_address, node2_address, node3_address, make_genesis):
    web_server = Bottle(__name__)  # Создаем веб-сервер для приема сообщений от узлов

    # Обработчик POST-запросов (входящих сообщений)
    @web_server.post("/")
    def message_handler():
        message = request.json
        if current_node.process_message(message):
            return "Message processed"
        return "Message processing error"

    # Определяем хост и порт узла
    node_host = node_address.split(':')[0]
    node_port = node_address.split(':')[1]

    # Запускаем поток с веб-сервером для приема POST-запросов
    thread_web_server = threading.Thread(
        target=lambda: run(app=web_server, host=node_host, port=int(node_port), quiet=True), daemon=False)
    thread_web_server.start()

    def blocks_maker():  # Производитель блоков для блокчейна
        nodes_urls = [f'http://{node_address}/',
                      f'http://{node2_address}/',
                      f'http://{node3_address}/']
        while True:
            new_block = current_node.make_block(make_genesis)  # Производим блок
            if new_block is not None:  # Блок произведён успешно
                # Создаем набор http-запросов - сообщений с информацией о новом блоке для всех узлов
                requests = (grequests.post(url, json=new_block.get_json()) for url in nodes_urls)
                # Отправляем запросы всем узлам (в т.ч. и себе)
                grequests.map(requests)
            sleep(0.1)

    # Запускаем поток с производителем блоков
    thread_blocks_maker = threading.Thread(target=blocks_maker(), daemon=False)
    thread_blocks_maker.start()


if __name__ == '__main__':
    # Разбираем параметры окружения
    if 'ID' in os.environ:
        node_id = int(os.environ['ID'])
    else:
        print("No ID in environment")
        exit(1)
    if 'ADDRESS' in os.environ:
        address = str(os.environ['ADDRESS'])
    else:
        print("No ADDRESS in environment")
        exit(1)
    if 'ADDRESS2' in os.environ:
        address2 = str(os.environ['ADDRESS2'])
    else:
        print("No ADDRESS2 in environment")
        exit(1)
    if 'ADDRESS3' in os.environ:
        address3 = str(os.environ['ADDRESS3'])
    else:
        print("No ADDRESS3 in environment")
        exit(1)
    if 'GENESIS' in os.environ:
        genesis = True if int(os.environ['GENESIS']) == 1 else False
    else:
        print("No GENESIS in environment")
        exit(1)

    # Создаем узел
    node = Node(node_id)

    # Запускаем формирование блокчейна
    start_blockchain(node, address, address2, address3, genesis)
