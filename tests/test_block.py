import pytest
import json
from block import Block


@pytest.mark.parametrize("node_id", [1, 2, 3])  # Тестируем для всех трех узлов
def test_block_init(node_id):
    prev_hash = "NONE"
    for i in range(1, 10):
        block = Block(i, prev_hash, node_id)
        assert block is not None
        assert block.index == i
        assert block.prev_hash == prev_hash
        assert block.node_id == node_id
        assert len(block.data) == 256
        assert all(char.isalnum() for char in block.data)
        assert len(block.hash) == 64
        assert block.hash[-4:] == "0000"
        prev_hash = block.hash


@pytest.mark.parametrize("node_id", [1, 2, 3])
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


@pytest.mark.parametrize("node_id", [1, 2, 3])  # Тестируем для всех трех узлов
def test_block_get_block(node_id):
    prev_hash = "NONE"
    for i in range(1, 10):
        block = Block(i, prev_hash, node_id)
        json_from_block = block.get_json()
        block2 = Block.get_block(json_from_block)
        assert block.node_id == block2.node_id
        assert block.index == block2.index
        assert block.prev_hash == block2.prev_hash
        assert block.hash == block2.hash
        assert block.data == block2.data
        assert block.nonce == block2.nonce
        prev_hash = block.hash
