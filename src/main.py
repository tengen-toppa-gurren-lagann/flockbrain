from bottle import Bottle, run, request
import threading
import grequests
import argparse
from node import Node
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
    # Разбираем параметры командной строки
    parser = argparse.ArgumentParser()
    parser.add_argument('-id', type=int, choices=[1, 2, 3], help='Node ID')
    parser.add_argument('-f', action='store_true', help='Generate first block (genesis)')
    parser.add_argument('-node', type=str, help='Node address:port')
    parser.add_argument('-node2', type=str, help='Node2 address:port')
    parser.add_argument('-node3', type=str, help='Node3 address:port')
    args = parser.parse_args()

    node_id = args.id
    address: str = args.node
    address2: str = args.node2
    address3: str = args.node3
    genesis: bool = args.f

    # Создаем узел
    node = Node(node_id)

    # Запускаем формирование блокчейна
    start_blockchain(node, address, address2, address3, genesis)
