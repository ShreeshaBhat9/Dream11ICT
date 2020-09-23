import requests
import json
from queue import Queue

with open('TeamIds.json', 'r') as openfile: 
    teamIds = json.load(openfile)

def convertHyphenToInt(hyphen):
    if hyphen == '-':
        return 0
    return hyphen

def getData(teamName):
    url = "https://www.fotmob.com/teams?id=" + str(teamIds[teamName]) + "&type=team"

    try:
        #Includes fixtures and results
        teamFixtures = requests.get(url = url).json()["fixtures"]
    except requests.exceptions.ConnectionError:
        print('Connection refused to get fixtures')

    lastFiveResults = Queue(maxsize = 5)

    for game in teamFixtures:
        if game["notStarted"]:
            break
        if lastFiveResults.full():
            lastFiveResults.get()
        lastFiveResults.put(game["id"])

    playerData = dict()

    url = "https://www.fotmob.com/matchDetails?matchId="

    print('\nResults\n-------\n')
    while not lastFiveResults.empty():
        URL = url + str(lastFiveResults.get())
        try:
            teams = requests.get(url = URL).json()["content"]["lineup"]
            if teams:
                teams =  teams["lineup"]
            else:
                continue
            if "stats" not in teams[0]["players"][0][0]:
                continue
        except requests.exceptions.ConnectionError:
            print('Connection refused to get game')

        if teams[0]["teamId"] == teamIds[teamName]:
            index = 0
            print("vs ",teams[1]["teamName"])
        else:
            index = 1
            print("vs ",teams[0]["teamName"])
        for position in teams[index]["players"]:
            for player in position:
                addStats(playerData,player,True)
        for player in teams[index]["bench"]:
            addStats(playerData,player,False)
    return playerData

def calculateIndex(playerData):
    for id in playerData:
        if "saves" in playerData[id]:
            index = playerData[id]["saves"]*8 + playerData[id]["passes"]*0.2 + playerData[id]["tackles"]*4 + playerData[id]["interceptions"]*4 + playerData[id]["clearances"]*2              
        else:
            index = playerData[id]["shotsOnTarget"]*10 + playerData[id]["chancesCreated"]*6 + playerData[id]["passes"]*0.2 + playerData[id]["tackles"]*4 + playerData[id]["interceptions"]*4 + playerData[id]["blockedShots"]*4 + playerData[id]["clearances"]*2  
        if playerData[id]["totalMinutes"] != 0:
            playerData[id]["pointsPer90"] = index*90/playerData[id]["totalMinutes"]
        else:
            playerData[id]["pointsPer90"] = 0

def addStats(playerData, player, starting):
    if "stats" not in player:
        return
    if player["id"] not in playerData:
        gameStats = dict()
        gameStats["name"] = player["name"]
        gameStats["totalMinutes"] = convertHyphenToInt(player["stats"]["0"]["Minutes played"])
        if starting:
            gameStats["starts"] = 1
            gameStats["startMinutes"] = gameStats["totalMinutes"]
        else:
            gameStats["starts"] = 0
            gameStats["startMinutes"] = 0
        gameStats["passes"] = convertHyphenToInt(player["stats"]["2"]["Accurate passes"])
        gameStats["interceptions"] = convertHyphenToInt(player["stats"]["3"]["Interceptions"])
        gameStats["clearances"] = convertHyphenToInt(player["stats"]["3"]["Clearances"])
        gameStats["tackles"] = convertHyphenToInt(player["stats"]["3"]["Tackles succeeded"])
        if player["role"] == "Keeper":
            gameStats["saves"] = convertHyphenToInt(player["stats"]["0"]["Saves"])
        else:
            gameStats["blockedShots"] = convertHyphenToInt(player["stats"]["1"]["Blocked shots"])
            gameStats["shotsOnTarget"] = convertHyphenToInt(player["stats"]["1"]["Shot on target"])
            gameStats["chancesCreated"] = convertHyphenToInt(player["stats"]["2"]["Key passes"])
        playerData[player["id"]] = gameStats
    else:
        playerData[player["id"]]["totalMinutes"] += convertHyphenToInt(player["stats"]["0"]["Minutes played"])
        if starting:
            playerData[player["id"]]["starts"] += 1
            playerData[player["id"]]["startMinutes"] += convertHyphenToInt(player["stats"]["0"]["Minutes played"])
        playerData[player["id"]]["passes"] += convertHyphenToInt(player["stats"]["2"]["Accurate passes"])
        playerData[player["id"]]["interceptions"] += convertHyphenToInt(player["stats"]["3"]["Interceptions"])
        playerData[player["id"]]["clearances"] += convertHyphenToInt(player["stats"]["3"]["Clearances"])
        playerData[player["id"]]["tackles"] += convertHyphenToInt(player["stats"]["3"]["Tackles succeeded"])
        if player["role"] == "Keeper":
            playerData[player["id"]]["saves"] += convertHyphenToInt(player["stats"]["0"]["Saves"])
        else:
            playerData[player["id"]]["blockedShots"] += convertHyphenToInt(player["stats"]["1"]["Blocked shots"])
            playerData[player["id"]]["shotsOnTarget"] += convertHyphenToInt(player["stats"]["1"]["Shot on target"])
            playerData[player["id"]]["chancesCreated"] += convertHyphenToInt(player["stats"]["2"]["Key passes"])

if __name__ == "__main__":
    print('Enter team name')
    teamName = input()

    playerData = getData(teamName)


    print('\n\n','{0: <25}'.format("Name"), "\t", "Starts", "\t", "Minutes", "\t", "Avg Minutes per Start", "\t", "ICT")
    print('{0: <25}'.format(" ----"), "\t", "------", "\t", "-------", "\t", "---------------------", "\t", "---\n")

    calculateIndex(playerData)

    for player in sorted(playerData.values(), key=lambda k: k['pointsPer90'], reverse=True):
        if player["starts"]==0:
            minPerStart = 0
        else:
            minPerStart = round(player["startMinutes"]/player["starts"], 2)
        print('{0: <25}'.format(player["name"]), "\t", player["starts"], "\t\t", player["totalMinutes"], "\t\t\t", minPerStart ,"\t\t", round(player["pointsPer90"], 2))
                
