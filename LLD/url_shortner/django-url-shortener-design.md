# URL Shortener: Low-Level Design in Python

## Problem Statement
Design a URL shortening service like TinyURL or Bitly that can:
1. Generate a unique short URL for a given long URL
2. Redirect users to the original URL when they access the short URL
3. Handle high traffic and storage requirements
4. Provide analytics on URL access (optional extension)

## Approach

### 1. Core Components
- URL Shortening Algorithm
- Storage Mechanism
- API Endpoints
- Redirection Service

### 2. Key Design Considerations
- Collision Handling: Ensuring unique short URLs
- Scalability: Handling high traffic and storage
- Performance: Fast encoding/decoding and redirection
- Security: Preventing abuse and protecting sensitive URLs

### 3. URL Shortening Algorithms
Two main approaches:

**a. Hash-based Approach**
- Use a hash function (MD5, SHA256) to generate a hash of the input URL
- Take the first 6-8 characters of the hash as the short URL
- Handle collisions by adding a counter or rehashing

**b. Base62 Encoding with Counter**
- Use an auto-incrementing ID and convert it to base62 (a-zA-Z0-9)
- This generates a unique, short alphanumeric string
- More efficient for storage and guaranteed uniqueness

## Implementation in Python

### Base Solution: URL Shortener Class

```python
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
```

### Enhanced Implementation: Using Base62 Encoding

```python
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
```

### Web Application Implementation (Flask)

```python
from flask import Flask, request, redirect, jsonify
import hashlib
import string
import random
from datetime import datetime

app = Flask(__name__)

class URLShortener:
    def __init__(self):
        self.url_mapping = {}
        self.custom_mapping = {}
        self.analytics = {}
    
    # [Include all the methods from the base implementation]
    # ... (omitted for brevity - copy from the base implementation)

# Create a global instance
shortener = URLShortener()

@app.route('/shorten', methods=['POST'])
def shorten_url():
    data = request.get_json()
    
    if 'url' not in data:
        return jsonify({'error': 'URL is required'}), 400
    
    long_url = data['url']
    custom_alias = data.get('custom_alias')
    
    try:
        short_url = shortener.generate_short_url(long_url, custom_alias)
        short_url_full = f"http://{request.host}/{short_url}"
        return jsonify({
            'short_url': short_url_full,
            'long_url': long_url
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@app.route('/<short_url>')
def redirect_to_url(short_url):
    try:
        long_url = shortener.get_long_url(short_url)
        return redirect(long_url)
    except ValueError:
        return jsonify({'error': 'URL not found'}), 404

@app.route('/analytics/<short_url>')
def get_analytics(short_url):
    try:
        analytics = shortener.get_analytics(short_url)
        return jsonify(analytics)
    except ValueError:
        return jsonify({'error': 'URL not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
```

### Web Application Implementation (Django)

Let's implement the URL shortener using Django's powerful framework:

#### Step 1: Project Setup

First, set up a Django project:

```bash
# Create Django project
django-admin startproject urlshortener
cd urlshortener

# Create an app for our URL shortener
python manage.py startapp shortener
```

#### Step 2: Define Models

Create models in `shortener/models.py`:

```python
from django.db import models
from django.utils import timezone
import hashlib
import string
import random

class URL(models.Model):
    long_url = models.URLField(max_length=2000)
    short_url = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.short_url} -> {self.long_url[:30]}{'...' if len(self.long_url) > 30 else ''}"
    
    @classmethod
    def create_short_url(cls, long_url, custom_alias=None):
        """Create a new short URL for the given long URL"""
        # Check if URL already exists
        existing = cls.objects.filter(long_url=long_url).first()
        if existing:
            return existing.short_url
            
        # Handle custom alias
        if custom_alias:
            if cls.objects.filter(short_url=custom_alias).exists():
                raise ValueError("Custom alias already in use")
            
            url_obj = cls(long_url=long_url, short_url=custom_alias)
            url_obj.save()
            return custom_alias
        
        # Generate a short URL using hash
        url_hash = hashlib.md5(long_url.encode()).hexdigest()[:6]
        
        # Handle collisions
        counter = 0
        temp_url = url_hash
        
        while cls.objects.filter(short_url=temp_url).exists():
            counter += 1
            temp_url = url_hash + str(counter)
        
        # Store the mapping
        url_obj = cls(long_url=long_url, short_url=temp_url)
        url_obj.save()
        
        return temp_url


class URLClick(models.Model):
    url = models.ForeignKey(URL, on_delete=models.CASCADE, related_name='clicks')
    clicked_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True, null=True)
    referer = models.URLField(max_length=2000, blank=True, null=True)
    
    def __str__(self):
        return f"Click on {self.url.short_url} at {self.clicked_at}"
```

#### Step 3: Create Views

Define views in `shortener/views.py`:

```python
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.utils.decorators import method_decorator
from django.conf import settings

import json
from datetime import datetime, timedelta

from .models import URL, URLClick

class ShortenURLView(View):
    @method_decorator(csrf_exempt)
    def post(self, request):
        try:
            data = json.loads(request.body)
            long_url = data.get('url')
            custom_alias = data.get('custom_alias')
            
            if not long_url:
                return JsonResponse({'error': 'URL is required'}, status=400)
                
            try:
                short_url = URL.create_short_url(long_url, custom_alias)
                short_url_full = f"{request.scheme}://{request.get_host()}/{short_url}"
                
                return JsonResponse({
                    'short_url': short_url_full,
                    'long_url': long_url
                })
            except ValueError as e:
                return JsonResponse({'error': str(e)}, status=400)
                
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)


def redirect_to_url(request, short_url):
    url_obj = get_object_or_404(URL, short_url=short_url)
    
    # Record click analytics
    click = URLClick(
        url=url_obj,
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT'),
        referer=request.META.get('HTTP_REFERER')
    )
    click.save()
    
    return redirect(url_obj.long_url)


class URLAnalyticsView(View):
    def get(self, request, short_url):
        try:
            url_obj = URL.objects.get(short_url=short_url)
            
            # Get time periods for analysis
            now = datetime.now()
            today = now.replace(hour=0, minute=0, second=0, microsecond=0)
            week_ago = today - timedelta(days=7)
            month_ago = today - timedelta(days=30)
            
            # Get click counts
            total_clicks = url_obj.clicks.count()
            today_clicks = url_obj.clicks.filter(clicked_at__gte=today).count()
            weekly_clicks = url_obj.clicks.filter(clicked_at__gte=week_ago).count()
            monthly_clicks = url_obj.clicks.filter(clicked_at__gte=month_ago).count()
            
            # Get recent clicks
            recent_clicks = [{
                'time': click.clicked_at.isoformat(),
                'ip': click.ip_address,
                'agent': click.user_agent,
                'referer': click.referer
            } for click in url_obj.clicks.order_by('-clicked_at')[:10]]
            
            return JsonResponse({
                'url': url_obj.long_url,
                'short_url': url_obj.short_url,
                'created_at': url_obj.created_at.isoformat(),
                'analytics': {
                    'total_clicks': total_clicks,
                    'today_clicks': today_clicks,
                    'weekly_clicks': weekly_clicks,
                    'monthly_clicks': monthly_clicks,
                    'recent_clicks': recent_clicks
                }
            })
            
        except URL.DoesNotExist:
            return JsonResponse({'error': 'URL not found'}, status=404)
```

#### Step 4: Configure URLs

Set up URL routes in `shortener/urls.py`:

```python
from django.urls import path
from . import views

urlpatterns = [
    path('api/shorten/', views.ShortenURLView.as_view(), name='shorten_url'),
    path('api/analytics/<str:short_url>/', views.URLAnalyticsView.as_view(), name='url_analytics'),
    path('<str:short_url>/', views.redirect_to_url, name='redirect_to_url'),
]
```

Update the project's `urlshortener/urls.py`:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('shortener.urls')),
]
```

#### Step 5: Register Admin Interface

Create `shortener/admin.py`:

```python
from django.contrib import admin
from .models import URL, URLClick

@admin.register(URL)
class URLAdmin(admin.ModelAdmin):
    list_display = ('short_url', 'truncated_url', 'created_at', 'click_count')
    search_fields = ('short_url', 'long_url')
    readonly_fields = ('created_at',)
    
    def truncated_url(self, obj):
        if len(obj.long_url) > 50:
            return f"{obj.long_url[:50]}..."
        return obj.long_url
    truncated_url.short_description = 'Long URL'
    
    def click_count(self, obj):
        return obj.clicks.count()
    click_count.short_description = 'Clicks'

@admin.register(URLClick)
class URLClickAdmin(admin.ModelAdmin):
    list_display = ('url', 'clicked_at', 'ip_address', 'truncated_agent')
    list_filter = ('clicked_at',)
    readonly_fields = ('clicked_at',)
    
    def truncated_agent(self, obj):
        if obj.user_agent and len(obj.user_agent) > 50:
            return f"{obj.user_agent[:50]}..."
        return obj.user_agent
    truncated_agent.short_description = 'User Agent'
```

#### Step 6: Settings Configuration

Update `urlshortener/settings.py` to include your app:

```python
# Add 'shortener' to INSTALLED_APPS
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'shortener',  # Add this line
]
```

#### Step 7: Run Migrations

Set up the database:

```bash
python manage.py makemigrations
python manage.py migrate
```

#### Step 8: Create a superuser for admin access

```bash
python manage.py createsuperuser
```

#### Step 9: Run the Server

```bash
python manage.py runserver
```

#### Step 10: Optional - Base62 Encoding Implementation

If you want to use Base62 encoding instead of hash-based approach, create a utility file `shortener/utils.py`:

```python
import string

class Base62:
    CHARSET = string.digits + string.ascii_lowercase + string.ascii_uppercase
    BASE = len(CHARSET)
    
    @classmethod
    def encode(cls, num):
        """Convert a decimal number to base62 string"""
        if num == 0:
            return cls.CHARSET[0]
        
        encoding = ""
        while num:
            num, remainder = divmod(num, cls.BASE)
            encoding = cls.CHARSET[remainder] + encoding
            
        return encoding
    
    @classmethod
    def decode(cls, base62_str):
        """Convert a base62 string to decimal"""
        num = 0
        for char in base62_str:
            num = num * cls.BASE + cls.CHARSET.index(char)
            
        return num
```

Then, you can modify the `URL` model's `create_short_url` method to use Base62 encoding:

```python
@classmethod
def create_short_url(cls, long_url, custom_alias=None):
    """Create a new short URL for the given long URL using Base62 encoding"""
    from .utils import Base62
    
    # Check if URL already exists
    existing = cls.objects.filter(long_url=long_url).first()
    if existing:
        return existing.short_url
        
    # Handle custom alias
    if custom_alias:
        if cls.objects.filter(short_url=custom_alias).exists():
            raise ValueError("Custom alias already in use")
        
        url_obj = cls(long_url=long_url, short_url=custom_alias)
        url_obj.save()
        return custom_alias
    
    # Generate a short URL using Base62 encoding of the ID
    # First, we need to save an object to get an ID
    url_obj = cls(long_url=long_url, short_url="temp")
    url_obj.save()
    
    # Now encode the ID
    short_url = Base62.encode(url_obj.id + 10000)  # Add offset to make URLs longer
    
    # Update the object with the actual short URL
    url_obj.short_url = short_url
    url_obj.save()
    
    return short_url
```

## Database Design

For a production system, we'd use a database instead of in-memory storage:

```python
import sqlite3
import hashlib
import time

class URLShortenerDB:
    def __init__(self, db_path='url_shortener.db'):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.setup_db()
    
    def setup_db(self):
        # Create tables if they don't exist
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            short_url TEXT UNIQUE,
            long_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS clicks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            short_url TEXT,
            clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ip_address TEXT,
            user_agent TEXT,
            FOREIGN KEY (short_url) REFERENCES urls(short_url)
        )
        ''')
        
        self.conn.commit()
    
    def generate_short_url(self, long_url, custom_alias=None):
        # Check if URL already exists
        self.cursor.execute('SELECT short_url FROM urls WHERE long_url = ?', (long_url,))
        result = self.cursor.fetchone()
        
        if result:
            return result[0]
        
        # Handle custom alias
        if custom_alias:
            self.cursor.execute('SELECT id FROM urls WHERE short_url = ?', (custom_alias,))
            if self.cursor.fetchone():
                raise ValueError("Custom alias already in use")
            
            short_url = custom_alias
        else:
            # Generate a short URL using MD5 hash
            url_hash = hashlib.md5(long_url.encode()).hexdigest()[:6]
            
            # Handle collisions
            counter = 0
            short_url = url_hash
            
            while True:
                self.cursor.execute('SELECT id FROM urls WHERE short_url = ?', (short_url,))
                if not self.cursor.fetchone():
                    break
                
                counter += 1
                short_url = url_hash + str(counter)
        
        # Store in database
        self.cursor.execute(
            'INSERT INTO urls (short_url, long_url) VALUES (?, ?)',
            (short_url, long_url)
        )
        self.conn.commit()
        
        return short_url
    
    def get_long_url(self, short_url, request_info=None):
        self.cursor.execute('SELECT long_url FROM urls WHERE short_url = ?', (short_url,))
        result = self.cursor.fetchone()
        
        if result:
            # Record click analytics
            if request_info:
                self.cursor.execute(
                    'INSERT INTO clicks (short_url, ip_address, user_agent) VALUES (?, ?, ?)',
                    (short_url, request_info.get('ip'), request_info.get('user_agent'))
                )
                self.conn.commit()
            
            return result[0]
        
        raise ValueError("Short URL not found")
    
    def get_analytics(self, short_url):
        # Check if URL exists
        self.cursor.execute('SELECT id FROM urls WHERE short_url = ?', (short_url,))
        if not self.cursor.fetchone():
            raise ValueError("Short URL not found")
        
        # Get total clicks
        self.cursor.execute('SELECT COUNT(*) FROM clicks WHERE short_url = ?', (short_url,))
        total_clicks = self.cursor.fetchone()[0]
        
        # Get recent clicks
        self.cursor.execute(
            'SELECT clicked_at, ip_address, user_agent FROM clicks WHERE short_url = ? ORDER BY clicked_at DESC LIMIT 10',
            (short_url,)
        )
        recent_clicks = [{"time": row[0], "ip": row[1], "agent": row[2]} for row in self.cursor.fetchall()]
        
        return {
            "total_clicks": total_clicks,
            "recent_clicks": recent_clicks
        }
    
    def close(self):
        self.conn.close()
```

## Potential Interview Questions

### Core Functionality Questions

1. **How would you generate a unique short URL for a given long URL?**
   - *Key points:* Hash function vs. Base62 encoding, collision handling strategies, counter vs. random generation

2. **How would you handle the case when two different users want the same custom alias?**
   - *Key points:* First-come-first-serve basis, error handling, alternative suggestions

3. **What should happen when a user accesses a short URL?**
   - *Key points:* 301 vs. 302 redirects, analytics tracking, error handling for non-existent URLs

4. **How would you prevent the same long URL from generating multiple short URLs?**
   - *Key points:* Check existing mappings, database indexing, efficient lookup

### Database Design Questions

5. **What would be your database schema for this service?**
   - *Key points:* Tables structure, index optimization, relationships between entities

6. **Would you use SQL or NoSQL for this application and why?**
   - *Key points:* Read/write patterns, scalability needs, consistency requirements

7. **How would you handle database sharding for a very large URL shortener service?**
   - *Key points:* Horizontal scaling, consistent hashing, data partitioning strategies

### Scalability and Performance Questions

8. **How would you scale this service to handle millions of URLs?**
   - *Key points:* Load balancing, caching, database optimization, microservices architecture

9. **What would be your caching strategy for this service?**
   - *Key points:* Redis/Memcached, cache eviction policies, cache invalidation strategies

10. **How would you handle the case when the service becomes very popular and needs to scale quickly?**
   - *Key points:* Auto-scaling, cloud services, performance monitoring, capacity planning

### Security and Edge Cases

11. **How would you prevent abuse of the service (e.g., spammers creating too many short URLs)?**
   - *Key points:* Rate limiting, captcha, user authentication, monitoring systems

12. **How would you handle malicious URLs or prevent your service from being used for phishing?**
   - *Key points:* URL scanning, blacklisting, user reporting mechanisms, regular audits

13. **How would you ensure the privacy of users who use your URL shortener?**
   - *Key points:* Data encryption, access controls, retention policies, compliance with regulations

### Analytics and Extensions

14. **How would you implement URL analytics (e.g., tracking clicks, geographic distribution)?**
   - *Key points:* Click tracking, data storage, aggregation strategies, real-time analytics

15. **How would you implement URL expiration or self-destructing URLs?**
   - *Key points:* TTL (Time To Live), cron jobs, cleanup strategies, user controls

### System Design Extensions

16. **How would you integrate this URL shortener with other services like social media platforms?**
   - *Key points:* APIs, webhooks, sharing features, metadata handling

17. **Would you implement any additional features to make your URL shortener stand out?**
   - *Key points:* QR code generation, link preview, custom domains, link management tools

## Additional Advanced Topics

### Availability and Reliability

18. **How would you ensure high availability of your URL shortener service?**
   - *Key points:* Multiple data centers, failover mechanisms, redundancy, disaster recovery

19. **What would be your monitoring strategy for this service?**
   - *Key points:* Health checks, error rates, latency tracking, alerting systems

### Testing and Quality Assurance

20. **How would you test your URL shortener implementation?**
   - *Key points:* Unit tests, integration tests, load testing, security testing

21. **What would be your deployment strategy for rolling out updates?**
   - *Key points:* CI/CD pipeline, blue-green deployment, canary releases, rollback capabilities

### Project Requirements and Trade-offs

22. **What are the key metrics you would use to measure the success of this URL shortener?**
   - *Key points:* Response time, availability, error rates, user adoption, conversion rates

23. **What are the trade-offs you made in your design and why?**
   - *Key points:* Complexity vs. performance, storage vs. computing, consistency vs. availability
