from datetime import datetime
import string
import time

class url_shortner:
    def __init__(self):
        self.url_mapping = {}
        self.count_mapping = {}
        self.analytics = {}
        self.counter = 1000
        self.short_algo = ShortnerAlgo()
    
    def generate_short_url(self, long_url, custom_mapping=None):
        if custom_mapping:
            if custom_mapping in self.url_mapping:
                raise ValueError(f"custom {custom_mapping} is alreday mapped with the another url")
            self.url_mapping[custom_mapping] = long_url
            self.analytics[custom_mapping] = {"total_visited": 0, "last_visited":0, "created_at": datetime.now()}
            return custom_mapping
        self.counter += 1
        short_string = self.short_algo.encode(self.counter)
    
        self.url_mapping[short_string] = long_url
        self.count_mapping[long_url] = self.counter
        self.analytics[short_string] = {"total_visited": 0, "last_visited":None, "created_at": datetime.now()}
        return short_string
    
    def get_long_url(self, short_url):

        if short_url in self.url_mapping:
            url = self.url_mapping[short_url]
            analytics_data = self.analytics[short_url]
            analytics_data["total_visited"] = analytics_data["total_visited"] + 1
            analytics_data['last_visited'] = datetime.now()
            self.analytics[short_url] = analytics_data
            return url
        raise ValueError(f"Shorl url is not found in database {short_url}")
    
    def get_analytics(self, short_url):
        if short_url in self.analytics:
            return self.analytics[short_url]
        raise ValueError(f"Analytics is not found for this url {short_url}")
    
    

class ShortnerAlgo:
    def __init__(self, algo_name="base62"):
        self.algo_name = algo_name
        self.character_62 = string.ascii_letters + string.digits
    
    def encode(self, num):
        if self.algo_name == "base62":
            base62 = ""
            base_char_len = len(self.character_62)
            while num:
                num, rem = divmod(num, base_char_len)
                base62 = self.character_62[rem] + base62
            return base62
        else:
            ValueError("Algo is not implemented here")
    
    def decode(self, url):
        if self.algo_name == "base62":
            num = 0
            base_char_len = len(self.character_62)
            if self.algo_name == "base62":
                for char in url:
                    num = num + self.character_62.index(char) * base_char_len
            return num
        else:
            ValueError("Algo is not implemented here")


url_short_manager = url_shortner()

url = "https://www.example.com/very/long/url/that/needs/shortening"
short_url = url_short_manager.generate_short_url(url)
print(f"Short url is -> {short_url}")

for i in range(5):
    long_url = url_short_manager.get_long_url(short_url)
    time.sleep(5)
print("Analytics is", url_short_manager.get_analytics(short_url))

    



