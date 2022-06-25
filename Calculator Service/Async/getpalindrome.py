import time
from celery import Celery

palindrome = Celery('prime', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

palindrome.conf.task_routes = {
    'Async.getpalindrome.getpalindrome': {'queue': 'palindrome'}
}

def isPalindrome(n):
    total = 0
    temp = n
    while(n>0):
        last=n%10
        total=total*10+last
        n=n//10
    if temp == total:
        return True
    return False

def isPrime(n):
        if(n==1 | n==0):
            return False
        for i in range(2, n):
            if(n%i==0):
                return False
        return True

@palindrome.task
def getpalindrome(z, bleh):
    time.sleep(1)
    count = 0
    i = 1
    while(count<=z):
        if(isPrime(i) & isPalindrome(i)):
            count = count + 1
        if count <= z:
            i = i + 1
    return i