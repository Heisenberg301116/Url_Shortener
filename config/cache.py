from pymemcache.client.base import Client
import os


# memcache_host = "localhost" # to run locally, uncomment
# memcache_port = 11211

memcache_host = os.environ.get('MEMCACHE_HOST', "localhost")
memcache_port = int(os.environ.get('MEMCACHE_PORT', 11211))

# Create a client to connect to Memcached
cached_obj = Client((memcache_host, memcache_port))