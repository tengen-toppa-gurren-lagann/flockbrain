import random
import string
from hashlib import sha256
import json


class Block:
    def __init__(self, index, prev_hash, node_id, data=None, cur_hash=None, nonce=None):
        self.index = index
        self.prev_hash = prev_hash
        self.nonce = 0
        self.node_id = node_id  # Узел, который произвел этот блок
        if data is not None and cur_hash is not None and nonce is not None:
            self.data = data
            self.hash = cur_hash
            self.nonce = nonce
            return

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
                self.nonce += random.randint(1, 10)
            elif node_id == 2:
                self.nonce += random.randint(11, 20)
            else:
                self.nonce += random.randint(21, 30)

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

    def __eq__(self, other):
        if not isinstance(other, Block):
            return False
        return self.index == other.index and self.prev_hash == other.prev_hash and self.node_id == other.node_id \
            and self.data == other.data and self.hash == other.hash and self.nonce == other.nonce
