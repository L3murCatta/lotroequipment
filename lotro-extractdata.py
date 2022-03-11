from collections import Counter
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import itertools, os, pickle, sys

CLASS = 'Hunter'
CURRENT_LEVEL = 27
lockedSet = ()
#lockedSet = ('Greater Armour of the Erebor Charge', 4)
#lockedSet = ('Armour of the Hytbold Charge', 2)
ignoreDifficult = True
baseline = {'Critical Rating': 360,
            'Finesse Rating': 25,
            'Physical Mastery Rating': 974,
            'Tactical Mastery Rating': 119,
            'Outgoing Healing Rating': 0,
            'Resistance Rating': 377,
            'Critical Defence': 0,
            'Incoming Healing Rating': 0,
            'Block Rating': 0,
            'Parry Rating': 652,
            'Evade Rating': 891,
            'Physical Mitigation': 0,
            'Tactical Mitigation': 335}
##OLDTANK
#required = ['Maximum Morale',
#            'Physical Mitigation',
#            'Tactical Mitigation',
#            'Critical Defence',
#            'Incoming Healing Rating',
#            'Finesse Rating'
#            ]
#weights = [1, 1, 1, 1, 1, 1]
##TANK
#required = ['Maximum Morale',
#            'Physical Mitigation',
#            'Tactical Mitigation',
#            'Finesse Rating'
#            ]
#weights = [1, 1, 4, 1]
##PDPS
required = ['Physical Mastery Rating',
            'Critical Rating',
            'Finesse Rating',
            'Physical Mitigation',
            'Tactical Mitigation',
            'Maximum Morale']
weights = [1, 1, 1, 1, 1, 1]
##BPE TANK
#required = ['Maximum Morale',
#            'Physical Mitigation',
#            'Tactical Mitigation',
#            'Critical Defence',
#            'Block Rating',
#            'Parry Rating',
#            'Evade Rating']
#weights = [1, 1, 1, 1, 1, 1, 1]
##HEALER
#required = ['Critical Rating',
#            'Maximum Morale',
#            'Physical Mitigation',
#            'Tactical Mitigation',
#            'Outgoing Healing Rating']
#weights = [1, 1, 1, 1, 2]

Bstart = {'Critical Rating': 200,
          'Finesse Rating': 200,
          'Physical Mastery Rating': 270,
          'Tactical Mastery Rating': 270,
          'Outgoing Healing Rating': 200,
          'Resistance Rating': 200,
          'Critical Defence': 200,
          'Incoming Healing Rating': 200,
          'Block Rating': 200,
          'Parry Rating': 200,
          'Evade Rating': 200}
Bstart['Physical Mitigation'] = Bstart['Tactical Mitigation'] = 93 if CLASS in ('Minstrel', 'Lore-master', 'Rune-keeper') else (127 if CLASS in ('Hunter', 'Burglar', 'Warden') else 174)
Bend = {'Critical Rating': 15000,
        'Finesse Rating': 15000,
        'Physical Mastery Rating': 20250,
        'Tactical Mastery Rating': 20250,
        'Outgoing Healing Rating': 15000,
        'Resistance Rating': 15000,
        'Critical Defence': 15000,
        'Incoming Healing Rating': 15000,
        'Block Rating': 15000,
        'Parry Rating': 15000,
        'Evade Rating': 15000}
Bend['Physical Mitigation'] = Bend['Tactical Mitigation'] = 6975 if CLASS in ('Minstrel', 'Lore-master', 'Rune-keeper') else (9525 if CLASS in ('Hunter', 'Burglar', 'Warden') else 13050)
A = {'Critical Rating': 50,
     'Finesse Rating': 100,
     'Physical Mastery Rating': 400,
     'Tactical Mastery Rating': 400,
     'Outgoing Healing Rating': 140,
     'Resistance Rating': 100,
     'Critical Defence': 160,
     'Incoming Healing Rating': 50,
     'Block Rating': 26,
     'Parry Rating': 26,
     'Evade Rating': 26}
A['Physical Mitigation'] = A['Tactical Mitigation'] = 65 if CLASS in ('Minstrel', 'Lore-master', 'Rune-keeper') else (85 if CLASS in ('Hunter', 'Burglar', 'Warden') else 110)
Pcap = {'Critical Rating': 25,
        #'Critical Rating': 23.21,
        'Finesse Rating': 50,
        #'Finesse Rating': 28.57,
        #'Finesse Rating': 11.77,
        'Physical Mastery Rating': 200,
        #'Physical Mastery Rating': 188.24,
        'Tactical Mastery Rating': 200,
        #'Tactical Mastery Rating': 188.24,
        'Outgoing Healing Rating': 70,
        'Resistance Rating': 50,
        'Critical Defence': 80,
        'Incoming Healing Rating': 25,
        'Block Rating': 13,
        'Parry Rating': 13,
        'Evade Rating': 13}
Pcap['Physical Mitigation'] = Pcap['Tactical Mitigation'] = 40 if CLASS in ('Minstrel', 'Lore-master', 'Rune-keeper') else (50 if CLASS in ('Hunter', 'Burglar', 'Warden') else 60)

possibleStats = ['Armour',
                 'Agility',
                 'Block Rating',
                 'Critical Defence',
                 'Critical Rating',
                 'Evade Rating',
                 'Fate',
                 'Finesse Rating',
                 'In-Combat Morale Regen',
                 'In-Combat Power Regen',
                 'Incoming Healing Rating',
                 'Maximum Morale',
                 'Maximum Power',
                 'Might',
                 'Outgoing Healing Rating',
                 'Parry Rating',
                 'Physical Mastery Rating',
                 'Physical Mitigation',
                 'Resistance Rating',
                 'Tactical Mastery Rating',
                 'Tactical Mitigation',
                 'Vitality',
                 'Will']
reducedStats = ['Block Rating',
                'Critical Defence',
                'Critical Rating',
                'Evade Rating',
                'Finesse Rating',
                'In-Combat Morale Regen',
                'In-Combat Power Regen',
                'Incoming Healing Rating',
                'Maximum Morale',
                'Maximum Power',
                'Outgoing Healing Rating',
                'Parry Rating',
                'Physical Mastery Rating',
                'Physical Mitigation',
                'Resistance Rating',
                'Tactical Mastery Rating',
                'Tactical Mitigation']
dataranges = {'Head': 'V',
              'Shoulder': 'W',
              'Chest': 'V',
              'Gloves': 'U',
              'Legs': 'V',
              'Feet': 'V',
              'Back': 'T',
              'Earring': 'S',
              'Necklace': 'S',
              'Bracelet': 'N',
              'Ring': 'T',
              'Pocket': 'R',
              'Secondary Weapon / Shield': 'V',
              'Ranged Weapon': 'H',
              'Class': 'H',
              'Legendary Weapon Title': 'J',
              'Legendary Class Item Title': 'N',
              'Virtues': 'T',
              'Settings': 'Q',
              'Gems': 'O',
              'Runes': 'O',
              'Crafted': 'K'}
itemTypes = ['Head',
             'Shoulder',
             'Chest',
             'Gloves',
             'Legs',
             'Feet',
             'Back',
             'Earring',
             'Earring',
             'Necklace',
             'Bracelet',
             'Bracelet',
             'Ring',
             'Ring',
             'Pocket',
             'Secondary Weapon / Shield',
             'Secondary Weapon / Shield',
             'Ranged Weapon',
             'Class',
             'Legendary Weapon Title',
             'Legendary Class Item Title',
             'Virtues',
             'Virtues',
             'Virtues',
             'Virtues',
             'Virtues',
             'Settings',
             'Settings',
             'Gems',
             'Gems',
             'Runes',
             'Runes',
             'Crafted',
             'Crafted']
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
#SPREADSHEET_ID = '1AlnXgPXbzr_CI0tS5eK-imn88P8i9Z_A550j6dQHfYQ'
#SPREADSHEET_ID = '1EXSlpqwAmRJVgiOkExP4wo8RPwwtpVSggy8bYJK-AQk'
SPREADSHEET_ID = '1PtI43U5lcSQFD_Cx-eG2bRApmvkvQKtQ0brqoQpA2Q0'

creds = None
# The file token.pickle stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)
service = build('sheets', 'v4', credentials=creds)
sheet = service.spreadsheets()

legitItems = [CLASS, 'Light', '']
if CLASS == 'Hunter' or CLASS == 'Warden' or CLASS == 'Burglar':
    legitItems.append('Medium')
if CLASS == 'Captain' or CLASS == 'Guardian' or CLASS == 'Champion' or CLASS == 'Beorning':
    legitItems.append('Medium')
    legitItems.append('Heavy')
if CLASS == 'Minstrel':
    legitItems.append('Shield')
if CLASS == 'Captain':
    legitItems.append('Halberd')
    #legitItems.append('Shield')
if CLASS == 'Warden':
    legitItems.append('Shield')
    legitItems.append('Warden\'s Shield')
if CLASS == 'Lore-master':
    legitItems.append('One-handed Sword')
if CLASS == 'Guardian':
    legitItems.append('Shield')
    legitItems.append('Heavy Shield')
if CLASS == 'Burglar':
    legitItems.append('One-handed Sword')
    legitItems.append('Dagger')
    legitItems.append('One-handed Mace')
    legitItems.append('One-handed Axe')
    legitItems.append('One-handed Club')
    legitItems.append('One-handed Hammer')
if CLASS == 'Hunter':
    legitItems.append('One-handed Sword')
    legitItems.append('One-handed Axe')
    legitItems.append('One-handed Club')
    legitItems.append('One-handed Hammer')
    legitItems.append('One-handed Mace')
    legitItems.append('Dagger')
    legitItems.append('Spear')
    legitItems.append('Bow')
    legitItems.append('Crossbow')

def selectLegitItems(values, legitItems):
    res = []
    for item in values:
        reqs = item[1].split('|')
        if any([req in legitItems for req in reqs]):
            res.append(item)
    return res

def restructure(values, statnames, meaningless = 3):
    global setItems, uniqueItems
    res = dict()
    for item in values:
        if item[0][0] == '#':
            if ignoreDifficult:
                continue
            else:
                item[0] = item[0][1:]
        res[item[0]] = dict()
        for stat in possibleStats:
            res[item[0]][stat] = 0
        cnt = 0
        for stat in item[meaningless:]:
            if len(stat) > 0:
                res[item[0]][statnames[0][cnt+meaningless]] = float(stat.replace(',', '.'))
            cnt += 1
        if 'Set' in statnames[0] and len(item[statnames[0].index('Set')]) > 0:
            setItems[item[0]] = item[statnames[0].index('Set')]
        if 'Unique' in statnames[0] and item[statnames[0].index('Unique')] == 'TRUE':
            uniqueItems.add(item[0])
    return res

def convertStats(values):
    for item in values.keys():
        if CLASS in ('Beorning', 'Captain'):
            values[item]['Physical Mastery Rating'] += 2.5 * values[item]['Might']
            values[item]['Tactical Mastery Rating'] += 2.5 * values[item]['Might']
        elif CLASS in ('Champion', 'Guardian'):
            values[item]['Physical Mastery Rating'] += 3 * values[item]['Might']
        elif CLASS == 'Warden':
            values[item]['Physical Mastery Rating'] += 2 * values[item]['Might']
        if CLASS in ('Beorning', 'Champion'):
            values[item]['Critical Rating'] += 2 * values[item]['Might']
        if CLASS == 'Beorning':
            values[item]['Block Rating'] += 2 * values[item]['Might']
            values[item]['Parry Rating'] += 3 * values[item]['Might']
            values[item]['Evade Rating'] += 1 * values[item]['Might']
        elif CLASS == 'Champion':
            values[item]['Parry Rating'] += 2 * values[item]['Might']
            values[item]['Evade Rating'] += 2 * values[item]['Might']
            values[item]['Physical Mitigation'] += 2 * values[item]['Might']
        else:
            values[item]['Block Rating'] += 3 * values[item]['Might']
            values[item]['Parry Rating'] += 2 * values[item]['Might']
        if CLASS == 'Beorning':
            values[item]['Physical Mastery Rating'] += 2 * values[item]['Agility']
            values[item]['Evade Rating'] += 2 * values[item]['Agility']
        elif CLASS in ('Burglar', 'Hunter', 'Warden'):
            values[item]['Physical Mastery Rating'] += 3 * values[item]['Agility']
            values[item]['Parry Rating'] += 2 * values[item]['Agility']
            values[item]['Evade Rating'] += 3 * values[item]['Agility']
        else:
            values[item]['Parry Rating'] += 2 * values[item]['Agility']
            values[item]['Evade Rating'] += 3 * values[item]['Agility']
        values[item]['Critical Rating'] += values[item]['Agility']
        if CLASS in ('Beorning', 'Guardian', 'Warden'):
            values[item]['Maximum Morale'] += 5 * values[item]['Vitality']
        elif CLASS in ('Burglar', 'Captain', 'Champion'):
            values[item]['Maximum Morale'] += 4.5 * values[item]['Vitality']
        else:
            values[item]['Maximum Morale'] += 4 * values[item]['Vitality']
            values[item]['Tactical Mitigation'] += values[item]['Vitality']
        if CLASS == 'Captain':
            values[item]['Resistance Rating'] += 2 * values[item]['Vitality']
        else:
            values[item]['Resistance Rating'] += values[item]['Vitality']
        if CLASS == 'Champion':
            values[item]['Block Rating'] += values[item]['Vitality']
        if CLASS in ('Lore-master', 'Minstrel', 'Rune-keeper'):
            values[item]['Tactical Mastery Rating'] += 3 * values[item]['Will']
            values[item]['Finesse Rating'] += values[item]['Will']
            values[item]['Resistance Rating'] += 2 * values[item]['Will']
        elif CLASS == 'Beorning':
            values[item]['Tactical Mastery Rating'] += 2 * values[item]['Will']
            values[item]['Resistance Rating'] += values[item]['Will']
        elif CLASS in ('Burglar', 'Champion', 'Guardian', 'Hunter'):
            values[item]['Tactical Mastery Rating'] += values[item]['Will']
            values[item]['Resistance Rating'] += 2 * values[item]['Will']
        else:
            values[item]['Resistance Rating'] += 2 * values[item]['Will']
        if CLASS in ('Beorning', 'Minstrel', 'Rune-keeper'):
            values[item]['Evade Rating'] += values[item]['Will']
        values[item]['Tactical Mitigation'] += values[item]['Will']
        values[item]['Critical Rating'] += 2.5 * values[item]['Fate']
        if CLASS in ('Burglar', 'Captain', 'Champion', 'Guardian', 'Hunter', 'Warden'):
            values[item]['Finesse Rating'] += values[item]['Fate']
        if CLASS == 'Beorning':
            values[item]['Tactical Mitigation'] += 2 * values[item]['Fate']
            values[item]['In-Combat Morale Regen'] += 3 * values[item]['Fate']
            values[item]['Finesse Rating'] += 0.5 * values[item]['Fate']
        else:
            values[item]['Tactical Mitigation'] += values[item]['Fate']
            values[item]['In-Combat Morale Regen'] += 1.5 * values[item]['Fate']
            values[item]['In-Combat Power Regen'] += 1.71 * values[item]['Fate']
        if CLASS != 'Captain':
            values[item]['Resistance Rating'] += values[item]['Fate']
        if CLASS == 'Lore-master': #?
            values[item]['Finesse Rating'] += values[item]['Fate'] #?
        values[item]['Physical Mitigation'] += values[item]['Armour']
        values[item]['Tactical Mitigation'] += 0.2 * values[item]['Armour']
        del values[item]['Might']
        del values[item]['Agility']
        del values[item]['Vitality']
        del values[item]['Fate']
        del values[item]['Will']
        del values[item]['Armour']
    return values

def cutRedundantItems(values):
    ikeys = list(values.keys())
    jkeys = values[ikeys[0]].keys()
    redundancy = []
    for i1 in range(len(ikeys)):
        if ikeys[i1] in setItems:
            continue
        for i2 in range(len(ikeys)):
            if i1 == i2 or ikeys[i2] in uniqueItems:
                continue
            for j in jkeys:
                if values[ikeys[i1]][j] > values[ikeys[i2]][j]:
                    break
            else:
                print(ikeys[i1], 'is redundant against', ikeys[i2])
                redundancy.append(ikeys[i1])
                break
    for key in redundancy:
        del values[key]
    return values

def emptyList():
    res = dict()
    item = dict()
    for stat in possibleStats:
        item[stat] = 0
    res['Empty Slot'] = item
    return res

def statToPercentage(name, value):
    #return min(A[name] * value / (value + Bend[name]) + 0.0002, Pcap[name])
    Lend = 75
    Lstart = 1
    L = CURRENT_LEVEL
    B = (Bstart[name]*(Lend-L)+(L-Lstart)*Bend[name]) / (Lend-Lstart)
    B = B // 10 * 10
    return min(A[name] * value / (value + B) + 0.0002, Pcap[name])

def calculateMaxMorale():
    resBuild = []
    resMorale = 0
    for category in itemTypes:
        morales = [(fulldb[category][item]['Maximum Morale'], item) for item in fulldb[category]]
        morales.sort()
        while morales[-1][1] in resBuild and (morales[-1][1] in uniqueItems or category == 'Virtues'):
            del morales[-1]
        resBuild.append(morales[-1][1])
        resMorale += morales[-1][0]
    return resMorale

def sortItems(category):
    OPP = dict()
    for item in fulldb[category]:
        OPP[item] = 0
    cnt = 0
    for stat in required:
        stats = [(fulldb[category][item][stat], item) for item in fulldb[category]]
        stats.sort()
        rankings = [0 for s in stats]
        increment = 0
        for i in range(1, len(stats)):
            if stats[i][0] > stats[i-1][0]:
                increment = i
            OPP[stats[i][1]] += weights[cnt] * increment
        cnt += 1
    OPP = [(OPP[key], key) for key in OPP]
    OPP.sort()
    return OPP

def evaluateBuild(build):
    currentStats = dict()
    setScore = Counter()
    for item in build:
        if item in setItems:
            setScore[setItems[item]] += 1
    for stat in required:
        currentStats[stat] = 0
        cnt = -1
        for item in build:
            cnt += 1
            currentStats[stat] += fulldb[itemTypes[cnt]][item][stat]
        for itemSet in setData:
            setInfo = itemSet.split('|')
            if setScore[setInfo[0]] >= int(setInfo[1]):
                currentStats[stat] += setData[itemSet][stat]
            try:
                if lockedSet[0] == setInfo[0] and setScore[setInfo[0]] < lockedSet[1]:
                    currentStats[stat] = -1
            except IndexError:
                pass
        try:
            currentStats[stat] += baseline[stat]
        except KeyError:
            pass
        try:
            currentStats[stat] = statToPercentage(stat, currentStats[stat])
        except KeyError:
            pass
    return currentStats

def evaluateEfficiency(stats):
    efficiencyRating = 0
    cnt = 0
    for stat in required:
        try:
            efficiencyRating += weights[cnt] * stats[stat] / Pcap[stat]
        except KeyError:
            if stat == 'Maximum Morale':
                efficiencyRating += weights[cnt] * stats['Maximum Morale'] / calculateMaxMorale()
        cnt += 1
    return efficiencyRating

fulldb = dict()
setItems = dict()
uniqueItems = set()
for key in dataranges.keys():
    print('### ' + key)
    if key in ('Back', 'Necklace', 'Ranged Weapon', 'Class', 'Legendary Weapon Title', 'Legendary Class Item Title'):
        meaningless = 2
    elif key in ('Earring', 'Ring'):
        meaningless = 4
    elif key in ('Virtues', 'Settings', 'Gems', 'Runes', 'Crafted'):
        meaningless = 1
    else:
        meaningless = 3
    #print('Connecting to the database...')
    DATA_RANGE_NAME = key + '!A2:' + dataranges[key]
    STAT_NAMES = key + '!A1:' + dataranges[key] + '1'
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                    range=DATA_RANGE_NAME).execute()
    origvalues = result.get('values', [])
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                    range=STAT_NAMES).execute()
    statnames = result.get('values', [])
    #print('Data retrieved!')
    #print('Selecting equippable items...')
    values = selectLegitItems(origvalues, legitItems)        
    #print('Restructuring the data...')
    values = restructure(values, statnames, meaningless)
    #print('Converting stats...')
    values = convertStats(values)
    #print('Checking for redundancy...')
#    try:
#        values = cutRedundantItems(values)
#    except IndexError:
#        values = emptyList()
    if values == {}:
        values = emptyList()
    fulldb[key] = values

print('### Set Data')
DATA_RANGE_NAME = 'Set Data!A2:F'
STAT_NAMES = 'Set Data!A1:F1'
result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                    range=DATA_RANGE_NAME).execute()
origvalues = result.get('values', [])
result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range=STAT_NAMES).execute()
statnames = result.get('values', [])
values = restructure(origvalues, statnames, 1)
setData = convertStats(values)

OPP = dict()
for category in dataranges:
    OPP[category] = sortItems(category)
    try:
        cnt = -1
        for item in OPP[category]:
            cnt += 1
            if item[1] in setItems and setItems[item[1]] == lockedSet[0]:
                OPP[category] = OPP[category][:cnt] + OPP[category][cnt+1:] + [item]
    except IndexError:
        pass
            
currentBuild = []
seen = []
for category in itemTypes:
    curIndex = -1
    while OPP[category][curIndex][1] in currentBuild and (OPP[category][curIndex][1] in uniqueItems or category == 'Virtues'):
        curIndex -= 1
    currentBuild.append(OPP[category][curIndex][1])
    seen.append(OPP[category][curIndex][1])
currentStats = evaluateBuild(currentBuild)
efficiencyRating = evaluateEfficiency(currentStats)
print(currentBuild)
print(currentStats)
print(efficiencyRating)
print()
mpSize = 1
mutationPool = dict()
for category in dataranges:
    mutationPool[category] = []
completed = []
#sys.exit()
while True:
    for category in dataranges:
        curIndex = -1
        try:
            while OPP[category][curIndex][1] in seen and not (category in ('Secondary Weapon / Shield', 'Earring', 'Ring', 'Bracelet', 'Settings', 'Gems', 'Runes', 'Crafted') and OPP[category][curIndex][1] not in uniqueItems and seen.count(OPP[category][curIndex][1]) < 2):
                curIndex -= 1
            seen.append(OPP[category][curIndex][1])
            mutationPool[category].append(OPP[category][curIndex][1])
        except IndexError:
            if category not in completed:
                completed.append(category)
    if len(completed) == len(dataranges.keys()):
        break

    while True:
        bestEstimatedReplacement = ''
        bestEstimatedEfficiency = efficiencyRating
        bestReplaced = ''
        bestReplacer = ''
        potential = False
        for category in mutationPool:
            for mutation in mutationPool[category]:
                cnt = -1
                for itemtype in itemTypes:
                    cnt += 1
                    if itemtype == category:
                        newBuild = currentBuild[:cnt] + [mutation] + currentBuild[cnt+1:]
                        newStats = evaluateBuild(newBuild)
                        newEfficiency = evaluateEfficiency(newStats)
                        if newEfficiency > bestEstimatedEfficiency:
                            bestEstimatedEfficiency = newEfficiency
                            potential = True
                            bestEstimatedReplacement = newBuild
                            bestReplaced = category + '|' + currentBuild[cnt]
                            bestReplacer = mutation
                            #print(mutation, bestReplaced)
        if not potential:
            break
        efficiencyRating = bestEstimatedEfficiency
        currentBuild = bestEstimatedReplacement
        replacement = bestReplaced.split('|')
        mutationPool[replacement[0]].append(replacement[1])
        mutationPool[replacement[0]].remove(bestReplacer)
        print(currentBuild)
        print(evaluateBuild(currentBuild))
        print(efficiencyRating)
        print()
    mpSize += 1
    #print('DEPTH', mpSize, 'ANALYZED')
    
'''
print('Building sets. Please wait...')
ekeys = list(fulldb['Earring'].keys())
bkeys = list(fulldb['Bracelet'].keys())
rkeys = list(fulldb['Ring'].keys())
vkeys = list(fulldb['Virtues'].keys())
skeys = list(fulldb['Settings'].keys())
gkeys = list(fulldb['Gems'].keys())
ukeys = list(fulldb['Runes'].keys())
ckeys = list(fulldb['Crafted'].keys())
progress = 0
hugedump = []
for head in fulldb['Head']:
    print(str(round(progress * 100 / len(fulldb['Head'].keys())))+'%')
    progress += 1
    for shoulder, chest, gloves, legs, feet, back, necklace, pocket, sws, rw, lwt, lcit, e1, b1, r1, cl, v1, s1, g1, u1, c1, in itertools.product(fulldb['Shoulder'], fulldb['Chest'], fulldb['Gloves'], fulldb['Legs'], fulldb['Feet'], fulldb['Back'], fulldb['Necklace'], fulldb['Pocket'], fulldb['Secondary Weapon / Shield'], fulldb['Ranged Weapon'], fulldb['Legendary Weapon Title'], fulldb['Legendary Class Item Title'], range(len(ekeys)), range(len(bkeys)), range(len(rkeys)), fulldb['Class'], range(len(vkeys)), range(len(skeys)), range(len(gkeys)), range(len(ukeys)), range(len(ckeys))):
        eshift = 1 if ekeys[e1] in uniqueItems else 0
        bshift = 1 if bkeys[b1] in uniqueItems else 0
        rshift = 1 if rkeys[r1] in uniqueItems else 0
        for e2, b2, r2, v2, s2, g2, u2, c2 in itertools.product(range(e1+eshift, len(ekeys)), range(b1+bshift, len(bkeys)), range(r1+rshift, len(rkeys)), range(v1+1, len(vkeys)), range(s1, len(skeys)), range(g1, len(gkeys)), range(u1, len(ukeys)), range(c1, len(ckeys))):
            for v3 in range(v2+1, len(vkeys)):
                for v4 in range(v3+1, len(vkeys)):
                    for v5 in range(v4+1, len(vkeys)):
                        currentBuild = (head, shoulder, chest, gloves, legs, feet, back, ekeys[e1], ekeys[e2], necklace, bkeys[b1], bkeys[b2], rkeys[r1], rkeys[r2], pocket, sws, rw, cl, lwt, lcit, vkeys[v1], vkeys[v2], vkeys[v3], vkeys[v4], vkeys[v5], skeys[s1], skeys[s2], gkeys[g1], gkeys[g2], ukeys[u1], ukeys[u2], ckeys[c1], ckeys[c2])
                        currentStats = dict()
                        for stat in reducedStats:
                            currentStats[stat] = 0
                            cnt = 0
                            for itemtype in itemTypes:
                                currentStats[stat] += fulldb[itemtype][currentBuild[cnt]][stat]
                                cnt += 1
                        for stat in baseline.keys():
                            currentStats[stat] += baseline[stat]
                        setScore = Counter()
                        for item in currentBuild:
                            if item in setItems:
                                setScore[setItems[item]] += 1
                        for itemSet in setData.keys():
                            setInfo = itemSet.split('|')
                            if setScore[setInfo[0]] >= int(setInfo[1]):
                                for stat in reducedStats:
                                    currentStats[stat] += setData[itemSet][stat]
                        for stat in baseline.keys():
                            currentStats[stat] = statToPercentage(stat, currentStats[stat])
                        currentStats['OPP'] = 0
                        currentStats['Build'] = currentBuild
                        hugedump.append(currentStats)
print('All sets calculated.')
print('Optimizing the requested parameters...')
for par in required:
    tmp = list(set([x[par] for x in hugedump]))
    tmp.sort()
    tmp.reverse()
    for entry in hugedump:
        entry['OPP'] += tmp.index(entry[par])
hugedump.sort(key = lambda x : x['OPP'])
for i in range(5):
    print(hugedump[i])
    print()
'''
#with open(CLASS+'setdb75.pickle', 'wb') as ws:
#    pickle.dump(???, ws)
