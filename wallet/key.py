#-*- coding: utf-8 -*-

import hashlib
import secp256k1
import re

def getPrivKeyFromSeed(seed):
	return secp256k1.PrivateKey(hashlib.sha256(seed).digest())

def getPrivKey(privKey):
	return secp256k1.PrivateKey(privKey, raw=True)

def getPubKey(privKey, raw=False):
	
	if raw:
		return secp256k1.PrivateKey(privKey, raw=True).pubkey
	else:
		return privKey.pubkey

def ripemd160(message):
	h = hashlib.new('ripemd160')
	h.update(message)
	return h.digest()

def getAddress(pubKey, raw=False):
	if raw:
		return ripemd160(hashlib.sha256(pubKey).digest())
	else:
		return ripemd160(hashlib.sha256(pubKey.serialize()).digest())

# https://github.com/vbuterin/pybitcointools/bitcoin/py2specials.py

code_strings = {
	2: '01',
	10: '0123456789',
	16: '0123456789abcdef',
	32: 'abcdefghijklmnopqrstuvwxyz234567',
	58: '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz',
    256: ''.join([chr(x) for x in range(256)])
}

def doubleSha256(s):
	return hashlib.sha256(hashlib.sha256(s).digest()).digest()

def getCodeString(base):
	return code_strings[base]

def decode(s, base):
	base = int(base)
	codeString = getCodeString(base)
	result = 0

	if base == 16:
		s = s.lower()

	while len(s)>0:
		result *= base
		result += codeString.find(s[0])
		s = s[1:]

	return result

def encode(val, base, minlen=0):
	base, minlen = int(base), int(minlen)
	codeString = getCodeString(base)

	result = ''

	while val > 0:
		result = codeString[val%base] + result
		val //= base

	return codeString[0] * max(minlen - len(result), 0) + result

def changeBase(s, frm, to, minlen=0):
	return encode(decode(s, frm), to, minlen)


"""
Prefix

Bitcoin address: 0x00
P2SH address: 0x05
Bitcoin testnet address: 0x6F
Private Key WIF: 0x80
BIP38 encrypted private key: 0x0142
BIP32 extended public key: 0x0488B21E
"""

def base58check(message, prefix=0):

	versionPrefix = ''

	if prefix ==0:
		versionPrefix = '\x00'		

	while prefix > 0:
		versionPrefix = chr(int(prefix%256)) + versionPrefix
		prefix//=256
	
	leadingzbytes = len(re.match('^\x00*', versionPrefix).group(0))

	checksum = doubleSha256(versionPrefix+message)

	payload = versionPrefix + message + checksum[:4]

	return '1'*leadingzbytes+changeBase(payload, 256, 58)

def signMessage(message, privKey): # -> bytes
	_signedMessage = privKey.ecdsa_sign(doubleSha256(message), raw=True)
	return privKey.ecdsa_serialize(_signedMessage)






