#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#   @autor: beauge_z, jussea_m

import socket
import sys
import os

buff_sz=4096

class player:
    inv=list()
    lvl=1

def moveTo(x, case):
    action = list()
    pos = tst = 0
    caseLen=3
    sz=3
    action.extend(cleanCase(case[pos]))
    for i in range(0, (3 + player.lvl - 1)):
        tst+=(int(caseLen/2) + 1 + i)
        if x >= sz and tst <= len(case):
            action.append('avance')
            pos+=(int(caseLen/2) + 1 + i)
            action.extend(cleanCase(case[pos]))
        caseLen+=2
        sz+=caseLen
    if pos == 0:
        action.append('avance')
        pos+=2
        action.extend(cleanCase(case[pos]))
    if pos < x:
        action.append('droite')
        while pos < x:
            action.append('avance')
            pos+=1
            action.extend(cleanCase(case[pos]))
    if pos > x:
        action.append('gauche')
        while pos > x:
            action.append('avance')
            pos-=1
            action.extend(cleanCase(case[pos]))
    return action

def checkInv(needed):
    for item in needed:
        if item not in player.inv:
            return False
    return True

def cleanCase(case):
    take=list()
    if case:
        for elem in case.split():
            if elem != 'joueur':
                take.append('prend ' + elem)
            if elem != 'nourriture' and elem != 'joueur':
                player.inv.append(elem)
    return take

def checkPlayer(case):
    if player.lvl == 1:
        return True
    nbplayer=0
    ret=0
    while ret != -1:
        ret = case.find('joueur', ret)
        if ret != -1:
            nbplayer+=1
    if (player.lvl == 2 or player.lvl == 3) and nbplayer != 2 :
       serv.send('broadcast lvl' + str(player.lvl))
       print('-->broadcast lvl' + str(player.lvl))
       return False
    if (player.lvl == 4 or player.lvl == 5) and nbplayer != 4 :
       serv.send('broadcast lvl' + str(player.lvl))
       print('-->broadcast lvl' + str(player.lvl))
       return False
    if (player.lvl == 5 or player.lvl == 7) and nbplayer != 6 :
       serv.send('broadcast lvl' + str(player.lvl))
       print('-->broadcast lvl' + str(player.lvl))
       return False
    return True

def getAction(mapseen, mytime):
    action=list()
    needed=list()
    newmap=mapseen.replace("{", "").replace("}", "")
    case=newmap.split(',')
    pos=0
    find=False
    action.clear()
    if player.lvl == 1:
        needed = ['linemate']
    if player.lvl == 2:
        needed = ['linemate', 'deraunere', 'sibur']
    if player.lvl == 3:
        needed = ['linemate', 'linemate', 'sibur', 'phiras', 'phiras']
    if player.lvl == 4:
        needed = ['linemate', 'deraunere', 'sibur', 'sibur', 'phiras']
    i=0
    for i in range(0, len(case)):
        if case[i].find('nourriture') != -1 and not find:
            action = moveTo(i, case)
            mytime+=126
            find=True
    i=0
    for elem in needed:
        for i in range(0, len(case)):
            if case[i].find(elem) != -1 and not find:
                action = moveTo(i, case)
                find=True
    find=False
    mytime-=(7*len(action))
    if (checkInv(needed) and checkPlayer(case[i]) and mytime - (7*len(needed))) > 400:
        action.extend(cleanCase(case[i]))
        for elem in needed:
            action.append('pose ' + elem)
            del player.inv[player.inv.index(elem)]
        action.append('incantation')
        player.lvl+=1
    if not action:
        action.append('droite')
    return action, mytime

def ai(serv, mytime):
    seen=False
    action=list()
    data=''
    while(data != 'mort\n'):
        if seen is False:
            action.clear()
            serv.send(bytes('voir\n', 'utf-8'))
            print('-->voir', flush=True)
            data=serv.recv(buff_sz).decode('utf-8')
            print('<--%s' % data, end="", flush=True)
            action, mytime=getAction(data, mytime)
            seen=True
        elif action:
            serv.send(bytes(action[0] + '\n', 'utf-8'))
            print('-->%s' % action[0], flush=True)
            data=serv.recv(buff_sz).decode('utf-8')
            print('<--%s' % data, end="", flush=True)
            if action[0] == 'incantation':
                data=serv.recv(buff_sz).decode('utf-8')
                print('<--%s' % data, end="", flush=True)
            del action[0]
            if not action:
                seen=False

def firstMsgs(serv, team):
    data=serv.recv(buff_sz).decode('utf-8')
    if (data == 'BIENVENUE\n'):
        print('<--%s' % data, end="", flush=True)
        serv.send(bytes(team + '\n', 'utf-8'))
        print('-->%s' % team, flush=True)
        data=serv.recv(buff_sz).decode('utf-8')
        print('<--%s' % data, end="", flush=True)
        numCl=int(data)
        data=serv.recv(buff_sz).decode('utf-8')
        print('<--%s' % data, end="", flush=True)
        sizeMap = data.split(' ')
        x = int(sizeMap[0])
        y = int(sizeMap[1])
    else:
        raise RuntimeError('Incompatible server. Maybe not a Zappy server?')
    return numCl

def server_connect(team_name, port, host):
    mytime=0
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    numCl = firstMsgs(s, team_name)
    newpid=-1
    if numCl > 0:
        newpid=os.fork()
        if (newpid == 0):
            os.system(' '.join(sys.argv))
            os._exit(0)
    ai(s, mytime)
    if newpid == 0:
        os.waitpid(newpid, 0)
    s.close()

def getArg():
    host='localhost'
    port=''
    team_name=''
    for i in range(1, len(sys.argv)):
        if i % 2 is not 0 and i+1 <= len(sys.argv):
            if sys.argv[i] == '-n':
                team_name=str(sys.argv[i+1])
            elif sys.argv[i] == '-p':
                port=int(sys.argv[i+1])
            elif sys.argv[i] == '-h':
                host=str(sys.argv[i+1])
    return (team_name, port, host)

def chckArg():
    try:
        host='localhost'
        port=''
        team_name=''
        for i in range(1, len(sys.argv)):
            if i % 2 is not 0 and i+1 <= len(sys.argv):
                if sys.argv[i] == '-n':
                    team_name=str(sys.argv[i+1])
                elif sys.argv[i] == '-p':
                    port=int(sys.argv[i+1])
                elif sys.argv[i] == '-h':
                    host=str(sys.argv[i+1])
        if not port or not team_name:
            raise RuntimeError('Client must have a team name and a port specified to run.')
    except ValueError:
        raise RuntimeError('Bad argument type.')
    return True

def main():
    try:
        if len(sys.argv) < 5 or len(sys.argv) > 7:
            print('Usage: %s -n team_name -p port [-h machine_name]' % str(sys.argv[0]), flush=True)
        else:
            if chckArg() is True:
                team_name, port, host = getArg()
                server_connect(team_name, port, host)
        return True
    except Exception as err:
        sys.stderr.write('[\033[1;31mError\033[0m]%s\nProgram is closing.\n' % str(err))
        return False

if __name__ == '__main__':
    sys.exit(main())
