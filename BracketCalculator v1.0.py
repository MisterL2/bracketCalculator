#Bracket calculator algorithm (c) MisterL2 01.03.2019
from itertools import product

class Group:

    def __init__(self,playerList,bestOf): #Assumes Match Win-Loss > MapDifference > MapWins > Head to Head
        self.groupSize=len(playerList)
        self.players = [Player(x) for x in playerList]
        self.matches = generateMatches(self.players) # [Player,otherPlayer,matchPlayed]
        self.bestOf = bestOf
        self.futureResults = set()

    def addResult(self,playerName,otherPlayerName,resultTuple):
        for match in self.matches:
            if playerName in {match[0].name,match[1].name} and otherPlayerName in {match[0].name,match[1].name}:
                match[2]=3 # isPlayed
                player = self.findPlayer(playerName)
                otherPlayer = self.findPlayer(otherPlayerName)
                self.futureResults.add(playerName + " " + str(resultTuple[0]) + "-" + str(resultTuple[1]) + " " + otherPlayerName)
                player.addMatch(otherPlayer.name,resultTuple)
                otherPlayer.addMatch(player.name,(resultTuple[::-1]))
                break

    def findPlayer(self,playerName):
        for player in self.players:
            if player.name==playerName:
                return player
            
    def displayBracket(self,condition=None,show=False):
        sortedPlayers = sorted(self.players,key=scoreToNumber,reverse=True)

        calculateH2H(sortedPlayers) #No output, mutates sortedPlayers. Also calculates the scores of all players
                            
                    
        if condition is not None:
            if not condition(sortedPlayers):
                return False #Doesn't print results if condition is not met
        if show:
            print("=========================================")
            for player in sortedPlayers:
                print("{:^10}:  ({}-{}) ({}-{}) {}".format(player.name,player.matchWins,player.matchLoss,player.mapWins,player.mapLoss,player.getMapScore()))
            for item in self.futureResults:
                print(item)
            print("=========================================")
        
        return True #Condition has been met, or no condition, if execution reaches this point



class Player:

    def __init__(self,name):
        self.name=name
        self.matches=[] #[otherPlayerName,(resultTuple)]
        self.matchWins = 0
        self.matchLoss = 0
        self.mapWins = 0
        self.mapLoss = 0

    def calculateScores(self):
        self.matchWins=self.matchLoss=self.mapWins=self.mapLoss=0 #Very necessary reset
        if not self.matches:
            pass
        else:
            for item in self.matches:
                if item[1][0]>item[1][1]:
                    self.matchWins+=1
                else: #Does not support TIEs
                    self.matchLoss+=1
                self.mapWins+=item[1][0]
                self.mapLoss+=item[1][1]

    def addMatch(self,otherPlayerName,resultTuple):
        
        for match in self.matches: 
            if match[0] == otherPlayerName:
                return #Don't override already existing results
                #break
        
        self.matches.append([otherPlayerName,resultTuple])

    def getMapScore(self):
        return self.mapWins-self.mapLoss


def generateMatches(playerList):
    matches = []
    for player in playerList:
        for otherPlayer in playerList:
            #String alphabetic comparison; ensures that matches only occur once.
            #Also excludes matches against the player themselves
            if player.name > otherPlayer.name: 
                matches.append([player,otherPlayer,False])
    return matches



def generateResults(bestOf):
    possibilities = []
    for i in range((bestOf//2)+2):
        for j in range((bestOf//2)+2):
            if (i+j)<=bestOf and (i>(bestOf//2) or j>(bestOf//2)):
                possibilities.append((i,j))
    return possibilities


def scoreToNumber(player): #H2H is managed seperately
    player.calculateScores()
    return player.matchWins*1000 + player.getMapScore()*20 + player.mapWins



def generateAllPossibilities(group,condition=None,show=False):
    #Recording initial state
    group.futureResults = set()
    matchingCases = 0
    totalCases = 0
    initialState = [player.matches.copy() for player in group.players] #List of lists
    alreadyPlayed = []
    TBD = []
    for match in group.matches:
        if not match[2]:
            TBD.append(match.copy())
        else:
            alreadyPlayed.append(match.copy())

    group.displayBracket()
    #Now begins the brute forcing
    possibleScores = generateResults(group.bestOf)
    for scoresList in product(possibleScores,repeat=len(TBD)):
        for i in range(len(TBD)):
            x = TBD[i][0].name
            y = TBD[i][1].name
            group.addResult(x,y,scoresList[i])
        matchingCases += group.displayBracket(condition,show) #Returns True or False, depending on if the condition is met
        totalCases+=1
        #Reset for next iteration
        resetToInitial(group,initialState,alreadyPlayed,TBD)
    return matchingCases, totalCases


def resetToInitial(group,initialState,alreadyPlayed,TBD):
    for i in range(len(group.players)): #List maintains order
        group.players[i].matches=initialState[i].copy()
    for match in group.matches:
        if match in TBD:
            match[2]=False
    group.futureResults = set()


def calculateH2H(sortedPlayers):
    for i in range(len(sortedPlayers)):
            for j in range(len(sortedPlayers)):
                if i != j and scoreToNumber(sortedPlayers[i]) == scoreToNumber(sortedPlayers[j]):
                    for match in sortedPlayers[i].matches:
                        if match[0]==sortedPlayers[j].name:                            
                            if match[1][0] > match[1][1]:
                                #Higher up = lower index
                                if i > j:
                                    sortedPlayers[i], sortedPlayers[j] = sortedPlayers[j], sortedPlayers[i]
                            else:
                                #Higher up = lower index
                                if i < j:
                                    sortedPlayers[i], sortedPlayers[j] = sortedPlayers[j], sortedPlayers[i]
                            return



def getChances(group,condition=None,show=False):
    a, b =generateAllPossibilities(group,condition,show)
    print (str(a*100/b) + "%")

    

