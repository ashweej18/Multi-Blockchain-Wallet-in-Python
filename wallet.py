# Import dependencies
import os
import subprocess
import json
from constants import BTC, ETH,BTCTEST
from dotenv import load_dotenv
from bit import wif_to_key
from bit import PrivateKeyTestnet
from eth_account import Account
from web3 import Web3
from web3.middleware import geth_poa_middleware
from bit.network import NetworkAPI

import constants

# Load and set environment variables
load_dotenv()
mnemonic =os.getenv("MNEMONIC")
number_derived =3

# Import constants.py and necessary functions from bit and web3

#print(constants.BTC)
#print(constants.BTCTEST)
#print(constants.ETH)
 
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
 
# Create a function called `derive_wallets`
def derive_wallets(mnemonic,coin_type,number_derived):
    command = './derive -g --mnemonic='+'"'+mnemonic+'"'+' --cols=address,index,path,privkey,pubkey --numderive='+str(number_derived)+' --coin='+'"'+ coin_type +'"'+ ' --format=json'
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output, err = p.communicate()
    p_status = p.wait()
    return json.loads(output)

# Create a dictionary object called coins to store the output from `derive_wallets`.

eth_coins = derive_wallets(mnemonic,constants.ETH,number_derived)
btctest_coins=derive_wallets(mnemonic,constants.BTCTEST,number_derived)
btc_coins=derive_wallets(mnemonic,constants.BTC,number_derived)

coins={ETH:eth_coins, BTCTEST:btctest_coins, BTC:btc_coins}


#print(coins)

print("btc coin address\n")
print(coins[BTCTEST][0]['privkey'])

#printing the address, pvtkeys for coins
for keys,values in coins.items():
    print("\n",keys)
    print('Address','|','Path','|','Index','|','Private Key')
    for values in values:
        print(values['address'],'|',values['path'],'|',values['index'],'|',values['privkey'])
    

# Create a function called `priv_key_to_account` that converts privkey strings to account objects.
def priv_key_to_account(coin_type,priv_key):
    if coin_type==ETH:
        return Account.from_key(priv_key)
    if coin_type==BTCTEST:
        return PrivateKeyTestnet(priv_key)

# Create a function called `create_tx` that creates an unsigned transaction appropriate metadata.
def create_tx(coin_type,account, recipient, amount):
    if coin_type==ETH:
        gasEstimate = w3.eth.estimateGas(
        {"from": account.address, "to": recipient.address, "value": amount})
        return {
            "from": account.address,
            "to": recipient.address,
            "value": amount,
            "gasPrice": w3.eth.gasPrice,
            "gas": gasEstimate,
            "nonce": w3.eth.getTransactionCount(account.address)
            }
    if coin_type==BTCTEST:
        return PrivateKeyTestnet.prepare_transaction(account.address, [(recipient.address, amount, BTC)]) 
    

# Create a function called `send_tx` that calls `create_tx`, signs and sends the transaction.
def send_tx(coin_type, account, recipient, amount):
    if coin_type ==ETH:
        tx = create_tx(coin_type,account, recipient, amount)
        signed_tx = account.sign_transaction(tx)
        result = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        print(result.hex())
        return result.hex()
    
    if coin_type == BTCTEST:
        raw_tx = create_tx(coin_type, account, recipient, amount)
        signed_tx = account.sign_transaction(raw_tx)
        result = NetworkAPI.broadcast_tx_testnet(signed_tx)
        print(signed_tx)
        return result

#Bitcoin Test Net Transaction
print("\n")

print (create_tx(BTCTEST, priv_key_to_account(BTCTEST, coins[BTCTEST][0]['privkey']), priv_key_to_account(BTCTEST, coins[BTCTEST][1]['privkey']), 0.000001))

print("\n")

print(send_tx(BTCTEST, priv_key_to_account(BTCTEST,coins[BTCTEST][0]['privkey']), priv_key_to_account(BTCTEST,coins[BTCTEST][1]['privkey']), 0.000001))



# ETH Transaction

print("\n")
#print (create_tx(ETH, priv_key_to_account(ETH, coins[ETH][0]['privkey']), priv_key_to_account(ETH, coins[ETH][1]['privkey']), 0.000001))
print(send_tx(ETH, priv_key_to_account(ETH,coins[ETH][0]['privkey']), priv_key_to_account(ETH,coins[ETH][1]['privkey']), 1))