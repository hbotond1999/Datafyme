from django.http import HttpResponse
from django.shortcuts import render

from common.vectordb.db.utils import insert_docs_to_collection


# Create your views here.
def loader(request):
    insert_docs_to_collection()
    return HttpResponse("DB loader")
