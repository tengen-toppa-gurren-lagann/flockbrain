import pytest
import json
from src.block import Block


pytestmark = pytest.mark.parametrize("node_id", [1, 2, 3])  # Все тесты в модуле проводим для всех трех узлов


def test_block_init(node_id):
    prev_hash = "NONE"
    for i in range(1, 10):
        # Проверим правильность создания блока
        block = Block(i, prev_hash, node_id)
        assert block is not None
        assert block.index == i
        assert block.prev_hash == prev_hash
        assert block.node_id == node_id
        assert len(block.data) == 256
        assert all(char.isalnum() for char in block.data)
        assert len(block.hash) == 64
        assert block.hash[-4:] == "0000"
        # Проверим правильность создания копии блока
        block2 = Block(block.index, block.prev_hash, block.node_id, block.data, block.hash, block.nonce)
        assert block2.index == block.index
        assert block2.prev_hash == block.prev_hash
        assert block2.node_id == block.node_id
        assert block2.data == block.data
        assert block2.hash == block.hash
        assert block2.nonce == block.nonce
        prev_hash = block.hash


def test_block_get_json(node_id):  # Тестируем для всех трех узлов
    prev_hash = "NONE"
    for i in range(1, 10):
        block = Block(i, prev_hash, node_id)
        json_from_block = block.get_json()
        assert type(json_from_block) == str
        object_from_json = json.loads(json_from_block)
        assert block.node_id == object_from_json['node']
        assert block.index == object_from_json['index']
        assert block.prev_hash == object_from_json['prev_hash']
        assert block.hash == object_from_json['hash']
        assert block.data == object_from_json['data']
        assert block.nonce == object_from_json['nonce']
        prev_hash = block.hash
