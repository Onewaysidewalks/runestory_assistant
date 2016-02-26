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

    def mergeCharacterDetailHtml(self, htmlElement):
        #Structure of html Element:
        ###----> <div id="character">
        ###---------> 1st ul is Large Art √
        ###---------> 2nd ul is Evaluation  √
        ###---------> 1st table is motif weapon  √
        ###---------> 2nd table is raw/SS/building stats  √
        ###---------> 3rd table is sp recovery tiers  √
        ###---------> 2st h3 is first leader skill name
        ###---------> 1st p is first leader skill description
        ###---------> 3nd h3 is second leader skill description
        ###---------> 2nd p is second leader skill
        ###---------> 4th h3 is first skill name
        ###---------> 1st font is first skill sp cost
        ###---------> 3rd p is first skill description
        ###---------> 4th table is first skill stats
        ###---------> 5th h3 is second skill name
        ###---------> 2nd font is second skill sp cost
        ###---------> 4th p is second skill description
        ###---------> 5th table is second skill description
        ###---------> 6th div is awakening cost

        #first we pull out the character div
        htmlElement = htmlElement.find('div', {'id': 'character'})

        #Then we pull out all uls, all table, all h3, all p, all font, and all div
        #To match the above provided structure
        ul_list = htmlElement.find_all('ul')
        table_list = htmlElement.find_all('table')
        h3_list = htmlElement.find_all('h3')
        p_list = htmlElement.find_all('p')
        font_list = htmlElement.find_all('font')
        div_list = htmlElement.find_all('div')

        #Large Art Structure -> 1st ul -> 1st img -> {src}
        self.LargeImageUrl = ul_list[0].find('img')['src']
        print self.LargeImageUrl

        #Evaluation Structure -> 2nd ul -> 1st div -> 1st div -> 2nd div -> 2nd span -> font -> font -> {value}
        #Not all characters have evaluations
        try:
            self.JpEvaluation = ul_list[1].find('div').find('div').find_all('div')[1].find_all('span')[1].string.encode('utf-8')
        except AttributeError:
            pass
        finally:
            if hasattr(self, 'JpEvaluation'):
                print "Found Evaluation: %s" % self.Id
            else:
                print "No Evaluation found: %s" % self.Id

        #motif weapon name and url structure
        ## url -> 1st table -> tbody -> 4th tr -> 1st td -> 1st a -> {href}
        ## name -> 1st table -> tbody -> 4th tr -> 1st td -> 1st a -> {value}
        baseElement = table_list[0].find('tbody').find_all('tr')[3].find('td').find('a')
        self.MotifWeaponUrl = baseElement['href']
        #Normalize the url to start with a /
        if self.MotifWeaponUrl and self.MotifWeaponUrl[0] != '/':
            self.MotifWeaponUrl = '/%s' % self.MotifWeaponUrl
        self.MotifWeaponName = baseElement.string.encode('utf-8')

        #Lvl 1 stats, Lvl 100 stats, and Building+buffed stats
        ## Lvl1 -> 2nd table -> tbody -> 2 tr -> 2-6 td -> {value}
        ## Lvl100 -> 2nd table -> tbody -> 3 tr -> 2-6 td -> {value}
        ## SS+100 -> 2nd table -> tbody -> 4 tr -> 2-6 td -> {value}
        statRows = table_list[1].find('tbody').find_all('tr')

        for index in range(4):
            if index == 0: #skip first row as its headers
                continue

            statCells = statRows[index].find_all('td')

            if index == 1: #Lvl 1 Stats
                self.HP_1 = statCells[0].string.encode('utf-8')
                self.SP_1 = statCells[1].string.encode('utf-8')
                self.Attack_1 = statCells[2].string.encode('utf-8')
                self.Defense_1 = statCells[3].string.encode('utf-8')
                self.Crit_1 = statCells[4].string.encode('utf-8')
            if index == 2: #Lvl 100 Stats
                self.HP_100 = statCells[0].string.encode('utf-8')
                self.SP_100 = statCells[1].string.encode('utf-8')
                self.Attack_100 = statCells[2].string.encode('utf-8')
                self.Defense_100 = statCells[3].string.encode('utf-8')
                self.Crit_100 = statCells[4].string.encode('utf-8')
            if index == 3: #Lvl 100 + SS Stats
                self.HP_100_SS = statCells[0].string.encode('utf-8')
                self.SP_100_SS = statCells[1].string.encode('utf-8')
                self.Attack_100_SS = statCells[2].string.encode('utf-8')
                self.Defense_100_SS = statCells[3].string.encode('utf-8')
                self.Crit_100_SS = statCells[4].string.encode('utf-8')

        #SP Recovery Tiers
        ## 3rd table -> tbody -> 2 tr -> 2-6 tds -> {value}
        statRows = table_list[2].find('tbody').find_all('tr')

        for index in range(3):
            if index == 0: #skip first row as its headers
                continue

            statCells = statRows[index].find_all('td')

            if index == 1: #non town affected tiers
                self.SP_Recovery_0_SS = statCells[0].contents[0].string.encode('utf-8')
                self.SP_Recovery_1_SS = statCells[1].contents[0].string.encode('utf-8')
                self.SP_Recovery_2_SS = statCells[2].contents[0].string.encode('utf-8')
                self.SP_Recovery_3_SS = statCells[3].contents[0].string.encode('utf-8')
                self.SP_Recovery_4_SS = statCells[4].contents[0].string.encode('utf-8')
            if index == 2: #town affected tiers
                self.SP_Recovery_0_SS_Town = statCells[0].contents[0].string.encode('utf-8')
                self.SP_Recovery_1_SS_Town = statCells[1].contents[0].string.encode('utf-8')
                self.SP_Recovery_2_SS_Town = statCells[2].contents[0].string.encode('utf-8')
                self.SP_Recovery_3_SS_Town = statCells[3].contents[0].string.encode('utf-8')
                self.SP_Recovery_4_SS_Town = statCells[4].contents[0].string.encode('utf-8')

        #Leader Skills
        ## 1st Leader Skill: 2nd hr -> {value}
        ## 1st Leader Skill Description: 1st p -> {value}
        ## 2nd Leader Skill: 3rd hr -> {value}
        ## 2nd Leader Skill Description: 2nd p -> {value}
        self.LeaderSkill1Name = hr_list[1].string.encode('utf8')
        self.LeaderSkill1Description = p_list[0].string.encode('utf-8')
        self.LeaderSkill1Name = hr_list[2].string.encode('utf8')
        self.LeaderSkill1Description = p_list[1].string.encode('utf-8')

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)

    def __unicode__(self):
        return str(self.__dict__)
