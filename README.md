resn
====
resn (REdis Social Network) is a simple library to create social networks. It provides a backend for data models using Redis, supporting friends, followers, updates and a news feed out of the box. You can use it with any web framework like Django, Flask, Pylons etc. For examples see the file **tests.py**. 

Requires:
*Latest version of [redis-py](http://github.com/andymccurdy/redis-py)
*Latest version of [redis_wrap](http://github.com/amix/redis_wrap)

Author: Vivek Narayanan <mail@vivekn.co.cc> 
License: BSD, see LICENSE for more info.

Installation
====
First install redis_py and redis_wrap if you haven't already
    $ easy_install redis
    $ easy_install resis_wrap

Then install resn
    $ easy_install resn


Setting up
====
To use resn, import the module resn and add this to the beginning of the file.
    from resn import *
    setup_system('default', host, port) # host and port of your redis server, default is localhost:6379

There are a couple of other settings you might want to change.
    resn_settings['Feed Size'] = 100 # default value = 1000,  No of messages in a user's feed.
    resn_settings['Token Validity'] = 72 * 3600 # This is the default value in seconds



API Reference
====

Users and Friends
------
'''' python
	create_user(id_attr, **kwargs):
	    """
	    Creates a new user with attributes specified as keyword arguments

	    'id_attr' is the name of the attribute that will uniquely identify the user.
	    """
	   
	get_numeric_user_id(username)

	delete_user(user):
	    """ Deletes the user and removes all friendships """
	   
	get_user_by_id(user_id):
	    """Returns an editable dictionary like wrapper of a user by numeric id"""
	    
	get_user(user):
	    """
	    Returns an editable dictionary like wrapper based on the attribute set in 'id_attr'
	    """
	  
	create_connection_by_ids(user1, user2):
	    """Creates a 'friendship' between two users. Uses internal numeric ids"""
	   

	delete_connection_by_ids(user1, user2):
	    """Deletes a 'friendship' between two users. Uses internal numeric ids"""
	    

	create_connection(user1, user2):
	    """Creates a 'friendship' between two users, parameters are the values of the 'id_attr' set in 'create_user'"""
	   
	    
	delete_connection(user1, user2):
	    """Deletes a 'friendship' between two users, parameters are the values of the 'id_attr' set in 'create_user'"""
	  
	get_friend_list(user):
	    """Returns a list of the user's friends"""
 
''''
Followers and Following
----
'''' python
	follow_by_ids(follower, followee):
	    """Creates an asymmetric connection between two users. Uses internal numeric ids"""

	follow(follower, followee):
	    """Creates an asymmetric connection between two users. """


	unfollow_by_ids(follower, followee):
	    """Deletes an asymmetric connection between two users. Uses internal numeric ids"""

	    
	unfollow(follower, followee):
	    """Deletes an asymmetric connection between two users. """


	get_followers_list(user):
	    """Returns a list of the user's followers"""
	  
	get_following_list(user):
	    """Returns a list of the users the user is following"""
''''
Updates and Feed
----


'''' python

	new_update(username, **update):
	    """Creates a new update object and pushes the update to the feeds of the user's friends and followers."""
	  
	    
	delete_update(update_id):
	    """Deletes a particular update"""
	    

	get_updates_from_list(feed):
	    """ Retrieve updates from their ids """
	   

	get_feed(username, limit = 1000):
	    """Returns the feed containing updates by friends"""
	   

	get_user_updates(username, limit = 1000):
	    """Returns a list of updates by the user. Useful for generating a user profile."""

''''


Authentication
----

'''' python
	check_password(username, password, password_field = 'password'):
	    """
	    password_field is the name of the field in 'create_user' that represents the password.
	    It is advisable to store and check against a hash of the password rather than the password itself.
	    """


	login_user(username):
	    """Call this function after check_password passes. It generates an auth token that can be stored in a cookie to store a user session."""
	    token = generate_auth_token()"""
	   

	logout_user(username):
	    """Clears the auth tokens."""
	    
	validate_token(token):
	    """ Validates the token stored in a cookie """
''''

Future
====
Support for integrating with Facebook and Twitter APIs is planned.
