import time
from celery import Celery

primecal = Celery('prime', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

primecal.conf.task_routes = {
    'Async.getprime.getprime': {'queue': 'prime'}
}

def isPrime(n):
        if(n==1 | n==0):
            return False
        for i in range(2, n):
            if(n%i==0):
                return False
        return True

@primecal.task
def getprime(z, bleh):
    time.sleep(2) 
    count = 0
    i = 1
    while(count<=z):
        if(isPrime(i)):
            count = count + 1
        if count <= z:
            i = i + 1
    return i