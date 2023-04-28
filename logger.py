from datetime import datetime, timedelta
from dateutil.parser import parse
import json
import re
from os.path import exists

""" 
Slices raw login input data into usable strings
    returns an array of:
    username of TYPE string
    date of TYPE datetime.datetime
    ipAddress of TYPE string
"""
def sliceLogin(line, verbose):
    date = parse(line[1:23])
    username = line.rsplit(']', 3)
    username = username[2].rsplit('[', 1)
    ipAddress = username[1].rsplit(':', 1)
    ipAddress = ipAddress[0][1:]
    username = username[0][2:]
    if verbose:
        print("\nLOGIN:")
        print(f"date: {date}")
        print(f"username: {username}")
        print(f"ipAddress {ipAddress}")

    return[username, date, ipAddress]


""" 
Slices raw logout input data into usable strings
    returns an array of:
    username of TYPE string
    date of TYPE datetime.datetime
"""
def sliceLogout(line, verbose):
    date = parse(line[1:23])
    username = line.rsplit(']', 3)
    username = username[3].rsplit('[', 1)
    username = username[0].rsplit(' ', 3)
    username = username[0][2:]

    if verbose:
        print("\nLOGOUT:")
        print(f"date: {date}")
        print(f"username: {username}")

    return[username, date]


""" 
Support function which checks if the player dictionary is initialized with username, totalLogins, totalPlaytime, lastSeen, and totalLogouts. 
Initializes them if not.
"""
def checkIfInPlayerDict(username, playerDict):
    if not username in playerDict:
        playerDict[username] = dict()
    if not "totalLogins" in playerDict[username]:
        playerDict[username]["totalLogins"] = 0
    if not "totalLogouts" in playerDict[username]:
        playerDict[username]["totalLogouts"] = 0
    if not "totalPlaytime" in playerDict[username]:
        playerDict[username]["totalPlaytime"] = [0, 0, 0, 0]
    if not "lastSeen" in playerDict[username]:
        playerDict[username]["lastSeen"] = "1900-12-30T00:00:00.000000"
    if not "ipAddresses" in playerDict[username]:
        playerDict[username]["ipAddresses"] = []


""" 
Support function which checks if the log dictionary is initialized with username.
Adds them if not.
"""
def checkIfInLogDict(username, logDict):
    if not username in logDict:
        logDict[username] = dict()


"""
    Looks through latest.txt log file for relevant lines, then sends them to be sliced.
"""
def logParser(logDict, playerDict, verbose = False):
    i = 0
    logouts = []
    logins = []

    #Open and read data from latest.txt
    log = open('latest.txt', encoding="utf-8")
    data = log.read()
    log.close()
    
    #Create lists of all instances of connecting and disconnecting.
    logoutFullList = re.findall(".* connection: .*", data)
    loginFullList = re.findall(".* logged in .*", data)

    #Sends each logout instance to be sliced for the relevant information.
    for line in logoutFullList:
        logouts.append(sliceLogout(line, verbose))
        username = logouts[i][0]
        dateISO = logouts[i][1].isoformat()
        
        checkIfInPlayerDict(username, playerDict)
        checkIfInLogDict(username, logDict)

        logDict[username][dateISO] = dict()
        logDict[username][dateISO]["date"] = logouts[i][1]

        logDict[username][dateISO]["logType"] = "logout"

        i += 1

    i = 0

    #Sends each login instance to be sliced for the relevant information.
    for line in loginFullList:
        logins.append(sliceLogin(line, verbose))
        username = logins[i][0]
        dateISO = logins[i][1].isoformat()

        checkIfInPlayerDict(username, playerDict)
        checkIfInLogDict(username, logDict)

        logDict[username][dateISO] = dict()
        logDict[username][dateISO]["date"] = logins[i][1]
        logDict[username][dateISO]["ipAddress"] = logins[i][2]

        #Add the IP to playerDict if none exist
        if playerDict[username]["ipAddresses"] == []:
            playerDict[username]["ipAddresses"].append(logins[i][2])

        #Add the IP to playerDict if it is not yet recorded.
        if logins[i][2] not in playerDict[username]["ipAddresses"]:
            playerDict[username]["ipAddresses"].append(logins[i][2])

        logDict[username][dateISO]["logType"] = "login"

        i += 1

"""
    Support function which rounds the input time to the nearest 30 minutes in the future.
"""
def hour_rounder(time):
    #If minutes are less than 30, set them to 30.
    if time.minute <= 30:
        return time.replace(second=0, microsecond=0, minute=30, hour=time.hour)
    #if minutes are greater than 30 set them to 0 and add one to the hour.
    elif time.minute > 30:
        return (time.replace(second=0, microsecond=0, minute=0, hour=time.hour)
               +timedelta(hours=1))
    else:
        print("Invalid minute timestamp")

"""
    Calculates the total time played by <username> player. 
"""
def timeMath(username, logoutTime, playerDict):
    delta = parse(logoutTime) - parse(playerDict[username]['lastSeen'])
    times = str(delta).rsplit(':', 3)

    #Add Seconds
    playerDict[username]["totalPlaytime"][3] = playerDict[username]["totalPlaytime"][3] + int(round(float(times[2])))
    while playerDict[username]["totalPlaytime"][3] >= 60:
        playerDict[username]["totalPlaytime"][3] -= 60
        playerDict[username]["totalPlaytime"][2] += 1

    #Add minutes
    playerDict[username]["totalPlaytime"][2] = playerDict[username]["totalPlaytime"][2] + int(times[1])
    while playerDict[username]["totalPlaytime"][2] >= 60:
        playerDict[username]["totalPlaytime"][2] -= 60
        playerDict[username]["totalPlaytime"][1] += 1
    
    #Add Hours
    playerDict[username]["totalPlaytime"][1] = playerDict[username]["totalPlaytime"][1] + int(times[0])
    while playerDict[username]["totalPlaytime"][1] >= 24:
        playerDict[username]["totalPlaytime"][1] -= 24
        playerDict[username]["totalPlaytime"][0] += 1


"""
    Writes the playerDict to file.
"""
def writeToFile(playerDict, file):
    print(f"Writing data to file {file}")
    with open(file, 'w') as fp:
        json.dump(playerDict, indent=4, sort_keys=True, default=str, fp=fp)

    fp.close()


"""
    Writes the playerDict from file.
"""
def readFromFile():
    file = open('player_stats.json', 'r')

    return json.load(file)


"""
    Calculates totalTimePlayed and lastSeen
"""
def calcTimePlayed(logDict, playerDict, verbose = False):
    for username in logDict:
        print(f"Compiling data for {username}")
        for log in sorted(logDict[username]):
            if playerDict[username]["lastSeen"] >= log:
                if verbose:
                    print("Skipping old entry.")
                continue

            if logDict[username][log]["logType"] == "logout":
                playerDict[username]["totalLogouts"] += 1
            elif logDict[username][log]["logType"] == "login":
                playerDict[username]["totalLogins"] += 1
            else:
                print(f"Invalid logType: {logDict[username][log]['logType']}")

            #This means there are two logins in a row, so we add a fake logout one second from the previous login.
            if int(playerDict[username]["totalLogins"]) >= int(playerDict[username]["totalLogouts"]) + 2:
                date = playerDict[username]['lastSeen']
                fresh_logout = parse(date)+timedelta(minutes=30)

                #Make sure the fake logout is before the next login.
                while(fresh_logout > parse(log)):
                    fresh_logout = fresh_logout - timedelta(minutes=1)

                #Make sure the fake logout is after the previous login.
                while(fresh_logout < parse(date)):
                    fresh_logout = fresh_logout + timedelta(seconds=1)

                dateISO = fresh_logout.isoformat()
                logDict[username][dateISO] = dict()
                logDict[username][dateISO]["date"] = fresh_logout
                logDict[username][dateISO]["logType"] = "logout"
                playerDict[username]["totalLogouts"] += 1
                if verbose:
                    print(f"Previous login:    {playerDict[username]['lastSeen']}")
                    print(f"Fake logout added: {dateISO}")
                    print(f"Next login:        {log}")

                #Update values for totalPlaytime
                timeMath(username, dateISO, playerDict)
            else:
                if logDict[username][log]["logType"] == "logout":
                    timeMath(username, log, playerDict)
                    if verbose:
                        print(f"{username}'s Total Playtime is: {str(playerDict[username]['totalPlaytime'])}")

            #Adds a human readable playtime stat
            playtime = playerDict[username]['totalPlaytime']
            playerDict[username]["totalPlaytimeHR"] = f"{playtime[0]} Days, {playtime[1]} Hours, {playtime[2]} Minutes, {playtime[3]} Seconds"

            #LastSeen calculations
            if log > playerDict[username]["lastSeen"]:
                if verbose:
                    print(f"Updating Log from {playerDict[username]['lastSeen']} to {log}")
                playerDict[username]["lastSeen"] = log


def main():
    outputFile = "player_stats.json"
    logDict = dict()
    playerDict = dict()
    
    if exists(outputFile):
        playerDict = readFromFile()
    else:
        playerDict = dict()

    logParser(logDict, playerDict,  verbose = False)

    calcTimePlayed(logDict, playerDict)

    writeToFile(playerDict, outputFile)

    print("Complete! Check out player_stats.json for the data.")


if __name__ == "__main__":
    main()