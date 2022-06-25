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
        id = cursor.fetchone()
        if id:
            cursor.close()
            return id['id']
        else:
            return

    def upload(self, file, id_user):
        cursor = self.connection.cursor(dictionary=True)
        
        for i in range(len(file)):
            sql = 'INSERT INTO file(name, id_user) VALUES (%s, %s)'
            cursor.execute(sql, [str(file[i]), id_user])
            self.connection.commit()
        cursor.close()
        return "File uploaded"
    
    def download(self, id_file, id_user):
        cursor = self.connection.cursor(dictionary=True)
        response = None
        
        sql = 'SELECT COUNT(*) AS x, file.* FROM file WHERE id = %s AND id_user = %s'
        cursor.execute(sql, [int(id_file), int(id_user)])
        result = cursor.fetchone()
        
        if result['x'] <= 0:
            response = {
                'result' : 'Not Found'
            }
        else:
            response = {
                'result': 'Found',
                "data": {
                    'id': result['id'],
                    'name': result['name']
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
        return DatabaseWrapper(self.connection_pool.get_connection(), self.client )