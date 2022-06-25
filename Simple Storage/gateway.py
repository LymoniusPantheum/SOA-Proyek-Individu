import json

from nameko.web.handlers import http
from werkzeug.wrappers import Response
import uuid

from nameko.rpc import RpcProxy
from nameko.web.handlers import http


class Gateway:
    name = 'gateway'

    session_rpc = RpcProxy('session_service')
    storage_rpc = RpcProxy('storage_service')
    
    @http('POST', '/register')
    def register(self, request):
        cookies = request.cookies
        if not cookies:
            request = request.json
            result = self.session_rpc.register(request)
            if result == "Success": 
                session_id = self.session_rpc.set_session(request)
                response = Response("Register Success")
                response.set_cookie('SESSID', session_id)
                return response
            else:
                return "Username already exist"
        else:
            return "Already login, can't register"
    
    @http('POST', '/login')
    def login(self, request):
        cookies = request.cookies
        if not cookies:
            request = request.json
            result = self.session_rpc.login(request)
            if result: 
                session_id = self.session_rpc.set_session(request)
                response = Response("Login Success")
                response.set_cookie('SESSID', session_id)
                response.set_cookie("ID", str(result))
                return response
            else:
                return "Username or Password is wrong"
        else:
            return "Already login"

    @http('GET', '/logout')
    def logout(self, request):
        cookies = request.cookies
        if cookies:
            self.session_rpc.destroy_session(cookies['SESSID'])
            response = Response("Logout Success")
            response.delete_cookie('SESSID', cookies['SESSID'])
            response.delete_cookie('ID', cookies['ID'])
            return response
        else:
            return "Not even login"

    
    @http('GET', '/download')
    def download(self, request):
        cookies = request.cookies
        if cookies and self.session_rpc.redis_check(cookies['SESSID']) != None:
            result = self.storage_rpc.download()
            return json.dumps(result)
        else:
            return "Not even login"
    
    @http('POST', '/upload')
    def upload(self, request):
        cookies = request.cookies
        if cookies and self.session_rpc.redis_check(cookies['SESSID']) != None:
            result = self.storage_rpc.upload(request)
            return json.dumps(result)
        else:
            return "Not even login"
