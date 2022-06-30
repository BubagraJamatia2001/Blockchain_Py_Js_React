from audioop import add
import uuid
import json

from backend.config import STARTING_BALANCE
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import (encode_dss_signature, decode_dss_signature)
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature


class Wallet:
    '''
    An individual wallet for a miner
    Keeps track of the miner's balance
    Allows a miner to authorize transactions
    '''
    def __init__(self, blockchain = None):
        self.blockchain = blockchain
        self.address = str(uuid.uuid4())[0:8]
        self.privateKey = ec.generate_private_key(
            ec.SECP256K1(), 
            default_backend()
            )
        self.publicKey = self.privateKey.public_key()
        self.serialize_public_key()

    @property
    def balance(self):
        return Wallet.calculate_balance(self.blockchain, self.address)

    def sign(self, data):
        '''
        Generate a signature based on the data using local private key
        '''
        return decode_dss_signature(
            self.privateKey.sign(
                json.dumps(data).encode('utf-8'), 
                ec.ECDSA(hashes.SHA256()
            )))

    def serialize_public_key(self):
        '''
        Reset the public key to its serialized version.
        '''
        self.publicKey = self.publicKey.public_bytes(
            encoding = serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode('utf-8')
 

    @staticmethod
    def verify(publicKey, data, signature):
        '''
        Verify a signature based on the original public key and data
        '''
        deserializedPublicKey = serialization.load_pem_public_key(
            publicKey.encode('utf-8'),
            default_backend()
        
        )
        (r, s) = signature

        try:
            deserializedPublicKey.verify(
                encode_dss_signature(r, s), 
                json.dumps(data).encode('utf-8'),
                ec.ECDSA(hashes.SHA256())
            )
            return True
        except InvalidSignature:
            return False

    @staticmethod
    def calculate_balance(blockchain, address):
        '''
        Calculate the balance of the given address considering the transaction data wihtin the blockchain

        The balance is found by adding the output values that belong to the address since the most recent transaction by that address
        '''

        balance = STARTING_BALANCE

        if not blockchain:
            return balance

        for block in blockchain.chain:
            for transaction in block.data:
                if transaction['input']['address'] == address:
                    # Anytime the address conducts a new transaction it resets its balance
                    balance = transaction['output'][address]
                elif address in transaction['output']:
                    balance += transaction['output'][address]

        return balance


def main():
    wallet = Wallet()
    print(f'wallet: {wallet.__dict__}')

    data = {'foo':'bar'}
    signature = wallet.sign(data)
    print(f'signature: {signature}')

    shouldBeValid = Wallet.verify(wallet.publicKey, data, signature)
    print(f'should_be_valid: {shouldBeValid}')

    shouldBeInvalid = Wallet.verify(Wallet().publicKey, data, signature)
    print(f'should_be_invalid: {shouldBeInvalid}')

if __name__ == '__main__':
    main()
