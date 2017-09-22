## example
```python
from flask import session, jsonify
from limit import LimiterRedis
from redis import Redis

redis = Redis.from_url(url="redis://localhost:6379/0")
limiter = LimiterRedis(redis, "test")

def get_cookie():
  return session.get("your_cookie_type")

def callback():
  return jsonify("message"="request drop")


@app.route('/', methods=['GET', 'POST'])
@limiter.limit(get_cookie, "3/10", callback)
def hello_world(anything=None):
  return jsonify("message"="request success")
```
## use
"3/10" =>"3 count per 60 second"
you can rewrite function create_count, get_count, incr_count by Inheritance LimiterMiXin, limit.py provide a redis classic.
