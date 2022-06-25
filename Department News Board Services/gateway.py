import json

from nameko.rpc import RpcProxy
from nameko.web.handlers import http

import dependencies
from werkzeug.wrappers import Response
import os

from flask import Flask, send_from_directory
from werkzeug.utils import secure_filename
import datetime


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


class NewsBoardGatewayService:
    name = 'news_board_gateway'
    session_rpc = RpcProxy('session_service')
    news_rpc = RpcProxy('news_service')
    session_provider = dependencies.Database()
    
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
            if result == "Success": 
                session_id = self.session_rpc.set_session(request)
                response = Response("Login Success")
                response.set_cookie('SESSID', session_id)
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
            return response
        else:
            return "Not even login"
    
    
    @http('POST', '/news')
    def add_news(self, request):
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
            
            add_news = self.news_rpc.add_news(arrFilename, request.form['text'])
            return add_news
        else:
            return "Not even login"
       
    @http('PUT', '/news/<int:news_id>')
    def edit_news_text(self, request, news_id):
        cookies = request.cookies
        if cookies and self.session_rpc.redis_check(cookies['SESSID']) != None:
            news_availability = self.news_rpc.checking_news_availability(news_id)
            if news_availability['result'] != 'Found':
                return "Not Found"

            timestamp = news_availability['data']['date_created']
            date = datetime.datetime.strptime(timestamp.split('T')[0], '%Y-%m-%d')
            current_date = datetime.datetime.date(datetime.datetime.now())
            
            if current_date >= datetime.datetime.date(date + datetime.timedelta(days=30)):
                return "Unable to edit, News has been archived"

            data = request.json
            edit_news_text = self.news_rpc.edit_news_text(news_id, data['text'])
            return edit_news_text 
        else:
            return "Not even login"
        
    @http('POST', '/news/<int:news_id>/file')
    def add_news_file(self, request, news_id):
        cookies = request.cookies
        if cookies and self.session_rpc.redis_check(cookies['SESSID']) != None:
            news_availability = self.news_rpc.checking_news_availability(news_id)
            if news_availability['result'] != 'Found':
                return "Not Found"
            
            timestamp = news_availability['response_data']['data']['created_on']
            date = datetime.datetime.strptime(timestamp.split('T')[0], '%Y-%m-%d')
            current_date = datetime.datetime.date(datetime.datetime.now())
            
            if current_date >= datetime.datetime.date(date + datetime.timedelta(days=30)):
                return "Unable to edit, News has been archived"
            
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
            
            add_news_file = self.news_rpc.add_news_file(news_id, arrFilename)
            
            return add_news_file
        else:
            return "Not even login"
        
    @http('DELETE', '/news/<int:news_id>')
    def delete_news(self, request, news_id):
        cookies = request.cookies
        if cookies and self.session_rpc.redis_check(cookies['SESSID']) != None:
            news_availability = self.news_rpc.checking_news_availability(news_id)
            if news_availability['result'] != 'Found':
                return "Not Found"
            
            delete_news = self.news_rpc.delete_news(news_id)
            return delete_news
        else:
            return "Not even login"
        
    @http('DELETE', '/news/<int:news_id>/file/<int:file_id>')
    def delete_news_file(self, request, news_id, file_id):
        cookies = request.cookies
        if cookies and self.session_rpc.redis_check(cookies['SESSID']) != None:
            news_availability = self.news_rpc.checking_news_availability(news_id)
            if news_availability['result'] != 'Found':
                return "Not Found"
            
            timestamp = news_availability['response_data']['data']['created_on']
            date = datetime.datetime.strptime(timestamp.split('T')[0], '%Y-%m-%d')
            current_date = datetime.datetime.date(datetime.datetime.now())
            
            if current_date >= datetime.datetime.date(date + datetime.timedelta(days=30)):
                return "Unable to edit, News has been archived"
            
            delete_news_file = self.news_rpc.delete_news_file(news_id, file_id)
            
            return delete_news_file
        else:
            return "Not even login"
        
    @http('GET', '/news')
    def get_all_news(self, request):
        get_all_news = self.news_rpc.get_all_news()
        
        return get_all_news
    
    
    @http('GET', '/news/<int:news_id>')
    def get_news_by_id(self, request, news_id):
        news_availability = self.news_rpc.checking_news_availability(news_id)
        if news_availability['result'] != 'Found':
            return "Not Found"
        
        get_news_by_id = self.news_rpc.get_news_by_id(news_id)
        
        return get_news_by_id
    
    
    @http('GET', '/api/news/file/<int:file_id>')
    def download_file(self, request, file_id):
        file = self.news_rpc.get_file(file_id)
        
        if int(file['response_code']) != 200:
            return int(file['response_code']), json.dumps(file['response_data'])
        
        filename = file['response_data']['data']['filename']
        response = Response(open(UPLOAD_FOLDER + '/' + filename, 'rb').read())
        file_type = filename.split('.')[-1]
        
        response.headers['Content-Type'] = EXTENSION_HEADER[file_type]
        response.headers['Content-Disposition'] = 'attachment; filename={}'.format(filename)
        
        return response
