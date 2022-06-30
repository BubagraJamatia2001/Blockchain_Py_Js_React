from backend.blockchain.block import Block, GENESIS_DATA
import time
from backend.config import MINE_RATE, SECONDS
from backend.util.hex_to_binary import hex_to_binary
import pytest

def test_mine_block():
    lastBlock = Block.genesis()
    data = 'test-data'
    block = Block.mine_block(lastBlock, data)

    assert isinstance(block, Block)
    assert block.data == data
    assert block.lastHash == lastBlock.hash
    assert hex_to_binary(block.hash)[0:block.difficulty] == '0'*block.difficulty

def test_genesis():
    genesis = Block.genesis()
    assert isinstance(genesis, Block)

    # assert genesis.timestamp == GENESIS_DATA['timestamp']
    # assert genesis.lastHash == GENESIS_DATA['lastHash'] 
    # assert genesis.hash == GENESIS_DATA['hash']
    # assert genesis.data == GENESIS_DATA['data']
    for key, value in GENESIS_DATA.items():
        getattr(genesis, key) == value

def test_quickly_mined_block():
    lastBlock = Block.mine_block(Block.genesis(), 'foo')
    minedBlock = Block.mine_block(lastBlock, 'bar')
    assert minedBlock.difficulty == lastBlock.difficulty + 1

def test_slowly_mined_block():
    lastBlock = Block.mine_block(Block.genesis(), 'foo')
    time.sleep(MINE_RATE / SECONDS)
    minedBlock = Block.mine_block(lastBlock, 'bar')
    assert minedBlock.difficulty == lastBlock.difficulty - 1


def test_mined_block_difficulty_limits_at_1():
    lastBlock = Block(time.time_ns(), 'test_last_hash', 'test_hash', 'test_data', 1 , 0)
    time.sleep(MINE_RATE / SECONDS)
    minedBlock = Block.mine_block(lastBlock, 'bar')
    assert minedBlock.difficulty == 1

@pytest.fixture
def lastBlock():
    return Block.genesis()

@pytest.fixture
def block(lastBlock):
    return Block.mine_block(lastBlock, 'test_data')

def test_is_valid_block(lastBlock, block):
    Block.is_valid_block(lastBlock, block)

def test_is_valid_block_bad_lastHash(lastBlock, block):
    block.lastHash = 'evilLastHash'
    with pytest.raises(Exception, match = '1. The Block lastHash must be correct.'):
        Block.is_valid_block(lastBlock, block)

def test_is_valid_block_bad_proof_of_work(lastBlock, block):
    block.hash = 'fff'
    with pytest.raises(Exception, match = '2. The proof of work requirement is not met.'):
        Block.is_valid_block(lastBlock, block)

def test_is_valid_block_jumped_difficulty(lastBlock, block):
    jumpedDifficulty = 10
    block.difficulty = jumpedDifficulty
    block.hash = f'{"0" * jumpedDifficulty}111abc'
    with pytest.raises(Exception, match = '3. The block difficulty must only be adjusted by 1.'):
        Block.is_valid_block(lastBlock, block)

def test_is_valid_block_bad_block_hash(lastBlock, block):
    block.hash = '0000000000000000bbbbbaaab'
    with pytest.raises(Exception, match = '4. The block hash must be correct.'):
        Block.is_valid_block(lastBlock, block)
