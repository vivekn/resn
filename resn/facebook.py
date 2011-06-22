"""
resn - Facebook interface
-------------------------
This module provides some basic features to help interface between your application and Facebook, 
to use these functions you need to obtain an access token using Facebook's oAuth process.

Please see http://developers.facebook.com/docs/reference/api/ for details on how to obtain the token, or use one of the many 
wrapper libraries to do the same.

"""

from .general import *
from simplejson import loads
from urllib2 import urlopen

def store_token(username, token):
    """ Stores the facebook oAuth token of the user """
    user = get_numeric_user_id(username)
    get_redis().set("users.%s.facebook" % user, token)

def get_token(username, token):
    """ Gets the token for the user, already stored in the database """
    user = get_numeric_user_id(username)
    return get_redis().get("users.%s.facebook" % user) or False

def _get_uid(username):
    """ Return the facebook uid of the user """
    token = get_token(username)
    data = loads(urlopen("https://graph.facebook.com/me/?access_token=%s&fields=id" % token))
    return data['id'] or ''

def _get_friend_uids(username):
    """ Return a list of UIDs of the user's facebook friends """
    token = get_token(username)
    data = loads(urlopen("https://graph.facebook.com/me/friends/?access_token=%s&fields=id" % token))
    result = []
    for friend in data['data']:
        result.append(friend['id'])
    return result    

def store_uid(username):
    """ Store the facebook uid of the user """
    uid = _get_uid(username)
    if uid:
        user = get_numeric_user_id(username)
        get_redis().hsetnx("users.%s" % user, 'facebook', uid)
        get_redis().setnx("facebook.%s" % uid, user)
        return True
    return False
    
def sync_friends(username):
    """ Syncs the user's friends with his/her facebook friends """
    user = get_numeric_user_id(username)
    friends = get_set("users.%s.friends" % user)
    for friend in _get_friend_uids(username):
        friend_id = get_redis().get("facebook.%s" % friend)
        if friend_id:
            friends.add(friend_id)
            
    

