import string
import time
from datetime import datetime

class URLShortenerBase62:
    def __init__(self):
        self.url_mapping = {}  # short_url -> long_url
        self.id_mapping = {}   # long_url -> id (to avoid duplicates)
        self.analytics = {}    # short_url -> visit data
        self.counter = 10000   # Starting counter (to avoid very short URLs)
        self.characters = string.ascii_letters + string.digits  # Base62: a-zA-Z0-9
    
    def base62_encode(self, num):
        """Convert a decimal number to base62 string."""
        if num == 0:
            return self.characters[0]
        
        base62 = ""
        base = len(self.characters)
        
        while num:
            num, remainder = divmod(num, base)
            base62 = self.characters[remainder] + base62
            
        return base62
    
    def base62_decode(self, base62_str):
        """Convert a base62 string to decimal."""
        num = 0
        base = len(self.characters)
        
        for char in base62_str:
            num = num * base + self.characters.index(char)
            
        return num
    
    def generate_short_url(self, long_url, custom_alias=None):
        """Generate a short URL for the given long URL."""
        # Return existing mapping if URL already shortened
        if long_url in self.id_mapping:
            return self.base62_encode(self.id_mapping[long_url])
        
        # Handle custom alias
        if custom_alias:
            if custom_alias in self.url_mapping:
                raise ValueError("Custom alias already in use")
            self.url_mapping[custom_alias] = long_url
            self.analytics[custom_alias] = {
                "created_at": datetime.now(),
                "visits": 0,
                "last_visited": None
            }
            return custom_alias
        
        # Generate new short URL
        self.counter += 1
        short_url = self.base62_encode(self.counter)
        
        # Store mappings
        self.url_mapping[short_url] = long_url
        self.id_mapping[long_url] = self.counter
        self.analytics[short_url] = {
            "created_at": datetime.now(),
            "visits": 0,
            "last_visited": None
        }
        
        return short_url
    
    def get_long_url(self, short_url):
        """Get the original long URL for a given short URL."""
        if short_url in self.url_mapping:
            # Update analytics
            self.analytics[short_url]["visits"] += 1
            self.analytics[short_url]["last_visited"] = datetime.now()
            return self.url_mapping[short_url]
        
        raise ValueError("Short URL not found")
    
    def get_analytics(self, short_url):
        """Get analytics for a given short URL."""
        if short_url in self.analytics:
            return self.analytics[short_url]
        
        raise ValueError("Short URL not found")


# Example usage
shortener = URLShortenerBase62()
short_url = shortener.generate_short_url("https://www.example.com/very/long/url/that/needs/shortening")
print(f"Short URL: {short_url}")

# Access URL multiple times
for _ in range(3):
    long_url = shortener.get_long_url(short_url)
    time.sleep(0.1)  # Simulate time between accesses

analytics = shortener.get_analytics(short_url)
print(f"Analytics: {analytics}")