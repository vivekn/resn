"""
resn is a simple library to create social networks.

Requires:
*Latest version of redis-py
*Latest version of redis_wrap

Author: Vivek Narayanan <mail@vivekn.co.cc> 
License: BSD

"""

from redis_wrap import *

def create_user(**kwargs):
    """Creates a new user with attributes specified as keyword arguments"""
    get_redis().incr("users.counter")
    ctr = get_redis().get("users.counter")
    user = get_hash("users." + ctr)
    for key in kwargs:
        user[key] = kwargs[key]


