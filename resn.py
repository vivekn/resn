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

    'id_attr' is the name of the attribute that will uniquely identify the user.
    """
    get_redis().incr("users.counter")
    ctr = get_redis().get("users.counter")
    user = get_hash("users." + ctr)
    for key in kwargs:
        user[key] = kwargs[key]
   
    if id_attr not in kwargs:
        raise KeyError, "You did not specify any key '%s' in the call to this function." % id_attr
    else:
        get_redis().set("users.id.%s" % kwargs[id_attr], ctr)

def get_user_by_id(user_id):
    """Returns an editable dictionary like wrapper of a user by numeric id"""
    return get_hash('users.' + user_id)

def get_user(user):
    """
    Returns an editable dictionary like wrapper based on the attribute set in 'id_attr'
    """
    return get_hash('users.id.' + user)

def create_connection_by_ids(user1, user2):
    """Creates a 'friendship' between two users. Uses internal numeric ids"""
    u1 = get_set('users.%s.friends' % user1)
    u2 = get_set('users.%s.friends' % user2)
    u1.add(user2)
    u2.add(user1)

def create_connection(user1, user2):
    """Creates a 'friendship' between two users, parameters are the values of the 'id_attr' set in 'create_user'"""
    u1 = get_redis().get('users.id.' + user1)
    u2 = get_redis().get('users.id.' + user2)
    create_connection_by_ids(u1, u2)
