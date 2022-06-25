from nameko.rpc import rpc
import time
from Async.getprime import getprime, primecal
from Async.getpalindrome import getpalindrome, palindrome
from celery.result import AsyncResult

class prime:
    name = "prime_service"

    
    @rpc
    def prime(self, z):
        id = getprime.apply_async((z, 1))
        result = AsyncResult(id.id, app=primecal)
        return result.get()
    
    @rpc
    def palindrome(self, z):
        id = getpalindrome.apply_async((z, 1))
        result = AsyncResult(id.id, app=palindrome)
        return result.get()
        
    @rpc
    def hello(self):
        return 'h4h4'
