from nameko.rpc import rpc
import dependencies


class session:
    name = 'session_service'

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


class news:
    name = 'news_service'
    database = dependencies.Database()

    @rpc
    def add_news(self, arr_filename, text):
        add_news = self.database.add_news(arr_filename, text)
        return add_news
    
    
    @rpc
    def checking_news_availability(self, news_id):
        news_availability = self.database.checking_news_availability(news_id)
        return news_availability
    
    
    @rpc
    def edit_news_text(self, news_id, text):
        edit_news_text = self.database.edit_news_text(news_id, text)
        return edit_news_text
    
    
    @rpc
    def add_news_file(self, news_id, arr_filename):
        add_news_file = self.database.add_news_file(news_id, arr_filename)
        return add_news_file
    
    
    @rpc
    def delete_news(self, news_id):
        delete_news = self.database.delete_news(news_id)
        return delete_news
    
    
    @rpc
    def delete_news_file(self, news_id, file_id):
        delete_news_file = self.database.delete_news_file(news_id, file_id)
        return delete_news_file
    
    
    @rpc
    def get_all_news(self):
        get_all_news = self.database.get_all_news()
        return get_all_news
    
    
    @rpc
    def get_news_by_id(self, news_id):
        get_news_by_id = self.database.get_news_by_id(news_id)
        return get_news_by_id
    
    
    @rpc
    def get_file(self, file_id):
        file = self.database.get_file(file_id)
        return file
