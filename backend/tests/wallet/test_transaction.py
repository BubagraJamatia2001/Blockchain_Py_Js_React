import pytest

from backend.wallet.transaction import Transaction
from backend.wallet.wallet import Wallet
from backend.config import MINING_REWARD, MINING_REWARD_INPUT


def test_transaction():
    senderWallet = Wallet()
    recipient = 'recipient'
    amount = 50
    transaction = Transaction(senderWallet, recipient, amount)

    assert transaction.output[recipient] == amount
    assert transaction.output[senderWallet.address] == senderWallet.balance - amount
    assert 'timestamp' in transaction.input
    assert transaction.input['amount'] == senderWallet.balance
    assert transaction.input['public_key'] == senderWallet.publicKey

    assert Wallet.verify(transaction.input['public_key'], transaction.output, transaction.input['signature'])

def test_transaction_exceeds_balance():
    
    with pytest.raises(Exception, match = 'Amount exceeds balance'):
        Transaction(Wallet(), 'recipient', 9001)

def test_transaction_update_exceeds_balance():
    senderWallet = Wallet()
    transaction = Transaction(senderWallet, 'recipient', 50)
    with pytest.raises(Exception, match='Amount exceeds balance'):
        transaction.update(senderWallet, 'new_recipient', 9001)

def test_transaction_update():
    senderWallet = Wallet()
    firstRecipient = 'first_recipient'
    firstAmount = 50

    transaction = Transaction(senderWallet, firstRecipient, firstAmount)

    nextRecipient = 'nextRecipient'
    nextAmount = 75

    transaction.update(senderWallet, nextRecipient, nextAmount)

    assert transaction.output[nextRecipient] == nextAmount
    assert transaction.output[senderWallet.address] == senderWallet.balance - firstAmount - nextAmount
    assert Wallet.verify(
        transaction.input['public_key'],
        transaction.output,
        transaction.input['signature']
    )

    toFirstAgainAmount = 25
    transaction.update(senderWallet, firstRecipient, toFirstAgainAmount)
    assert transaction.output[nextRecipient] == firstAmount + toFirstAgainAmount
    assert transaction.output[senderWallet.address] == senderWallet.balance - firstAmount - nextAmount - toFirstAgainAmount
    assert Wallet.verify(
        transaction.input['public_key'],
        transaction.output,
        transaction.input['signature']
    )

def test_valid_transaction():
    Transaction.is_valid_transaction(Transaction(Wallet(), 'recipient', 50))

def test_valid_transaction_with_invalid_outputs():
    senderWallet = Wallet()
    transaction = Transaction(Wallet(), 'recipient', 50)
    transaction.output[senderWallet.address] = 9001

    with pytest.raises(Exception, match='Invalid transaction output values'):
        Transaction.is_valid_transaction(transaction)

def test_valid_transaction_with_invalid_signature():
    transaction = Transaction(Wallet(), 'recipient', 50)
    transaction.input['signature'] = Wallet().sign(transaction.output)

    with pytest.raises(Exception, match = 'Invalid Signature'):
        Transaction.is_valid_transaction(transaction)

def test_reward_transaction():
    miner_wallet = Wallet()
    transaction = Transaction.reward_transaction(miner_wallet)

    assert transaction.input == MINING_REWARD_INPUT
    assert transaction.output[miner_wallet.address] == MINING_REWARD

def test_valid_reward_transaction():
    reward_transaction = Transaction.reward_transaction(Wallet())
    Transaction.is_valid_transaction(reward_transaction)

def test_invalid_reward_transaction_extra_recipient():
    reward_transaction = Transaction.reward_transaction(Wallet())
    reward_transaction.output['extra_recipient'] = 60

    with pytest.raises(Exception, match = "Invalid mining reward"):
        Transaction.is_valid_transaction(reward_transaction)

def test_invalid_reward_transaction_extra_recipient():
    minerWallet = Wallet()
    reward_transaction = Transaction.reward_transaction(minerWallet)
    reward_transaction.output[minerWallet.address] = 9001

    with pytest.raises(Exception, match = "Invalid mining reward"):
        Transaction.is_valid_transaction(reward_transaction)