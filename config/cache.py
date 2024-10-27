from pymemcache.client.base import Client

# memcache_host = "memcachedcontainer" # to run in docker, uncomment 
memcache_host = "localhost" # to run locally, uncomment
# memcache_host ='urlcache-memcached.default.svc.cluster.local' # to run in K8s
memcache_port = 11211

# Create a client to connect to Memcached
cached_obj = Client((memcache_host, memcache_port))

# import socket
# from pymemcache.client.hash import HashClient

# # Get IP addresses associated with the host name
# _, _, ips = socket.gethostbyname_ex(memcache_host)

# # Print the obtained IP addresses
# print("IP addresses associated with the host name:")
# for ip in ips:
#     print(ip)

# # Create a list of servers using the obtained IP addresses
# servers = [(ip, 11211) for ip in ips]

# # Print the list of servers
# print("List of servers:")
# for server in servers:
#     print(server)

# # Initialize the HashClient
# cached_obj = HashClient(servers, use_pooling=True)

# # Set a value in the cache
# cached_obj.set('greeting', 'Hello there Friend!')

# # Get the value from the cache
# greeting = cached_obj.get('greeting')

# # Print the retrieved value
# print("Retrieved greeting from the cache:")
# print(greeting)