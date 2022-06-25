from nameko.rpc import rpc
import dependencies 

class session:
    name = "storage_service"

    database = dependencies.Database()

    @rpc
    def download(self, file):
        result = self.database.download(file)
        return result

    @rpc
    def upload(self, file):
        result = self.database.upload(file)
        return result