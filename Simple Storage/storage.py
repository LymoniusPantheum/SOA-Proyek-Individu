from nameko.rpc import rpc
import dependencies 

class session:
    name = "storage_service"

    database = dependencies.Database()

    @rpc
    def download(self, file, id):
        result = self.database.download(file, id)
        return result

    @rpc
    def upload(self, file, id):
        result = self.database.upload(file, id)
        return result