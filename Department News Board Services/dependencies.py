from nameko.extensions import DependencyProvider

import pickle
import uuid
import redis

import mysql.connector
from mysql.connector import Error
import mysql.connector.pooling

class DatabaseWrapper:

    connection = None

    def __init__(self, connection, redis):
        self.connection = connection
        self.redis = redis
        self.default_expire = 60 * 60
    
    def generate_session_id(self):
        key = str(uuid.uuid4())
        while self.redis.exists(key):
            key = str(uuid.uuid4())
        return key

    def set_session(self, user_data):
        # Pickle User Data so that can be stored in Redis
        user_data_pickled = pickle.dumps(user_data)

        # Get Session ID
        session_id = self.generate_session_id()

        # Store Session Data with Expire Time in Redis
        self.redis.set(session_id, user_data_pickled, ex=self.default_expire)

        return session_id
    
    def get_session(self, session_id):
        # Get the Data from Redis
        result = self.redis.get(session_id)

        if result:
        # Unpack the user data from Redis
            user_data = pickle.loads(result)
        else:
            user_data = None

        return user_data

    def destroy_session(self, session_id):
        self.redis.delete(session_id)
        return

    def register(self, json):
        cursor = self.connection.cursor(dictionary=True)
        username = json['username']
        password = json['password']
        check = "SELECT * FROM data WHERE username = %s"
        cursor.execute(check, [username])
        if not cursor.fetchone():
            sql = "INSERT INTO data(username, password) VALUES(%s, %s)"
            cursor.execute(sql, [username, password])
            self.connection.commit()
            cursor.close()
            return "Success"
        else:
            return

    def login(self, json):
        cursor = self.connection.cursor(dictionary=True)
        username = json['username']
        password = json['password']
        sql = "SELECT * FROM data WHERE username = %s AND password = %s"
        cursor.execute(sql, [username, password])
        if cursor.fetchone():
            cursor.close()
            return "Success"
        else:
            return

    def add_news(self, arr_filename, text):
        cursor = self.connection.cursor(dictionary=True)
        
        sql = 'INSERT INTO news(text, status) VALUES (%s, %s)'
        cursor.execute(sql, [str(text), int(0)])
        self.connection.commit()
        lastRowId = cursor.lastrowid
        
        for i in range(len(arr_filename)):
            sql = 'INSERT INTO news_file(name, status, id_news) VALUES (%s, %s, %s)'
            cursor.execute(sql, [str(arr_filename[i]), int(0), int(lastRowId)])
            self.connection.commit()
        
        cursor.close()
        return "News added"
    
    
    def checking_news_availability(self, id_news):
        cursor = self.connection.cursor(dictionary=True)
        response = None
        
        sql = 'SELECT COUNT(*) AS x, news.* FROM news WHERE id = %s AND status = 0'
        cursor.execute(sql, [int(id_news)])
        result = cursor.fetchone()
        
        if result['x'] > 0:
            response = {
                'result': 'Found',
                "data": {
                    'id': result['id'],
                    'text': result['text'],
                    'status': result['status'],
                    'date_created': result['date_created']
                }
            }
        
        cursor.close()
        return response
    
    
    def edit_news_text(self, id_news, text):
        cursor = self.connection.cursor(dictionary=True)
        
        sql = 'UPDATE news SET text =%s WHERE id = %s'
        cursor.execute(sql, [str(text), int(id_news)])
        self.connection.commit()
        
        cursor.close()
        return "Edited"
    
    
    def add_news_file(self, id_news, arr_filename):
        cursor = self.connection.cursor(dictionary=True)
        
        for i in range(len(arr_filename)):
            sql = 'INSERT INTO news_file(filename, status, id_news) VALUES (%s, %s, %s)'
            cursor.execute(sql, [str(arr_filename[i]), int(0), int(id_news)])
        
        self.connection.commit()
        cursor.close()
        return "File added"
    
    
    def delete_news(self, id_news):
        cursor = self.connection.cursor(dictionary=True)
        
        sql = 'UPDATE news_file SET status=%s WHERE id_news = %s'
        cursor.execute(sql, [int(1), int(id_news)])
        
        sql = 'UPDATE news SET status=%s WHERE id = %s'
        cursor.execute(sql, [int(1), int(id_news)])
        
        self.connection.commit()
        cursor.close()
        return "Deleted"
    
    
    def delete_news_file(self, id_news, file_id):
        cursor = self.connection.cursor(dictionary=True)
        
        sql = 'SELECT COUNT(*) AS x FROM `news_files` WHERE id_news = %s AND id = %s'
        cursor.execute(sql, [int(id_news), int(file_id)])
        result = cursor.fetchone()
        
        if result['x'] <= 0:
            return {
                'response_code': 404,
                'response_data': {
                    "status": "error",
                    "message": "File not found"
                }
            }
        
        sql = 'UPDATE news_file SET status=%s WHERE id = %s AND id_news = %s'
        cursor.execute(sql, [int(1), int(file_id), int(id_news)])
        
        self.connection.commit()
        cursor.close()
        return "Deleted"
    
    
    def get_all_news(self):
        cursor = self.connection.cursor(dictionary=True)
        result = []
        
        sql = 'SELECT * FROM news WHERE status = %s'
        cursor.execute(sql, [int(0)])
        
        for row in cursor.fetchall():
            files = []
            
            sql_news = 'SELECT * FROM news_file WHERE id_news = %s AND status = %s'
            cursor.execute(sql_news, [int(row['id']), int(0)])
            
            for file in cursor.fetchall():
                files.append({
                    'id': file['id'],
                    'name': file['name']
                })
            
            result.append({
                'id': row['id'],
                'text': row['text'],
                'date_created': row['date_created'],
                'files': files
            })
        
        cursor.close()
        return result
    
    
    def get_news_by_id(self, id_news):
        cursor = self.connection.cursor(dictionary=True)
        response = None
        files = []
        
        sql = 'SELECT * FROM`news WHERE status = %s AND id = %s'
        cursor.execute(sql, [int(0), int(id_news)])
        result = cursor.fetchone()
        
        sql_get_news_files = 'SELECT * FROM news_file WHERE id_news = %s AND status = %s'
        cursor.execute(sql_get_news_files, [int(result['id']), int(0)])
        
        for file in cursor.fetchall():
            files.append({
                'id': file['id'],
                'filename': file['filename']
            })
        
        response = {
            'id': result['id'],
            'text': result['text'],
            'date_created': result['date_created'],
            'files': files
        }
        
        cursor.close()
        return {
            'response_code': 200,
            'response_data': {
                "status": "success",
                "data": response
            }
        }
    
    
    def get_file(self, file_id):
        cursor = self.connection.cursor(dictionary=True)
        response = None
        
        sql = 'SELECT COUNT(*) AS x, news_files.* FROM `news_files` WHERE id = %s AND deleted = 0'
        cursor.execute(sql, [int(file_id)])
        result = cursor.fetchone()
        
        if result['x'] <= 0:
            response = {
                'response_code': 404,
                'response_data': {
                    "status": "error",
                    "message": "File not found"
                }
            }
        else:
            response = {
                'response_code': 200,
                'response_data': {
                    "status": "success",
                    "data": {
                        'id': result['id'],
                        'filename': result['filename']
                    }
                }
            }
        
        cursor.close()
        return response


class Database(DependencyProvider):

    connection_pool = None

    def __init__(self):
        try:
            self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="database_pool",
                pool_size=5,
                pool_reset_session=True,
                host='192.168.245.129',
                port='3306',
                database='SOA',
                user='admin',
                password='admin123'
            )
        except Error as e :
            print ("Error while connecting to MySQL using Connection pool ", e)
    
    def setup(self):
        self.client = redis.Redis(host='127.0.0.1', port=6379, db=0)

    def get_dependency(self, worker_ctx):
        return DatabaseWrapper(self.connection_pool.get_connection(), self.client)