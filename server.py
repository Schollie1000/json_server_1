
import socket
import os
from _thread import *
import json
import pickle
import random

ServerSocket = socket.socket()
host = '127.0.0.1'
port = 1233
ThreadCount = 0

def check_value(data,subtopic, val):
    return any(player[subtopic]==val for player in data)

def player_new(playername,adress,json_messages):
    print("entered Playername was "+playername)
    reply = ''
    if check_value(json_messages['player'],'name',playername):
        reply = 'Error: player allready exists'
    else:
        listofquestions = []
        for run in json_messages['Question']:
            listofquestions.append(run['id'])
        json_player = {'name': playername, 'score':0, 'secret':adress[0], 'qid':0, 'not_answered':listofquestions}
        json_messages['player'].append(json_player)
        reply = 'player was created'
    
    return reply

def player_question(playername,adress,json_messages):
    print("entered Playername was "+playername)
    reply = ''
    if check_value(json_messages['player'],'name',playername):
        print("assign func "+playername)
        for run in json_messages['player']:
            if run['name'] == playername:
                if run["qid"] == 0:
                    print("player has no question assigned")
                    qnum = random.choice(run["not_answered"])
                    run["qid"] = qnum
                    reply = json_messages['Question'][qnum-1]["text"]
                else:
                    print("player has allready a quesion assigned")
                    reply = "player has allready a quesion assigned "+ json_messages['Question'][run["qid"]-1]["text"]   
        
    else:
        reply = 'Error: player does not exist'
    return reply

def player_answer(playername,answer,adress,json_messages):
    print("entered Playername was "+playername+" answer was ",answer)
    reply = ""
    if check_value(json_messages['player'],'name',playername):
        for run in json_messages['player']:
            if run['name'] == playername:
                if run['secret']!=adress[0]:
                    print("wrong ip adress")
                    reply(" ip adress wrong, are you cheating ? ")
                elif run["qid"] == 0:
                    print("player has no question assigned")
                    reply = " no question assigned "
                else:
                    qnum = run["qid"] 
                    answer_correct = json_messages['Question'][qnum-1]["answer"]
                    if answer == answer_correct:
                        print("answer was correct ")
                        reply = "correct, congratulations!! Plese request a new Question"
                        run["score"] = run["score"] + 1
                        run["not_answered"].remove(run["qid"])
                        run["qid"] = 0
                    else:
                        print("answer was wrong")
                        reply = " wrong!  "+ json_messages['Question'][qnum-1]["text"]
    else:
        reply(" name wrong, are you cheating ? ")
    return reply    


def player_stepback(playername,adress,json_messages):
    print("entered Playername was "+playername)
    reply = ''
    if check_value(json_messages['player'],'name',playername):
        print("assign func "+playername)
        for run in json_messages['player']:
            if run['name'] == playername:
                if run['secret']!=adress[0]:
                    print("wrong ip adress")
                    reply(" ip adress wrong, are you cheating ? ")
                else:
                    run["qid"] = 0
                    reply(" stepped back from question, please get new one ")
    else:
        reply(" name wrong, are you cheating ? ")
    return reply

def leaderboard(json_messages):
    player_dict = {}
    
    for pl in json_messages["player"]:
        player_dict[pl["name"]]= pl["score"]
    return dict(sorted(player_dict.items(), key=lambda item: item[1], reverse=True))

def threaded_client(connection,address):
    json_messages = json.load(open("messages.json"))

    connection.send(str.encode('Welcome to the Quiz Server'))

    try:
        data = connection.recv(2048)
        msgfromclient = pickle.loads(data)
        msgtoclient = ''
        extrastring = ''
        print(msgfromclient,address)
        try:
            if check_value(json_messages['Message'],'id',msgfromclient['cmd']):
                print("cmd good")
                
                for msg in json_messages['Message']:
                    
                    if msg['id'] == msgfromclient['cmd']:
                        
                        if msg['id'] == 'newplayer':
                            extrastring = player_new(msgfromclient['name'],address,json_messages)
                        
                        elif msg['id'] == 'leaderboard':
                            print("cmd leader")
                            extrastring = str(leaderboard(json_messages))
                            print(extrastring)
                        
                        elif msg['id'] == 'requestquestion':
                            extrastring = player_question(msgfromclient['name'],address,json_messages)
                            print("assigning question to ",msgfromclient['name'])
                        
                        elif msg['id'] == 'answer':
                            extrastring = player_answer(msgfromclient['name'],msgfromclient['answer'],address,json_messages)
                            print("assigning question to ",msgfromclient['name'])
                        elif msg['id'] == 'stepback':
                            (msgfromclient['name'],address,json_messages)
                        
                        msgtoclient = msg['text']+'  '+extrastring
            else:
                print("cmd fault")
                msgtoclient = 'no known cmd, try {"cmd": "help"}'
            print("msg to client : "+msgtoclient)
            connection.send(str.encode(msgtoclient))
            connection.close()
        except:
            print("exept 1")
            connection.send(str.encode('Server close connection due notcorrect json'))
            connection.close()                
        #connection.sendall(str.encode(reply))
    except:
        connection.send(str.encode('Server close connection due 2'))
        connection.close()
    
    json_object = json.dumps(json_messages, indent=4)    
    with open("messages.json", "w") as outfile:
        outfile.write(str(json_object))
    print('ending Thread')
    #ThreadCount -= 1
    
def main():
    global json_messages
    filename = os.path.basename(__file__)		
    print("start "+filename)
    
    print("load cmds ")
    json_messages = json.load(open("messages.json"))
    #print(json_messages)
    try:
        ServerSocket.bind((host, port))
    except socket.error as e:
        print(str(e))

    print('Waitiing for a Connection..')
    ServerSocket.listen(5)

    while True:
        Client, address = ServerSocket.accept()
        print('Connected to: ' + address[0] + ':' + str(address[1]))
        start_new_thread(threaded_client, (Client,address))
        #ThreadCount += 1
        #print('Thread cnt : ' + str(ThreadCount))
    ServerSocket.close()




if __name__ == '__main__':
    main()
    print("end Server")