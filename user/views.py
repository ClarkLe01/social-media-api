from django.shortcuts import render


# Create your views here.
def caculate(a, b):
    if a == 1:
        return 0
    return a + b
