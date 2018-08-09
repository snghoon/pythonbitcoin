#-*- coding: utf-8 -*-

import hashlib
import secp256k1
import key
import random
import binascii
import requests
import json
from transaction import Transaction

class Wallet:

	def __init__(self, privKey=None):
		
		if privKey == None:
			self._privKey = key.getPrivKeyFromSeed(str(random.randrange(1,100000)+9218912379821897321978231892137)) # object
		else:
			self._privKey = key.getPrivKey(key.changeBase(privKey,16,256))

		self._pubKey = key.getPubKey(self._privKey, raw=False) # object
		self._address = key.getAddress(self._pubKey, raw=False) # bytes

	def getPrivKeyHex(self):
		return self._privKey.serialize()

	def getPubKeyHex(self):
		#return "".join([str(c) for c in self._pubKey.serialize(compressed=False)])
		#return [c for c in self._pubKey.serialize(compressed=False)]
		return binascii.hexlify(self._pubKey.serialize())
		#return self._pubKey.serialize()

	def getAddressHex(self):
		return binascii.hexlify(self._address)

	def getAddressP2PKH(self):
		return key.base58check(self._address, prefix = 0x6F) 

	def getTxs(self):
		return None

	def getUTXOs(self):
		response = requests.get("https://testnet.blockexplorer.com/api/addr/%s/utxo"%(self.getAddressP2PKH()))
		
		rawUTXOs = response.json()

		UTXOs = []

		for rawUTXO in rawUTXOs:
			UTXO = {'txid':rawUTXO['txid'], 'index':rawUTXO['vout'], 'amount':rawUTXO['satoshis'], 'scriptPubKey':rawUTXO['scriptPubKey']}
			UTXOs.append(UTXO)

		return UTXOs

	def toBeUsedTxs(self, amount):
		
		UTXOs = self.getUTXOs()

		count =0
		i=0

		for UTXO in UTXOs:
			count += UTXO['amount']
			i+=1
			if count >= amount:
				break
		else:
			return None

		return UTXOs[:i]

	def send(self, toAddr, amount):

		UTXOs = self.toBeUsedTxs(amount)

		if UTXOs == None:
			return None

		_tx = Transaction()

		_tx.createTx(UTXOs, toAddr, amount)

		_privKeys = [self._privKey for i in range(len(UTXOs))]

		_tx.signTx(_privKeys)

		payload = json.dumps({"rawtx":binascii.hexlify(_tx._rawTx)})

		response = requests.post("https://testnet.blockexplorer.com/api/tx/send", data=payload)

		print binascii.hexlify(_tx._rawTx), response

		return binascii.hexlify(_tx._rawTx)
		#return response.json()['txid']

