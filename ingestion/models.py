def getClassFromId(id):
    if id is 1:
        return "Fencer"
    if id is 2:
        return "Lancer"
    if id is 3:
        return "Warrior"
    if id is 4:
        return "Brawler"
    if id is 5:
        return "Sniper"
    if id is 6:
        return "Mage"
    if id is 7:
        return "Dual Saber"
    if id is 8:
        return "Dragon Rider"
    return "UNKNOWN"

def getTypeFromId(id):
    if id is 1:
        return "Hero"
    if id is 2:
        return "Defense"
    if id is 3:
        return "Support"
    if id is 4:
        return "Technical"
    if id is 5:
        return "Balance"
    if id is 6:
        return "Skill"
    if id is 7:
        return "Attacker"
    return "UNKNOWN"

class Character(object):
    def __init__(self, htmlElement, classId, rarity, characterTypeId):
        self.ClassId = classId
        self.Class = getClassFromId(classId)
        self.Rarity = rarity
        self.Type = getTypeFromId(characterTypeId)
        self.TypeId = characterTypeId

        #There are nine columns in the htmlelement (a tr ROW)
        #The order is as follows:
        #0: Icon image
        #1: {EMPTY}
        #2: Name: From here we glean rawName, character id, and ingestionUrl
        #3: HP
        #4: SP
        #5: Attack
        #6: Defense
        #7: Crit
        #8: Auto Skills

        pos = 0
        for tableCell in htmlElement.find_all('td'):

            try:
                if pos is 0:
                    tableCell.find('a')
                    characterAnchor = htmlElement.find('a')
                    self.IconUrl = str(htmlElement.find('img')['src'])
                if pos is 2:
                    characterAnchor = tableCell.find('a')
                    self.RawName = unicode(characterAnchor.string).encode('utf-8')
                    self.Id = str(characterAnchor['href']).replace("character?id=", "")
                    self.IngestionUrl = "/" + str(characterAnchor['href']) #normalize to have a preceding slash
                if pos is 3:
                    self.HP = tableCell.string.encode('utf-8')
                if pos is 4:
                    self.SP = tableCell.string.encode('utf-8')
                if pos is 5:
                    self.Attack = tableCell.string.encode('utf-8')
                if pos is 6:
                    self.Defense = tableCell.string.encode('utf-8')
                if pos is 7:
                    self.Crit = tableCell.string.encode('utf-8')
                if pos is 8:
                    self.Passives = []
                    for span in tableCell.find_all('span'):
                        passive = span.string
                        if passive: #This will be empty if a character has less than three passives
                            self.Passives.append(passive.encode('utf-8').strip())
            except:
                print "Offending Html Element %s" % htmlElement
                print "Offending tableCell %s" % tableCell
                raise
            pos = pos + 1

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)

    def __unicode__(self):
        return str(self.__dict__)
