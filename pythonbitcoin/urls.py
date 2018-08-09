"""pythonbitcoin URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from rpc import views as rpc_views
from wallet import views as wallet_views

urlpatterns = [
	url(r'^rpc/(?P<method>[a-z]+)', rpc_views.callRPC),
	url(r'^wallet$', wallet_views.wallet),
	url(r'^transaction/(?P<txhash>[a-z0-9]+)', wallet_views.transaction),
	url(r'^wallet/send/', wallet_views.send, name='send'),
]
