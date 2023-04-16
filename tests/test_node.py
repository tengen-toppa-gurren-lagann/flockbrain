import pytest
from node import Node


@pytest.mark.parametrize("node_id", [1, 2, 3])  # Тестируем для всех трех узлов
def test_node_init(node_id):
    node = Node(node_id)
    assert node is not None
    assert node.id == node_id
    assert node.blockchain is not None
    assert len(node.blockchain) == 0


@pytest.mark.parametrize("node_id", [1, 2, 3])  # Тестируем для всех трех узлов
def test_node_make_block(node_id):
    n = 10
    node = Node(node_id)
    node.blockchain.clear()  # Очистим блокчейн
    # Проверим, что genesis не производится если не надо
    block = node.make_block(make_genesis=False)
    assert block is None
    # Проверим производство genesis-а
    block = node.make_block(make_genesis=True)
    assert block is not None
    assert block.node_id == node.id
    assert block.index == 1
    assert block.prev_hash == "NONE"
    # Проверим производство других блоков
    for i in range(2, n):
        prev_hash = block.hash
        node.blockchain.append(block)
        block = node.make_block(make_genesis=False)
        assert block is not None
        assert block.node_id == node.id
        assert block.index == i
        assert block.prev_hash == prev_hash


@pytest.mark.parametrize("node_id", [1, 2, 3])  # Тестируем для всех трех узлов
def test_node_process_message(node_id):
    n = 50
    node = Node(node_id)
    node.blockchain.clear()  # Очистим блокчейн
    # Проверим обработку сообщения для genesis
    block = node.make_block(make_genesis=True)
    json_str = block.get_json()
    assert node.process_message(json_str)
    assert not node.process_message(json_str)  # Повторно один и тот же блок не должен добавляться в блокчейн
    # Проверим обработку сообщения для других блоков
    for i in range(1, n):
        block = node.make_block(make_genesis=False)
        json_str = block.get_json()
        assert node.process_message(json_str)
        assert not node.process_message(json_str)  # Повторно один и тот же блок не должен добавляться в блокчейн
        block.index -= 1  # Сымитируем более старый блок, чем последний в блокчейне
        json_str = block.get_json()
        assert not node.process_message(json_str)  # Устаревший блок не должен добавляться в блокчейн
    assert len(node.blockchain) == n  # Все правильные блоки должны были добавиться в блокчейн
