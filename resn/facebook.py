from .general import *

def store_token(username, token):
    """ Stores the facebook oAuth token of the user """
    user = get_numeric_user_id(username)
    get_redis().set("users.%s.facebook" % user, token)

def _get_uid(username):
    """ Return the facebook uid of the user """
    pass

def _get_friend_uids(username):
    """ Return a list of UIDs of the user's facebook friends """
    pass

def store_uid(username, uid):
    """ Store the facebook uid of the user """
    user = get_numeric_user_id(username)
    _user = get_hash("users.%s" % user)
    _user['facebook'] = uid
    get_redis().set("facebook.%s" % uid, user)
    
def sync_friends(username):
    """ Syncs the user's friends with his/her facebook friends """
    user = get_numeric_user_id(username)
    friends = get_set("users.%s.friends" % user)
    for friend in _get_friend_uids(username):
        friend_id = get_redis().get("facebook.%s" % friend)
        if friend_id:
            friends.add(friend_id)
            
    

