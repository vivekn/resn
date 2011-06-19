from redis_wrap import get_redis, get_hash, get_set, setup_system
import random


resn_settings = {
    'Feed Size': 1000, # Maximum number of messages in a user's feed
    'Token Validity': 72 * 3600, # Time in seconds before a token expires.
}



#~~~~Users and Friends~~~~


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

def get_numeric_user_id(username):
    return get_redis().get("users.id.%s" % username)

def delete_user(user):
    """ Deletes the user and removes all friendships """
    friends = get_set("users.%s.friends" % user)
    for friend in friends:
        get_set("users.%s.friends" % friend).remove(user)
    get_redis().delete("users.%s" % user)

def get_user_by_id(user_id):
    """Returns an editable dictionary like wrapper of a user by numeric id"""
    return get_hash('users.' + user_id)

def get_user(user):
    """
    Returns an editable dictionary like wrapper based on the attribute set in 'id_attr'
    """
    return get_hash('users.' + get_numeric_user_id(user))

def create_connection_by_ids(user1, user2):
    """Creates a 'friendship' between two users. Uses internal numeric ids"""
    u1 = get_set('users.%s.friends' % user1)
    u2 = get_set('users.%s.friends' % user2)
    u1.add(user2)
    u2.add(user1)

def delete_connection_by_ids(user1, user2):
    """Deletes a 'friendship' between two users. Uses internal numeric ids"""
    u1 = get_set('users.%s.friends' % user1)
    u2 = get_set('users.%s.friends' % user2)
    u1.remove(user2)
    u2.remove(user1)


def create_connection(user1, user2):
    """Creates a 'friendship' between two users, parameters are the values of the 'id_attr' set in 'create_user'"""
    u1 = get_numeric_user_id(user1)
    u2 = get_numeric_user_id(user2)
    create_connection_by_ids(u1, u2)
    
def delete_connection(user1, user2):
    """Deletes a 'friendship' between two users, parameters are the values of the 'id_attr' set in 'create_user'"""
    u1 = get_numeric_user_id(user1)
    u2 = get_numeric_user_id(user2)
    delete_connection_by_ids(u1, u2)

def extract(iterable):
    return (get_user_by_id(user)['id'] for user in iterable)


def get_friend_list(user):
    """Returns a list of the user's friends"""
    user = get_numeric_user_id(user)
    return extract(get_set("users.%s.friends" % user))

#~~~~Followers and Following~~~~



def follow_by_ids(follower, followee):
    """Creates an asymmetric connection between two users. Uses internal numeric ids"""
    following = get_set("users.%s.following" % follower)
    following.add(followee)
    followers = get_set("users.%s.followers" % followee)
    followers.add(follower)

def follow(follower, followee):
    """Creates an asymmetric connection between two users. """
    fr = get_numeric_user_id(follower)
    fe = get_numeric_user_id(followee)
    follow_by_ids(fr, fe)

def unfollow_by_ids(follower, followee):
    """Deletes an asymmetric connection between two users. Uses internal numeric ids"""
    following = get_set("users.%s.following" % follower)
    following.remove(followee)
    followers = get_set("users.%s.followers" % followee)
    followers.remove(follower)
    
def unfollow(follower, followee):
    """Deletes an asymmetric connection between two users. """
    fr = get_numeric_user_id(follower)
    fe = get_numeric_user_id(followee)
    unfollow_by_ids(fr, fe)

def get_followers_list(user):
    """Returns a list of the user's followers"""
    user = get_numeric_user_id(user)
    return extract(get_set("users.%s.followers" % user))

def get_following_list(user):
    """Returns a list of the users the user is following"""
    user = get_numeric_user_id(user)
    return extract( get_set("users.%s.following" % user) )



#~~~~Updates and Feed~~~~




def new_update(username, **update):
    """Creates a new update object and pushes the update to the feeds of the user's friends and followers."""
    user = get_numeric_user_id(username)

    get_redis().incr("updates.counter")
    ctr = get_redis().get("updates.counter")
    upd = get_hash("updates." + ctr)
    upd['user'] = user
    for key in update:
        upd[key] = update[key]

    friends = get_redis().sunion("users.%s.friends" % user, "users.%s.followers" % user)
    for friend in friends:
        get_redis().lpush("users.%s.feed" % friend, ctr)
        get_redis().ltrim("users.%s.feed" % friend, 0, resn_settings['Feed Size']) 

    get_redis().lpush("users.%s.updates" % user, ctr) #This is useful for maintaining a list of updates by a particular user
    
def delete_update(update_id):
    """Deletes a particular update"""
    get_redis().delete("updates." + update_id)

def get_updates_from_list(feed):
    """ Retrieve updates from their ids """
    newfeed = []
    for item in feed:
        update = get_hash('updates.%s' % item)
        if len(update):
            newfeed.append(update)
    return newfeed

def get_feed(username, limit = resn_settings['Feed Size']):
    """Returns the feed containing updates by friends"""
    user = get_numeric_user_id(username)
    return get_updates_from_list(get_redis().lrange("users.%s.feed" % user, 0, limit))

def get_user_updates(username, limit = resn_settings['Feed Size']):
    """Returns a list of updates by the user. Useful for generating a user profile."""
    user = get_numeric_user_id(username)
    return get_updates_from_list(get_redis().lrange("users.%s.updates" % user, 0, limit))



#~~~~Authentication~~~~



def generate_auth_token():
    return ''.join(random.choice('1234567890abcdef') for i in range(25))

def check_password(username, password, password_field = 'password'):
    """
    password_field is the name of the field in 'create_user' that represents the password.
    It is advisable to store and check against a hash of the password rather than the password itself.
    """
    user = get_hash('users.%s' % get_numeric_user_id(username))
    if not user:
        return False
    return user[password_field] == password

def login_user(username):
    """Call this function after check_password passes. It generates an auth token that can be stored in a cookie to store a user session."""
    token = generate_auth_token()
    user = get_user(username)
    user['auth'] = token
    get_redis().set("auth.%s" % token, str(get_numeric_user_id(username)))
    get_redis().expire("auth.%s" % token, resn_settings['Token Validity']) 
    return token

def logout_user(username):
    """Clears the auth tokens."""
    user = get_user(username)
    token = user['auth']
    get_redis().delete("auth.%s" % token)
    del user['auth'] 

def validate_token(token):
    """ Validates the token stored in a cookie """
    user_id = get_redis().get("auth.%s" % token)
    user = get_hash("users.%s" % user_id)
    if not len(user):
        return False
    return user['auth'] == token
