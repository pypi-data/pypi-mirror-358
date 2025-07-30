# discord.gg/opening | dataopen

## DISCLAIMER:
##      Some features can rate limit your account, use this at your own risk.


```python
import openwrapper
client = openwrapper.Client(token='your_token') # Initialize the client with your token


def get_country():
    country_code = client.get_country()
    if country_code:
        print(f"Country Code: {country_code}")
    else:
        print("Failed to retrieve country code")
get_country()

def get_dms():
    dms = client.get_dms()
    for user_id, username in dms:
        print(f"User ID: {user_id} | Username: {username}")
get_dms()

def get_guilds():
    guilds = client.get_guilds()
    for guild_id, guild_name in guilds:
        print(f"Guild ID: {guild_id} | Guild Name: {guild_name}")
get_guilds()

def get_friends():
    friends = client.get_friends()
    for friend_id, friend_name in friends:
        print(f"Friend ID: {friend_id} | Friend Name: {friend_name}")
get_friends()

def token_lookup():
    profile = client.token_lookup()
    if profile:
        print(f"Username: {profile['username']}")
        print(f"Email: {profile['email']}")
        print(f"Phone: {profile['phone']}")
        print(f"Locale: {profile['locale']}")
    else:
        print("Invalid token")
token_lookup()

def send_message(c,m):
    client.send_message(channel_id=c, message=m)
    print(f"Message sent to channel {c}: {m}")
send_message(c=id, m='Hi star plsssssssss')

def remove_friend(uid):
    client.remove_friend(user_id=uid)
    print(f"Removed friend with User ID: {uid}")
remove_friend(uid=ID)

def set_language(country_code):
    client.set_language(country_code=country_code)
    print(f"Language set to {country_code}")
set_language(country_code='country code') 
            # 'da', 'de', 'en-GB', 'en-US', 'es-ES', 'fr', 'hr', 'it',
            # 'lt', 'hu', 'nl', 'no', 'pl', 'pt-BR', 'ro', 'fi', 'sv-SE',
            # 'vi', 'tr', 'cs', 'el', 'bg', 'ru', 'uk', 'th', 'zh-CN',
            # 'ja', 'ko'

def set_hypesquad(house_id):
    client.set_hypesquad(house_id=house_id)
    print(f"Hypesquad house set to {house_id}")
set_hypesquad(house_id=id) # 1 = bravery, 2 = balance, 3 = brilliance

def block_user(uid):
    client.block_user(user_id=uid)
    print(f"Blocked user with User ID: {uid}")
block_user(uid=ID) # Block a user

client.UnblockUser(UserId=id) # Unblock a user
def unblock_user(uid):
    client.unblock_user(user_id=uid)
    print(f"Unblocked user with User ID: {uid}")
unblock_user(uid=ID) # Unblock a user

def get_messages(channel_id):
    messages = client.get_messages(channel_id=channel_id)
    for msg in messages:
        print(f"Message ID: {msg['message_id']} | Username: {msg['username']} | Content: {msg['content']}")
get_messages(channel_id=ID) # Get messages from a channel
```