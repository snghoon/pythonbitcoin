# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http.response import HttpResponseRedirect, HttpResponse
from django.urls import reverse

from wallet import Wallet
from transaction import Transaction
from wallet import key
import json
import requests


# Create your views here.

def wallet(request):

	_wallet = Wallet(privKey = 'd3bb5455675aba4d45267ac0976ab866b1e0b12febe00ea4ce616bacebd8de2b') # testnet address = mrmNVLCXsPk12MALWiKJpNbCiwi1tPyqEc
	#_wallet = Wallet()

	#return HttpResponse("Private key: %s Public Key: %s Address: %s"%(_wallet.getPrivKeyHex(), _wallet.getPubKeyHex(), _wallet.getAddressHex()))
	
	request.session['key']='d3bb5455675aba4d45267ac0976ab866b1e0b12febe00ea4ce616bacebd8de2b'

	return render(request,'wallet/index.html', 
		{'privKey':key.changeBase(_wallet.getPrivKeyHex()+'01', 16, 58)
		, 'pubKey':_wallet.getPubKeyHex()
		, 'P2PKH_address':_wallet.getAddressP2PKH()
		, 'txs':_wallet.getUTXOs()})

#def send(request, toAddr, amount):
def send(request):

	toAddr = request.POST['toAddr']
	amount = int(request.POST['amount'])

	_wallet = Wallet(privKey = request.session['key'])

	txid = _wallet.send(toAddr, amount)

	_tx = Transaction(txid)

	return render(request, 'wallet/transaction.html', {'tx':json.dumps(_tx.getTxInfo(), indent=4)})

	#return HttpResponseRedirect('wallet/transaction.html', {'tx':json.dumps(__tx.getTxInfo(), indent=4)})
	#return  HttpResponseRedirect(reverse('transaction', args=(txid,)))

def transaction(request, txhash):

	try:
		rawTx = requests.get("https://testnet.blockexplorer.com/api/rawtx/"+txhash).json()['rawtx']
	except Exception:
		return HttpResponse(Exception)
	
	print rawTx
	
	_tx = Transaction(rawTx)

	return render(request, 'wallet/transaction.html', {'tx':json.dumps(_tx.getTxInfo(), indent=4)})