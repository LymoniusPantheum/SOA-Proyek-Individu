from nameko.rpc import rpc
from itertools import combinations
from itertools import permutations
import dependencies 

class session:
    name = "session_service"

    database = dependencies.Database()

    @rpc
    def register(self, json):
        result = self.database.register(json)
        return result
    
    @rpc
    def login(self, json):
        result = self.database.login(json)
        return result

    @rpc
    def logout(self, json):
        result = self.database.logout(json)
        return result

    @rpc
    def get_session(self, id):
        result = self.database.get_session(id)
        return result

    @rpc
    def set_session(self, data):
        result = self.database.set_session(data)
        return result

    @rpc
    def destroy_session(self, id):
        self.database.set_session(id)
        return

    @rpc
    def redis_check(self, id):
        result = self.database.get_session(id)
        if result != None:
            return True
        else:
            return False