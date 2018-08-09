#-*- coding: utf-8 -*-

import key, binascii

class Transaction:

	def __init__(self, rawTx = None): # hex

		if rawTx != None:
			self._rawTx  = key.changeBase(rawTx, 16, 256)

			self._tx = txDeserialize(self._rawTx)

	def getTxInfo(self):
		return self._tx

	def setTxInfo(self, tx):
		self._tx = tx
		

	def createTx(self, UTXOs, toAddr, amount):

		self._tx = {}
		self._tx["version"] = 1
		self._tx["numIn"] = len(UTXOs)
		self._tx["txIns"] = []

		for UTXO in UTXOs:
			tempTxIn = {}
			tempTxIn["prevOutTxid"] = UTXO["txid"]
			tempTxIn["prevOutIndex"] = UTXO["index"]
			tempTxIn["prevOutScriptPubKey"] = UTXO["scriptPubKey"]
			tempTxIn["lenScript"]=0
			tempTxIn["scriptSig"]= None
			tempTxIn["sequence"] = 0xffffffff
			self._tx["txIns"].append(tempTxIn)

		self._tx["numOut"] = 1
		self._tx["txOuts"] = []

		for i in range(self._tx["numOut"]):
			tempTxOut = {}
			tempTxOut["value"] = amount
			pubKeyHash = key.changeBase(toAddr, 58, 256)[1:-4]
			tempTxOut["scriptPubKey"]= setScriptPubKey(pubKeyHash)
			tempTxOut['lenScript']= len(key.changeBase(tempTxOut['scriptPubKey'], 16, 256))
			self._tx["txOuts"].append(tempTxOut)

		self._tx["lockTime"]=0
		self._tx["sigHashCode"] = 1

	def signTx(self, privKeys):
		for i in range(len(privKeys)):
			signedMessage = key.signMessage(getScriptSigMessage(self._tx, i), privKeys[i])+'\x01'

			pubKey = privKeys[i].pubkey.serialize()
			scriptSig = key.encode(len(signedMessage), 256) + signedMessage + key.encode(len(pubKey), 256) + pubKey

			self._tx["txIns"][i]["lenScript"] = len(scriptSig)
			self._tx["txIns"][i]["scriptSig"] = binascii.hexlify(scriptSig)

			print binascii.hexlify(signedMessage[:-1])
			print binascii.hexlify(getScriptSigMessage(self._tx,i))

		print self._tx
		self._rawTx = txSerialize(self._tx)

def txDeserialize(rawTx):

	tx = {}

	counter = 0

	tx["version"] = key.decode(rawTx[0:4][::-1], 256)

	counter += 4

	(tx["numIn"], counter) = getCompactInt(rawTx, counter)

	_txIns = []

	for i in range(tx["numIn"]):
		(_tempTxIn, counter) = getTxIn(rawTx, counter)
		_txIns.append(_tempTxIn)

	tx["txIns"] = _txIns

	(tx["numOut"], counter) = getCompactInt(rawTx, counter)

	_txOuts = []

	for i in range(tx["numOut"]):
		(_tempTxOut, counter) = getTxOut(rawTx, counter)
		_txOuts.append(_tempTxOut)

	tx["txOuts"]=_txOuts

	tx["lockTime"] = key.decode(rawTx[counter:counter+4], 256)

	return tx

def txSerialize(tx):

	rawTx = ""

	rawTx += key.encode(tx["version"], 256, 4)[::-1]

	rawTx += setCompactInt(tx["numIn"])

	for i in range(tx["numIn"]):
		rawTx += setTxIn(tx["txIns"][i])

	rawTx += setCompactInt(tx["numOut"])

	for i in range(tx["numOut"]):
		rawTx += setTxOut(tx["txOuts"][i])

	rawTx += key.encode(tx["lockTime"], 256, 4)[::-1]

	return rawTx 

def getCompactInt(s, counter):

	num = key.decode(s[counter:counter+1], 256)

	if num <= 252:
		return (num, counter + 1)
	elif num == 0xfd:
		return (key.decode(s[counter+1:counter+3][::-1], 256), counter+3) #0xfdxxxx, 2bytes after 0xfd
	elif num == 0xfe:
		return (key.decode(s[counter+1:counter+5][::-1], 256), counter+5) #0xfexxxxxxxx, 4bytes after 0xfe
	elif num == 0xff:
		return (key.decode(s[counter+1:counter+9][::-1], 256), counter+9) #0xffxxxxxxxxxxxxxxx, 8bytes after 0xff

	return None

def getTxIn(s, counter):
	_txIn = {}
	_txIn["prevOutTxid"] = binascii.hexlify(s[counter:counter+32][::-1])
	_txIn["prevOutIndex"] = key.decode(s[counter+32:counter+36][::-1], 256)
	(_txIn["lenScript"], counter) = getCompactInt(s, counter+36)
	_txIn["scriptSig"] = binascii.hexlify(s[counter:counter+_txIn["lenScript"]])
	_txIn["sequence"] = binascii.hexlify(s[counter+_txIn["lenScript"]:counter+_txIn["lenScript"]+4][::-1])
	return (_txIn, counter+_txIn["lenScript"]+4)

def getTxOut(s, counter):
	_txOut = {}
	_txOut["value"] = key.decode(s[counter:counter+8][::-1], 256)
	(_txOut["lenScript"], counter) = getCompactInt(s, counter+8)
	_txOut["scriptPubKey"] = binascii.hexlify(s[counter:counter+_txOut["lenScript"]])
	return (_txOut, counter+_txOut["lenScript"])

def setCompactInt(value): # -> bytes

	if value <= 252:
		return key.encode(value, 256)
	elif value <= 0xffff:
		return '\xfd' + key.encode(value, 256, 2)[::-1]
	elif value <= 0xffffffff:
		return '\xfe' + key.encode(value, 256, 4)[::-1]
	else:
		return '\xff' + key.encode(value, 256, 8)[::-1]


def setTxIn(txIn): # -> bytes
	_rawTxIn = ""

	_rawTxIn += key.changeBase(txIn["prevOutTxid"], 16, 256)[::-1]
	_rawTxIn += key.encode(txIn["prevOutIndex"], 256, 4)[::-1]
	_rawTxIn += setCompactInt(txIn["lenScript"])
	#scriptSig = setScriptSig(prevTxs, tx)
	#_rawTxIn += setCompactInt(len(scriptSig))
	#_rawTxIn += scriptSig
	_rawTxIn += key.changeBase(txIn["scriptSig"], 16, 256)
	_rawTxIn += key.encode(txIn["sequence"], 256, 4)[::-1]

	return _rawTxIn

def setTxOut(txOut): # -> bytes 
	_rawTxOut = ""

	_rawTxOut += key.encode(txOut["value"], 256, 8)[::-1]
	_rawTxOut += setCompactInt(txOut["lenScript"])
	_rawTxOut += key.changeBase(txOut["scriptPubKey"], 16, 256)

	return _rawTxOut

def setScriptPubKey(pubKeyHash): # -> hex
	rawScriptPubKey = '76a9'

	rawScriptPubKey += key.encode(len(pubKeyHash), 16)
	rawScriptPubKey += binascii.hexlify(pubKeyHash)

	rawScriptPubKey += '88ac'

	return rawScriptPubKey

def getScriptSigMessage(tx, i): # -> bytes
	
	rawTx = ""

	rawTx += key.encode(tx["version"], 256, 4)[::-1]

	#rawTx += setCompactInt(len(prevTxs))
	rawTx += setCompactInt(1)

	#for i in range(len(prevTxs)):

	rawTx += key.changeBase(tx["txIns"][i]["prevOutTxid"], 16, 256)[::-1]
	rawTx += key.encode(tx["txIns"][i]["prevOutIndex"], 256, 4)[::-1]

	tempScriptPubKey = key.changeBase(tx["txIns"][i]["prevOutScriptPubKey"], 16, 256)[::-1]

	rawTx += setCompactInt(len(tempScriptPubKey))
	rawTx += tempScriptPubKey[::-1]
	rawTx += key.encode(tx["txIns"][i]["sequence"], 256, 4)[::-1]

	rawTx += setCompactInt(tx["numOut"])

	for i in range(tx["numOut"]):
		rawTx += setTxOut(tx["txOuts"][i])

	rawTx += key.encode(tx["lockTime"], 256, 4)[::-1]
	rawTx += key.encode(tx["sigHashCode"], 256, 4)[::-1]

	print 'rawTx'+binascii.hexlify(rawTx)

	return rawTx 

