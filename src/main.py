from bottle import Bottle, run, request
import threading
import grequests
import argparse
from src.node import Node
from time import sleep
from gevent import monkey

monkey.patch_all()


class Starter:
    def __init__(self, current_node, node_address, node2_address, node3_address, make_genesis):
        self.node = current_node
        self.node_address = node_address
        self.node2_address = node2_address
        self.node3_address = node3_address
        self.make_genesis = make_genesis

    def start_blocks_maker(self, n_blocks):  # Запуск производителя блоков для блокчейна (с ограничением кол-ва блоков)
        nodes_urls = [f'http://{self.node_address}/',
                      f'http://{self.node2_address}/',
                      f'http://{self.node3_address}/']
        while len(self.node.blockchain) < n_blocks:
            new_block = self.node.make_block(self.make_genesis)  # Производим блок
            if new_block is not None:  # Блок произведён успешно
                # Создаем набор http-запросов - сообщений с информацией о новом блоке для всех узлов
                requests = (grequests.post(url, json=new_block.get_json()) for url in nodes_urls)
                # Отправляем запросы всем узлам (в т.ч. и себе)
                grequests.map(requests)
            sleep(0.1)

    def start_message_receiver(self):  # Запуск приемника сообщений от узлов
        web_server = Bottle(__name__)  # Создаем веб-сервер

        # Обработчик POST-запросов (входящих сообщений)
        @web_server.post("/")
        def message_handler():
            message = request.json
            if self.node.process_message(message):
                return "Message processed"
            return "Message processing error"

        # Определяем хост и порт узла
        node_host = self.node_address.split(':')[0]
        node_port = self.node_address.split(':')[1]

        # Запускаем поток с веб-сервером для приема POST-запросов
        thread_web_server = threading.Thread(
            target=lambda: run(app=web_server, host=node_host, port=int(node_port), quiet=True), daemon=False)
        thread_web_server.start()

    def start_blockchain(self, n_blocks=50):  # Запуск блокчейна
        self.start_message_receiver()
        self.start_blocks_maker(n_blocks)


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
    starter = Starter(node, address, address2, address3, genesis)
    starter.start_blockchain()
