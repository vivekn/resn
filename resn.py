"""
resn is a simple library to create social networks.

Requires:
*Latest version of redis-py
*Latest version of redis_wrap

Author: Vivek Narayanan <mail@vivekn.co.cc> 
License: BSD

"""

from redis_wrap import get_redis, get_hash, get_set

def create_user(id_attr, **kwargs):
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
        user['id'] = kwargs[id_attr]

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
    
def new_update(user, **update):
    """Creates a new update object and pushes the update to the feeds of the user's friends and followers.
    The parameter 'user' is the numeric id of the user"""

    get_redis().incr("updates.counter")
    ctr = get_redis().get("updates.counter")
    upd = get_hash("updates." + ctr)
    upd['user'] = user
    for key in update:
        upd = update[key]

    friends = get_set("users.%s.friends" % user)
    for friend in friends:
        get_redis().lpush("users.%s.feed" % friend, ctr)
        get_redis().ltrim("users.%s.feed" % friend, 0, 1000) #TODO: Change hardcoded limit 1000 to a setting.

    get_redis().lpush("users.%s.updates" % user, ctr) #This is useful for maintaining a list of updates by a particular user
    
def delete_update(update_id):
    """Deletes a particular update"""
    get_redis().delete("updates." + update_id)

def get_updates_from_list(feed):
    """ Performs existence checks on updates """
    newfeed = []
    for update in feed:
        if len(update):
            newfeed.append(update)
    return newfeed

def get_feed(user, limit = 1000):
    """Returns the feed containing updates by friends"""
    return get_updates_from_list(get_redis.lrange("users.%s.feed" % user, 0, limit))

def get_user_updates(user, limit = 1000):
    """Returns a list of updates by the user. Useful for generating a user profile."""
    return get_updates_from_list(get_redis.lrange("users.%s.updates" % user, 0, limit))

        
