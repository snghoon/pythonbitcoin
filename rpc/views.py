# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.shortcuts import render
from django.http.request import HttpRequest
from django.http.response import HttpResponse
import json, requests, time

# Create your views here.

class RPCHost(object):

	def __init__(self, url):
		self._url = url;
		self._headers ={'content-type': 'application/json'}

	def call(self, method, *params):
		payload = json.dumps({"method":method, "params":list(params), "jsonrpc": "1.0"})
		try:
			response = requests.post(self._url, headers=self._headers,data=payload)
		except:
			return "Connection Failed"

		return response.json()['result']

def callRPC(request, method):
	url = "http://foo:qDDZdeQ5vw9XXFeVnXT4PZ--tGN2xNjjR4nrtyszZx0=@10.117.0.111:18332"

	host = RPCHost(url)
	return HttpResponse(host.call(method))

