from nameko.extensions import DependencyProvider

import pickle
import uuid
import redis

import mysql.connector
from mysql.connector import Error
from mysql.connector import pooling

class DatabaseWrapper:

    connection = None

    def __init__(self, connection, redis):
        self.connection = connection
        self.redis = redis
        self.default_expire = 60 * 60
    
    def generate_session_id(self):
        key = str(uuid.uuid4())
        # while self.redis.exist(key):
            # key = str(uuid.uuid4())
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

    def upload(self, file):
        cursor = self.connection.cursor(dictionary=True)
    
    def download(self):
        cursor = self.connection.cursor(dictionary=True)
        result = []


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