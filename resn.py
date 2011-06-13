"""
resn is a simple library to create social networks.

Requires:
*Latest version of redis-py
*Latest version of redis_wrap

Author: Vivek Narayanan <mail@vivekn.co.cc> 
License: BSD

"""

from redis_wrap import * 

def create_user(id_attr = None, **kwargs):
    """
    Creates a new user with attributes specified as keyword arguments

    'id_attr' is an optional argument to set the attribute that will uniquely identify a user.
    """
    get_redis().incr("users.counter")
    ctr = get_redis().get("users.counter")
    user = get_hash("users." + ctr)
    for key in kwargs:
        user[key] = kwargs[key]
   
    if id_attr:
        if id_attr not in kwargs:
            raise KeyError, "You did not specify any key '%s'." % id_attr
        else:
            get_redis().set("users.id.%s" % kwargs[id_attr], ctr)

def get_user_by_id(user_id):
    """Returns an editable dictionary like wrapper of a user by numeric id"""
    return get_hash('users.' + user_id)

def get_user(user):
    """
    Requires 'id_attr' to be set when create_user was called.
    Returns an editable dictionary like wrapper based on the attribute set in 'id_attr'
    """
    return get_hash('users.id.' + user)




