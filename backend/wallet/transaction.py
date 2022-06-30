from ast import ExceptHandler
import uuid
import time
from venv import create
from backend.wallet.wallet import Wallet
from backend.config import MINING_REWARD, MINING_REWARD_INPUT

class Transaction:
    '''
    Document of an exchange in currency from a sender to one or more recipients
    '''
    def __init__(self, senderWallet = None, recipient=None, amount=None, id=None, input=None, output=None):
        self.id = id or str(uuid.uuid4())[0:8]      
        self.output = output or self.create_output(senderWallet, recipient, amount)
        self.input = input or self.create_input(senderWallet, self.output)
    
    def create_output(self, senderWallet, recipient, amount):
        '''
        Structure the output data for the transaction
        '''
        if amount>senderWallet.balance:
            raise Exception('Amount exceeds balance')
        output = {}
        output[recipient] = amount
        output[senderWallet.address] = senderWallet.balance - amount

        return output

    def create_input(self, senderWallet, output):
        '''
        Structure the input data for the transaction
        Sign the transaction and include the sender's public key and address
        '''
        return {
            'timestamp': time.time_ns(),
            'amount': senderWallet.balance,
            'address': senderWallet.address,
            'public_key': senderWallet.publicKey,
            'signature': senderWallet.sign(output)
        }
    
    def update(self, senderWallet, recipient, amount):
        '''
        Update the transaction with an existing or new recipient
        '''
        if amount > self.output[senderWallet.address]:
            raise Exception('Amount exceeds balance')
        
        if recipient in self.output:
            self.output[recipient] = self.output[recipient] + amount
        else:
            self.output[recipient] = amount
        
        self.output[senderWallet.address] = self.output[senderWallet.address] - amount

        self.input = self.create_input(senderWallet, self.output)

    @staticmethod
    def is_valid_transaction(transaction):
        '''
        Validate a transaction
        Raise an exception for invalid transactions
        '''

        if transaction.input == MINING_REWARD_INPUT:
            if list(transaction.output.values()) != [MINING_REWARD]:
                raise Exception('Invalid mining reward')
            return

        outputTotal = sum(transaction.output.values())
        if transaction.input['amount'] != outputTotal:
            raise Exception('Invalid transaction output values')
        
        if not Wallet.verify(
            transaction.input['public_key'],
            transaction.output,
            transaction.input['signature'] 
        ) :
            raise Exception('Invalid Signature')

    def to_json(self):
        '''
        Serilaize the transaction
        '''
        return self.__dict__
    
    @staticmethod
    def from_json(transactionJson):
        '''
        Deserialize a transaction's json representation back into a Transaction instance
        '''
        return Transaction(**transactionJson)

    @staticmethod
    def reward_transaction(miner_wallet):
        '''
        Generate a reward transaction that award the miner
        '''
        output = {}
        output[miner_wallet.address] = MINING_REWARD
        return Transaction(input = MINING_REWARD_INPUT, output=output)

def main():
    transaction = Transaction(Wallet(), 'recipient', 15)
    print(f'transaction.__dict__ : {transaction.__dict__}')

    transactionJson = transaction.to_json()

    restoreTransaction = Transaction.from_json(transactionJson)
    print(f'restore_transaction.__dict__ : {restoreTransaction.__dict__}')

if __name__ == '__main__':
    main()

