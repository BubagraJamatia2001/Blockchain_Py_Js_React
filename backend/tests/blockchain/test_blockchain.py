import pytest
from backend.blockchain.blockchain import Blockchain
from backend.blockchain.block import GENESIS_DATA
from backend.wallet.transaction import Transaction
from backend.wallet.wallet import Wallet


def test_blockchain_instance():
    blockchain = Blockchain()
    assert blockchain.chain[0].hash == GENESIS_DATA['hash']


def test_add_block():
    blockchain = Blockchain()
    data = 'test-data'
    blockchain.add_block(data)

    assert blockchain.chain[-1].data == data

@pytest.fixture
def blockchainThreeBlocks():
    blockchain = Blockchain()
    for i in range(3):
        blockchain.add_block([Transaction(Wallet(), 'recipient', i).to_json()])
    return blockchain

def test_is_valid_chain(blockchainThreeBlocks):
    Blockchain.is_valid_chain(blockchainThreeBlocks.chain)

def test_is_valid_chain_bad_genesis(blockchainThreeBlocks):
    blockchainThreeBlocks.chain[0].hash = 'evil_hash'
    with pytest.raises(Exception, match='The genesis block must be valid'):
        Blockchain.is_valid_chain(blockchainThreeBlocks.chain)

def test_replace_chain(blockchainThreeBlocks):
    blockchain = Blockchain()
    blockchain.replace_chain(blockchainThreeBlocks.chain)
    assert blockchain.chain == blockchainThreeBlocks.chain

def test_replace_chain_not_longer(blockchainThreeBlocks):
    blockchain = Blockchain()
    with pytest.raises(Exception, match='Cannot Replace. The incomming chain must be longer.'):
        blockchainThreeBlocks.replace_chain(blockchain.chain)

def test_replace_chain_bad_chain(blockchainThreeBlocks):
    blockchain = Blockchain()
    blockchainThreeBlocks.chain[1].hash = 'evil hash'
    with pytest.raises(Exception, match='The incomming chain is invalid'):
        blockchain.replace_chain(blockchainThreeBlocks.chain)

def test_valid_transaction_chain(blockchainThreeBlocks):
    Blockchain.is_valid_transaction_chain(blockchainThreeBlocks.chain)

def test_valid_transaction_chain_duplicate_transactions(blockchainThreeBlocks):
    transaction = Transaction(Wallet(), 'recipient', 1).to_json()

    blockchainThreeBlocks.add_block([transaction, transaction])

    with pytest.raises(Exception, match='is not unique.'):
        Blockchain.is_valid_transaction_chain(blockchainThreeBlocks.chain)

def test_valid_transaction_chain_multiple_rewards(blockchainThreeBlocks):
    reward1 = Transaction.reward_transaction(Wallet()).to_json()
    reward2 = Transaction.reward_transaction(Wallet()).to_json()
    blockchainThreeBlocks.add_block([reward1, reward2])

    with pytest.raises(Exception, match='one mining reward per block.'):
        Blockchain.is_valid_transaction_chain(blockchainThreeBlocks.chain)

def test_valid_transaction_chain_bad_transaction(blockchainThreeBlocks):
    badTransaction = Transaction(Wallet(), 'recipient', 1)
    badTransaction.input['signature'] = Wallet().sign(badTransaction.output)
    blockchainThreeBlocks.add_block([badTransaction.to_json()])
    
    with pytest.raises(Exception):
        Blockchain.is_valid_transaction_chain(blockchainThreeBlocks.chain)

def test_is_valid_transaction_chain_bad_historic_balance(blockchainThreeBlocks):
    wallet = Wallet()
    badTransaction  = Transaction(wallet, 'recipient', 20)
    badTransaction.output[wallet.address] = 9000
    badTransaction.input['amount'] = 9020
    badTransaction.input['signature'] = Wallet().sign(badTransaction.output)

    blockchainThreeBlocks.add_block([badTransaction.to_json()])

    with pytest.raises(Exception, match = "has an invalid input amount"):
        Blockchain.is_valid_transaction_chain(blockchainThreeBlocks.chain)
