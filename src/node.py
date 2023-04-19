import json
import logging

from block import Block

DEBUG = True


class Node:
    blockchain = []

    def __init__(self, node_id):
        self.id = node_id
        logging.basicConfig(filename=f"node{self.id}_log.txt", level=logging.INFO)

    def make_block(self, make_genesis):  # Произвести блок
        new_block = None
        if len(self.blockchain) > 0:  # Блокчейн не пустой
            last_block = self.blockchain[-1]  # Последний блок в блокчейне
            new_block = Block(last_block.index + 1, last_block.hash, self.id)  # Производим новый блок
        elif make_genesis:  # Блокчейн пуст, но надо произвести первый блок
            new_block = Block(1, 'NONE', self.id)
        return new_block

    def process_message(self, received_json):  # Обработчик входящих сообщений. Возврат: True - блок добавлен в блокчейн
        received_block_info = json.loads(received_json)
        received_block_index = received_block_info['index']
        if len(self.blockchain) > 0:  # Блокчейн не пустой
            last_index = self.blockchain[-1].index  # Индекс последнего блока в блокчейне
        else:
            last_index = 0  # Приняли первый блок (genesis)
        if received_block_index > last_index:  # Это новый блок или genesis -> добавляем блок в блокчейн
            prev_hash = received_block_info['prev_hash']
            node_id = received_block_info['node']
            data = received_block_info['data']
            cur_hash = received_block_info['hash']
            nonce = received_block_info['nonce']
            new_block = Block(received_block_index, prev_hash, node_id, data, cur_hash, nonce)
            self.blockchain.append(new_block)
            if new_block.node_id != self.id or DEBUG:  # Выводим только чужие блоки
                print(self.to_string(new_block))
                logging.info(f"{self.to_string(new_block)}")
            return True
        return False

    def to_string(self, block):
        return f'Node {self.id} - new block from node {block.node_id}: index={block.index}, ' \
               f'prev_hash = {block.prev_hash}, hash={block.hash}, data = {block.data}, nonce = {block.nonce}'
