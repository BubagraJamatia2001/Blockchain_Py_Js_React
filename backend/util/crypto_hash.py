import hashlib
import json


def crypto_hash(*args):
    """
    Return a SHA-256 hash of the given arguments.
    """
    stringifiedArgs = sorted(map(lambda data: json.dumps(data), args))
    # print(f'args : {stringifiedArgs}')

    joinedData = ''.join(stringifiedArgs)
    # print(f'joinedData: {joinedData}')

    return hashlib.sha256(joinedData.encode('utf-8')).hexdigest()


def main():
    print(f" CryptoHash('one', 2, [3]'): {crypto_hash('one', 2, [3])}")
    print(f" CryptoHash( 2, 'one', [3]'): {crypto_hash(2, 'one', [3])}")
    

if __name__== '__main__' :
    main()