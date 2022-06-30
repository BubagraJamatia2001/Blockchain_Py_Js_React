from backend.wallet.transaction import Transaction
from backend.wallet.wallet import Wallet
from backend.blockchain.blockchain import Blockchain
from backend.config import STARTING_BALANCE

def test_verify_valid_signature():
    data = {'foo': 'test_data'}
    wallet = Wallet()
    signature = wallet.sign(data)

    assert Wallet.verify(wallet.publicKey, data, signature)

def test_verify_invalid_signature():
    data = {'foo': 'test_data'}
    wallet = Wallet()
    signature = wallet.sign(data)

    assert not Wallet.verify(Wallet().publicKey, data, signature)

def test_calculate_balance():
    blockchain = Blockchain()
    wallet = Wallet()
    assert Wallet.calculate_balance(blockchain, wallet.address) == STARTING_BALANCE
    # transfers and amount
    amount = 50
    transaction = Transaction(wallet, 'recipient', amount)
    blockchain.add_block([transaction.to_json()])

    assert Wallet.calculate_balance(blockchain, wallet.address) == STARTING_BALANCE - amount

    # receives an amount
    receivedAmount1 = 50
    receivedTransaction1 = Transaction(Wallet(), wallet.address, receivedAmount1)

    receivedAmount2 = 30
    receivedTransaction2 = Transaction(Wallet(), wallet.address, receivedAmount2)

    blockchain.add_block([receivedTransaction1.to_json(), receivedTransaction2.to_json()])

    assert Wallet.calculate_balance(blockchain, wallet.address) == \
        STARTING_BALANCE - amount + receivedAmount1 + receivedAmount2



# def test_calculate_balance():

