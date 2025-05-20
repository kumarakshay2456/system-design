import hashlib
import string
import random
from datetime import datetime

class URLShortener:
    def __init__(self):
        # In-memory storage (would be a database in production)
        self.url_mapping = {}  # short_url -> long_url
        self.custom_mapping = {}  # custom_alias -> long_url
        self.analytics = {}  # short_url -> visit_count

    def generate_short_url(self, long_url, custom_alias=None):
        """Generate a short URL for the given long URL."""
        # Handle custom alias if provided
        if custom_alias:
            if custom_alias in self.custom_mapping:
                raise ValueError("Custom alias already in use")
            self.custom_mapping[custom_alias] = long_url
            return custom_alias
        
        # Generate a short URL using MD5 hash
        url_hash = hashlib.md5(long_url.encode()).hexdigest()[:6]
        
        # Handle collisions
        counter = 0
        temp_url = url_hash
        while temp_url in self.url_mapping and self.url_mapping[temp_url] != long_url:
            counter += 1
            temp_url = url_hash + str(counter)
        
        # Store the mapping
        self.url_mapping[temp_url] = long_url
        self.analytics[temp_url] = 0
        
        return temp_url

    def get_long_url(self, short_url):
        """Get the original long URL for a given short URL."""
        # Try custom mapping first
        if short_url in self.custom_mapping:
            # Update analytics
            self.analytics[short_url] = self.analytics.get(short_url, 0) + 1
            return self.custom_mapping[short_url]
        
        # Try regular mapping
        if short_url in self.url_mapping:
            # Update analytics
            self.analytics[short_url] = self.analytics.get(short_url, 0) + 1
            return self.url_mapping[short_url]
        
        raise ValueError("Short URL not found")
    
    def get_analytics(self, short_url):
        """Get analytics for a given short URL."""
        if short_url in self.analytics:
            return {"visits": self.analytics[short_url]}
        elif short_url in self.custom_mapping:
            return {"visits": self.analytics.get(short_url, 0)}
        else:
            raise ValueError("Short URL not found")


# Example usage
shortener = URLShortener()
short_url = shortener.generate_short_url("https://www.example.com/very/long/url/that/needs/shortening")
print(f"Short URL: {short_url}")

long_url = shortener.get_long_url(short_url)
print(f"Original URL: {long_url}")

analytics = shortener.get_analytics(short_url)
print(f"Analytics: {analytics}")

# Custom alias example
custom_short = shortener.generate_short_url("https://www.example.com/custom", "example")
print(f"Custom Short URL: {custom_short}")