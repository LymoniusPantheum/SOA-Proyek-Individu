import json

from nameko.web.handlers import http
from werkzeug.wrappers import Response
import uuid
import os

from flask import Flask, send_from_directory
from werkzeug.utils import secure_filename
from nameko.rpc import RpcProxy
from nameko.web.handlers import http

UPLOAD_FOLDER = 'data/news'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
EXTENSION_HEADER = {
    'txt': 'text/plain',
    'pdf': 'application/pdf',
    'png': 'image/png',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'gif': 'image/gif'
}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists('data'):
    os.mkdir('data')
if not os.path.exists(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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

    
    @http('GET', '/download/<int:id_file>')
    def download(self, request, id_file):
        cookies = request.cookies
        if cookies and self.session_rpc.redis_check(cookies['SESSID']) != None:
            result = self.storage_rpc.download(id_file, cookies['ID'])
            
            if result['result'] != 'Found':
                return "Not Found"
            
            filename = result['data']['name']
            response = Response(open(UPLOAD_FOLDER + '/' + filename, 'rb').read())
            file_type = filename.split('.')[-1]
            
            response.headers['Content-Type'] = EXTENSION_HEADER[file_type]
            response.headers['Content-Disposition'] = 'attachment; filename={}'.format(filename)
        
            return response
        else:
            return "Not even login"
    
    @http('POST', '/upload')
    def upload(self, request):
        cookies = request.cookies
        if cookies and self.session_rpc.redis_check(cookies['SESSID']) != None:
            if 'file' not in request.files:
                return "No File"
            files = request.files.getlist('file')
            for file in files:
                if file.filename == '':
                    return "No File"
            arrFilename = []
            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    arrFilename.append(filename)
                else:
                    return "Unsupported File Type"
            
            add_news = self.storage_rpc.upload(arrFilename, cookies['ID'])
            return add_news
        else:
            return "Not even login"
