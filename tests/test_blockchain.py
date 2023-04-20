from time import sleep

import pytest
from src.node import Node
from src.main import Starter


@pytest.mark.parametrize("node_id, node_address, node2_address, node3_address, make_genesis",
                         [(1, "127.0.0.1:10000", "127.0.0.1:10001", "127.0.0.1:10002", True)])
def test_blockchain_init(node_id, node_address, node2_address, node3_address, make_genesis):
    n_blocks = 10

    node = Node(node_id)
    assert node is not None
    starter = Starter(node, node_address, node2_address, node3_address, make_genesis)
    starter.start_blockchain(n_blocks)
    assert len(node.blockchain) != 0
    first_block = node.blockchain[0]
    assert first_block.index == 1
    assert first_block.prev_hash == 'NONE'


@pytest.mark.parametrize("node_id, node2_id, node3_id, node_address, node2_address, node3_address",
                         [(1, 2, 3, "127.0.0.1:10000", "127.0.0.1:10001", "127.0.0.1:10002")])
def test_blockchain(node_id, node2_id, node3_id, node_address, node2_address, node3_address):
    n_blocks = 10

    node1 = Node(node_id)
    node2 = Node(node2_id)
    node3 = Node(node3_id)

    starter1 = Starter(node1, node_address, node2_address, node3_address, False)
    starter2 = Starter(node2, node2_address, node_address, node3_address, False)
    starter3 = Starter(node3, node_address, node3_address, node_address, True)

    starter1.start_message_receiver()
    sleep(0.1)
    starter2.start_message_receiver()
    sleep(0.1)
    starter3.start_blockchain(n_blocks)

    for i in range(0, n_blocks):
        assert starter1.node.blockchain[i] == starter2.node.blockchain[i] == starter3.node.blockchain[i]
