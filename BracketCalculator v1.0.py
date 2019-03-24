#Bracket calculator algorithm (c) MisterL2 01.03.2019
from itertools import product

priorities = [lambda p : p.matchWins, lambda p : p.getMapScore(), lambda p : p.mapWins]

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
                match[2]=True # isPlayed
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
        sortedPlayers = sorted(self.players,key=lambda p : scoreToNumber(p,self.players),reverse=True)
                    
        if condition is not None:
            if not condition(sortedPlayers):
                return False #Doesn't print results if condition is not met
        if show:
            print("=========================================")
            for player in sortedPlayers:
                print("{:^10}:  ({}-{}) ({}-{})  {}   {}".format(player.name,player.matchWins,player.matchLoss,player.mapWins,player.mapLoss,player.getMapScore(),f"H2H: {player.h2h}" if player.isTied else ""))
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
        self.h2h = 0
        self.isTied = 0 #becomes True 

    def calculateScores(self):
        self.matchWins=self.matchLoss=self.mapWins=self.mapLoss=0 #Very necessary reset. DO NOT reset H2H or isTied here!
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


def scoreToNumber(player,allPlayers=None): #H2H is managed seperately
    player.calculateScores()
    if allPlayers is not None:
        calculateH2H(allPlayers) #No output, calculates h2h scores for all tied participants
        return calculatePriorities(player) + (player.h2h,) #The "," is cast to tuple
    return calculatePriorities(player)

def calculatePriorities(player):
    global priorities
    resultTuple = ()
    for item in priorities:
        resultTuple += (item(player),) #The "," is cast to tuple
    return resultTuple
    

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
        for otherMatch in TBD:
            if match[0] == otherMatch[0] and match[1] == otherMatch[1]: #Same matchup. Using "match in TBD" doesn't work, because the boolean will be True for the match in group.matches, but False for the one in TBD
                match[2]=False
    group.futureResults = set()


def calculateH2H(players):
    for player in players:
        player.h2h=0 #Important reset BEFORE subsequent calculations
        player.isTied=0
        
    for player1 in players:
        for player2 in players:
            if player1 is player2 or scoreToNumber(player1) != scoreToNumber(player2):
                continue
            for match in player1.matches:
                if match[0] == player2.name:
                    if match[1][0] > match[1][1]:
                        player1.h2h += 1
                    player1.isTied=player2.isTied=True
                    break


def getChances(group,condition=None,show=False):
    a, b =generateAllPossibilities(group,condition,show)
    print (str(a*100/b) + "%")

''' #Example data
group = Group(["a","b","c","d","e"],3)
group.addResult("a","b",(2,1))
group.addResult("a","c",(2,0))
group.addResult("b","c",(1,2))
group.addResult("d","c",(1,2))
group.addResult("b","d",(2,0))
group.addResult("a","d",(2,0))
group.addResult("a","e",(2,0))
group.addResult("d","e",(2,0))
group.addResult("b","e",(2,0))
group.addResult("c","e",(2,1))
'''
