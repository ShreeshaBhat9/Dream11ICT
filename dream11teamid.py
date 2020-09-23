#Update team Ids

import requests
import json

with open('LeagueIds.json', 'r') as openfile: 
    leagueIds = json.load(openfile)

if __name__ == "__main__":
    
    teamIds = dict()

    for leagueName, leagueId in leagueIds.items():
        
        url = "https://www.fotmob.com/leagues?id=" + str(leagueId) + "&type=league"

        try:
            table = requests.get(url = url).json()["tableData"]
        except requests.exceptions.ConnectionError:
            print('Connection refused to get fixtures')

        if table:
            table = table["tables"][0]
        else:
            print('Table not present for ',leagueName)
            continue
        
        if "table" in table:
            table = table["table"]
        else:
            print('Table not present for ',leagueName)
            continue

        print(leagueName,"done")

        for team in table:
            if team["name"] in teamIds:
                print(team["name"], "already exists, current league = ",leagueName)
            else:
                teamIds[team["name"]] = team["id"]

    with open("TeamIds.json", "w") as outfile: 
        outfile.write(json.dumps(teamIds, indent = 4))
    
    print('TeamIds.json updated')