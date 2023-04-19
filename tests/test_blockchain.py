import pytest
import threading
from time import sleep
from node import Node
from main import start_blockchain


@pytest.mark.parametrize("node_id, node_address, node2_address, node3_address, make_genesis",
                         [(1, "127.0.0.1:10000", "127.0.0.1:10001", "127.0.0.1:10002", True)])
def test_blockchain_init(node_id, node_address, node2_address, node3_address, make_genesis):
    node = Node(node_id)
    assert node is not None
    thread = threading.Thread(target=start_blockchain,
                              args=(node, node_address, node2_address, node3_address, make_genesis), daemon=False)
    thread.start()
    i = 0
    while len(node.blockchain) == 0 and i < 50:
        sleep(0.1)
        i += 1
    assert len(node.blockchain) != 0
    first_block = node.blockchain[0]
    assert first_block.index == 1
    assert first_block.prev_hash == 'NONE'
    assert first_block.node_id == node.id


@pytest.mark.parametrize("node_id, node_address, node2_address, node3_address, make_genesis",
                         [(1, "127.0.0.1:10000", "127.0.0.1:10001", "127.0.0.1:10002", True)])
def test_blockchain(node_id, node_address, node2_address, node3_address, make_genesis):
    node1 = Node(1)
    node2 = Node(2)
    node3 = Node(3)
    thread1 = threading.Thread(target=start_blockchain, args=(node1, node_address, node2_address, node3_address, False),
                               daemon=False)
    thread2 = threading.Thread(target=start_blockchain, args=(node2, node2_address, node_address, node3_address, False),
                               daemon=False)
    thread3 = threading.Thread(target=start_blockchain, args=(node3, node3_address, node_address, node2_address, True),
                               daemon=False)
    thread1.start()
    thread2.start()
    thread3.start()

    n = 30
    while len(node1.blockchain) < n or len(node2.blockchain) < n or len(node3.blockchain) < n:
        sleep(0.1)

    for i in range(n):
        assert node1.blockchain[i] == node2.blockchain[i] == node3.blockchain[i]
