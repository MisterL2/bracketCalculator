# Bracket Calculator
Calculates all possible results of any RR group stage

### Usage:

##### 1. Initialise the group, with a list of players and the best-of-X of the group matches

For example (IEM Katowice Group D, Best of 3): 

```groupD = Group(["Bunny","TY","uThermal","Scarlett","soO","Dear"],3)```

##### 2. Add all matches that have already been played

e.g.
```groupD.addResult("TY","uThermal",(2,1)) ```

##### 3. Call ```getChances(group,condition=None,show=False) ```

e.g.
```getChances(groupD,selector,True) ```
-> Prints out all scenarios where the condition specified in "selector" is met

Alternatively, call it without a condition

```getChances(groupD,show=True) ```

In this case, the probability will always be 100% (obviously). If you, for some reason, want to NOT have the probability displayed at the end of the results list, call ``` generateAllPossibilities(group,condition=None,show=False) ```

------------------------------------------------
### The Selector function
This is the function that is passed as parameter to ```getChances()``` or ```generateAllPossibilities(): ```

It takes a list of players (ordered from first to last place) as parameter and must return a boolean that indicates whether the list matches the condition or not.

For example:
```python
def selector(sortedPlayers):
    for i in range(len(sortedPlayers)):
        if sortedPlayers[i].name == "soO":
            return i==1
```
With this selector, all results are returned where soO is second place in his group (index 1 -> 2nd place, index 0 -> 1st place).
This can be easily modified to i<=2 to check if he achieved top 3, etc.

```python
def selector(sortedPlayers):
    a = 0
    for i in range(3):
        if sortedPlayers[i].name in {"TY","uThermal","Bunny"}:
            a+=1        
    return a==2
```
This returns all results, where exactly 2 players out of "TY" "uThermal" and "Bunny" are in the top 3.
This can also easily be modified to check various other solutions.

--------------------------------------------------------
### Changing Evaluation Order
By default, the program assumes the following Evaluation Order:

1. Match Win-Loss
2. Map Win-Loss
3. Map Wins
4. Head to Head

However, if your tournament has a different Evaluation Order, you can change this easily.
Please note that Head-to-Head scores are excluded from this, they will always be evaluated last.
In order to change this setting, simply change ```priorities``` (a list of lambdas).
By default, it looks like this:
```python
priorities = [lambda p : p.matchWins, lambda p : p.getMapScore(), lambda p : p.mapWins]
```
If you want Map Win-Loss to count before Match Win-Loss, for example, you simply swap them:
```python
priorities = [lambda p : p.getMapScore(), lambda p : p.matchWins, lambda p : p.mapWins]
```
If you want have "Match Win-Loss -> Map Win-Loss -> H2H" (without total Map Wins counting), then simply remove the third evaluation entirely.
```python
priorities = [lambda p : p.matchWins, lambda p : p.getMapScore()]
```
H2H will always run AFTER all of the priorities are evaluated.

Possible values to evaluate by:
##### ```p.matchWins```

##### ```p.matchLoss```

##### ```p.getMapScore()```

##### ```p.mapWins```

##### ```p.mapLoss```

##### ```p.name```

The option ```p.getMapScore()``` is only syntactic sugar for ```p.mapWins - p.mapLoss```. Please remember the ().

Note that even though the field ```p.h2h``` exists, ordering by it will not work (as it is not calculated at that point!). If you want to order by H2H, you can do this by setting ```priorities = []```

--------------------------------------------------------
### Functional assumptions
The program assumes standard tournament brackets, meaning:
* Every player plays each other player once
* All matches are of the same best-of-x, every best-of-x is odd (so no best-of-2) and a tie is not possible (like a 1.5 : 1.5 tie in chess)

If all components of the Evaluation Order are tied, Head-To-Head is evaluted. If Head-To-Head scores are equal (extremely unlikely, only possible in 4-way ties or bigger) then the tied participants are listed in alphabetical order. If participants are also named the same, the universe ends and we all die.
