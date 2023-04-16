import random
import string
from hashlib import sha256
import json


class Block:
    def __init__(self, index, prev_hash, node_id):
        self.index = index
        self.prev_hash = prev_hash
        self.nonce = 0
        self.node_id = node_id  # Узел, который произвел этот блок

        # Инициализируем поле данных блока - строку заданной длины из случайных символов (букв и цифр)
        chars = string.ascii_lowercase + string.digits
        self.data = ''.join(random.choice(chars) for _ in range(256))

        # Вычисляем хеш (sha256) - он должен заканчиваться на 0000, для достижения этого может изменяться nonce
        while True:
            cur_str = str(self.index) + self.prev_hash + self.data + str(self.nonce)
            cur_hash = sha256(cur_str.encode('utf-8')).hexdigest()
            if cur_hash[-4:] == "0000":  # Достигли нужного значения хеша
                self.hash = cur_hash
                break
            # Каждый узел изменяет значение nonce по-разному:
            if node_id == 1:
                self.nonce += 1
            elif node_id == 2:
                self.nonce += random.randint(2, 10)
            else:
                self.nonce += random.randint(11, 100)

    def get_json(self) -> str:  # Возвращает JSON-строку с полями блока
        return json.dumps(
            {
                'node': self.node_id,
                'index': self.index,
                'prev_hash': self.prev_hash,
                'hash': self.hash,
                'data': self.data,
                'nonce': self.nonce
            }
        )

    @staticmethod
    def get_block(json_str):  # Возвращает блок с полями, инициализированными в соответствии с JSON-строкой
        block = Block(1, '1', 1)
        block_info = json.loads(json_str)
        block.node_id = block_info['node']
        block.index = block_info['index']
        block.prev_hash = block_info['prev_hash']
        block.hash = block_info['hash']
        block.data = block_info['data']
        block.nonce = block_info['nonce']
        return block
