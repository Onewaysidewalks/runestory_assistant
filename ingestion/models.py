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
                    self.IconUrl = str(htmlElement.find('img')['src']).strip()
                if pos is 2:
                    characterAnchor = tableCell.find('a')
                    self.RawName = unicode(characterAnchor.string).encode('utf-8').strip().replace('\r', '').replace('\n', '')
                    self.Id = str(characterAnchor['href']).replace("character?id=", "").strip()
                    self.IngestionUrl = "/" + str(characterAnchor['href']).strip() #normalize to have a preceding slash
                if pos is 3:
                    if tableCell.string:
                        self.HP = tableCell.string.encode('utf-8').strip().replace('\r', '').replace('\n', '')
                    else:
                        self.HP = 0
                if pos is 4:
                    if tableCell.string:
                        self.SP = tableCell.string.encode('utf-8').strip().replace('\r', '').replace('\n', '')
                    else:
                        self.SP = 0
                if pos is 5:
                    if tableCell.string:
                        self.Attack = tableCell.string.encode('utf-8').strip().replace('\r', '').replace('\n', '')
                    else:
                        self.Attack = 0
                if pos is 6:
                    if tableCell.string:
                        self.Defense = tableCell.string.encode('utf-8').strip().replace('\r', '').replace('\n', '')
                    else:
                        self.Defense = 0
                if pos is 7:
                    if tableCell.string:
                        self.Crit = tableCell.string.encode('utf-8').strip().replace('\r', '').replace('\n', '')
                    else:
                        self.Crit = 0
                if pos is 8:
                    self.Passives = []
                    for span in tableCell.find_all('span'):
                        passive = span.string
                        if passive: #This will be empty if a character has less than three passives
                            self.Passives.append(passive.encode('utf-8').strip().replace('\r', '').replace('\n', ''))
            except Exception as ex:
                print "Could not create base character: %s" % self.Id
                raise

            pos = pos + 1

    def mergeCharacterDetailHtml(self, htmlElement):
        #Approximate Structure of html Element:
        ###----> <div id="character">
        ###---------> 1st ul is Large Art
        ###---------> 2nd ul is Evaluation
        ###---------> 1st table is motif weapon
        ###---------> 2nd table is raw/SS/building stats
        ###---------> 3rd table is sp recovery tiers
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
        ###---------> 6th div is awakening cost TODO

        #first we pull out the character div
        htmlElement = htmlElement.find('div', {'id': 'character'})

        ##Note: not all characters have 2 leader skills (minimum 1), so we have to account for that as well
        #This will affect both skill and leader skill names, as well as descriptions
        secondLeaderSkillNameIndex = 2
        secondLeaderSkillDescIndex = 1
        firstSkillNameIndex = 3
        firstSkillDescIndex = 2
        firstSkillSpIndex = 64
        firstSkillSpReducedIndex = None
        secondSkillNameIndex = 4
        secondSkillDescIndex = 3
        secondSkillSpIndex = 73
        secondSkillSpReducedIndex = None

        try:
            #Then we pull out all uls, all table, all h3, all p, all font, and all div
            #To match the above provided structure
            ul_list = htmlElement.find_all('ul')
            table_list = htmlElement.find_all('table')
            h3_list = htmlElement.find_all('h3')
            p_list = htmlElement.find_all('p')
            font_list = htmlElement.find_all('font')
            div_list = htmlElement.find_all('div')

            ##Note: some tables can be missing, so we need to adjust what we are looking for appropriately.
            #There are 7 tables in a full set, including a table we dont care about, so we must make sure the list
            #has enough to cover that table, including the on we dont care about
            firstSkillTableIndex = 4 #OPTIONAL
            secondSkillTableIndex = 5 #OPTIONAL

            if len(table_list) == 6:
                secondSkillTableIndex = None
            elif len(table_list) < 6:
                firstSkillTableIndex = None
                secondSkillTableIndex = None

            if len(h3_list) < 7: #not enough to have two leader skills
                secondLeaderSkillNameIndex = None
                secondLeaderSkillDescIndex = None
                firstSkillNameIndex = 2
                firstSkillDescIndex = 1
                secondSkillNameIndex = 3
                secondSkillDescIndex = 2

            #set the skill indexes based on their adjacent SP-classed span
            foundFirst = False
            for elementIndex in range(len(htmlElement.contents)):
                if 'class="sp"' in '%s' % htmlElement.contents[elementIndex]:
                    print 'sp class found at %s' % elementIndex
                    if foundFirst:
                        secondSkillSpIndex = elementIndex + 1

                        secondSkillDescIndex = elementIndex + 2
                        #Now we have to see if the desc index is a span (if it is, its actually the reduced SP cost, and the next one is the desc)
                        if 'span' in str(htmlElement.contents[secondSkillDescIndex]):
                            print 'Found Reduced SP Cost skill 2'
                            secondSkillSpReducedIndex = secondSkillDescIndex
                            secondSkillDescIndex = secondSkillDescIndex + 2

                        secondSkillNameIndex = elementIndex - 2
                    else:
                        firstSkillSpIndex = elementIndex + 1
                        firstSkillDescIndex = elementIndex + 2

                        #Now we have to see if the desc index is a span (if it is, its actually the reduced SP cost, two more is the desc)
                        if 'span' in str(htmlElement.contents[firstSkillDescIndex]):
                            print 'Found Reduced SP Cost skill 1'
                            firstSkillSpReducedIndex = firstSkillDescIndex
                            firstSkillDescIndex = firstSkillDescIndex + 2

                        firstSkillNameIndex = elementIndex - 2
                        foundFirst = True

            #Large Art Structure -> 1st ul -> 1st img -> {src}
            if ul_list[0].find('img'):
                self.LargeImageUrl = ul_list[0].find('img')['src']
            else:
                print 'No LargeImageUrl found, character %s' % self.Id

            #Evaluation Structure -> 2nd ul -> 1st div -> 1st div -> 2nd div -> 2nd span -> font -> font -> {value}
            #Not all characters have evaluations
            try:
                self.JpEvaluation = ul_list[1].find('div').find('div').find_all('div')[1].find_all('span')[1].string.encode('utf-8').strip().replace('\n', '').replace('\r', '')
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
            if baseElement:
                self.MotifWeaponUrl = baseElement['href']
                #Normalize the url to start with a /
                if self.MotifWeaponUrl and self.MotifWeaponUrl[0] != '/':
                    self.MotifWeaponUrl = '/%s' % self.MotifWeaponUrl
                self.MotifWeaponName = baseElement.string.encode('utf-8').strip().replace('\n', '').replace('\r', '')
                self.MotifWeaponId = self.MotifWeaponUrl[self.MotifWeaponUrl.index('=') + 1:].encode('utf-8')
            else:
                print 'No motif details for character %s' % self.Id
                self.MotifWeaponName = ''
                self.MotifWeaponUrl = ''


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
                    #Note: shinki releases dont have lvl1 stats
                    if statCells[0].string:
                        self.HP_1 = statCells[0].string.encode('utf-8').replace('\n', '').replace('\r', '')
                        self.SP_1 = statCells[1].string.encode('utf-8').replace('\n', '').replace('\r', '')
                        self.Attack_1 = statCells[2].string.encode('utf-8').replace('\n', '').replace('\r', '')
                        self.Defense_1 = statCells[3].string.encode('utf-8').replace('\n', '').replace('\r', '')
                        self.Crit_1 = statCells[4].string.encode('utf-8').replace('\n', '').replace('\r', '')
                    else:
                        self.HP_1 = 'UNKNOWN'
                        self.SP_1 = 'UNKNOWN'
                        self.Attack_1 = 'UNKNOWN'
                        self.Defense_1 = 'UNKNOWN'
                        self.Crit_1 = 'UNKNOWN'
                if index == 2: #Lvl 100 Stats
                    if statCells[0].string:
                        self.HP_100 = statCells[0].string.encode('utf-8').replace('\n', '').replace('\r', '')
                        self.SP_100 = statCells[1].string.encode('utf-8').replace('\n', '').replace('\r', '')
                        self.Attack_100 = statCells[2].string.encode('utf-8').replace('\n', '').replace('\r', '')
                        self.Defense_100 = statCells[3].string.encode('utf-8').replace('\n', '').replace('\r', '')
                        self.Crit_100 = statCells[4].string.encode('utf-8').replace('\n', '').replace('\r', '')
                    else:
                        self.HP_100 = 'UNKNOWN'
                        self.SP_100 = 'UNKNOWN'
                        self.Attack_100 = 'UNKNOWN'
                        self.Defense_100 = 'UNKNOWN'
                        self.Crit_100 = 'UNKNOWN'
                if index == 3: #Lvl 100 + SS Stats
                    if statCells[0].string:
                        self.HP_100_SS = statCells[0].string.encode('utf-8').replace('\n', '').replace('\r', '')
                        self.SP_100_SS = statCells[1].string.encode('utf-8').replace('\n', '').replace('\r', '')
                        self.Attack_100_SS = statCells[2].string.encode('utf-8').replace('\n', '').replace('\r', '')
                        self.Defense_100_SS = statCells[3].string.encode('utf-8').replace('\n', '').replace('\r', '')
                        self.Crit_100_SS = statCells[4].string.encode('utf-8').replace('\n', '').replace('\r', '')
                    else:
                        self.HP_100_SS = 'UNKNOWN'
                        self.SP_100_SS = 'UNKNOWN'
                        self.Attack_100_SS = 'UNKNOWN'
                        self.Defense_100_SS = 'UNKNOWN'
                        self.Crit_100_SS = 'UNKNOWN'

            #SP Recovery Tiers
            ## 3rd table -> tbody -> 2 tr -> 2-6 tds -> {value}
            statRows = table_list[2].find('tbody').find_all('tr')

            for index in range(len(statRows)):
                if index == 0: #skip first row as its headers
                    continue

                statCells = statRows[index].find_all('td')

                if index == 1: #non town affected tiers
                    self.SP_Recovery_0_SS = statCells[0].contents[0].string.encode('utf-8').strip().replace('\n', '').replace('\r', '')
                    self.SP_Recovery_1_SS = statCells[1].contents[0].string.encode('utf-8').strip().replace('\n', '').replace('\r', '')
                    self.SP_Recovery_2_SS = statCells[2].contents[0].string.encode('utf-8').strip().replace('\n', '').replace('\r', '')
                    self.SP_Recovery_3_SS = statCells[3].contents[0].string.encode('utf-8').strip().replace('\n', '').replace('\r', '')
                    self.SP_Recovery_4_SS = statCells[4].contents[0].string.encode('utf-8').strip().replace('\n', '').replace('\r', '')
                if index == 2: #town affected tiers
                    self.SP_Recovery_0_SS_Town = statCells[0].contents[0].string.encode('utf-8').strip().replace('\n', '').replace('\r', '')
                    self.SP_Recovery_1_SS_Town = statCells[1].contents[0].string.encode('utf-8').strip().replace('\n', '').replace('\r', '')
                    self.SP_Recovery_2_SS_Town = statCells[2].contents[0].string.encode('utf-8').strip().replace('\n', '').replace('\r', '')
                    self.SP_Recovery_3_SS_Town = statCells[3].contents[0].string.encode('utf-8').strip().replace('\n', '').replace('\r', '')
                    self.SP_Recovery_4_SS_Town = statCells[4].contents[0].string.encode('utf-8').strip().replace('\n', '').replace('\r', '')
            else:
                self.SP_Recovery_0_SS = ''
                self.SP_Recovery_1_SS = ''
                self.SP_Recovery_2_SS = ''
                self.SP_Recovery_3_SS = ''
                self.SP_Recovery_4_SS = ''
                self.SP_Recovery_0_SS_Town = ''
                self.SP_Recovery_1_SS_Town = ''
                self.SP_Recovery_2_SS_Town = ''
                self.SP_Recovery_3_SS_Town = ''
                self.SP_Recovery_4_SS_Town = ''

            #Leader Skills
            ## 1st Leader Skill: 2nd h3 -> {value}
            ## 1st Leader Skill Description: 1st p -> {value}
            ## 2nd Leader Skill: 3rd h3 -> {value}
            ## 2nd Leader Skill Description: 2nd p -> {value}
            if h3_list[1].string:
                self.LeaderSkill1Name = h3_list[1].string.encode('utf8').strip().replace('\n', '').replace('\r', '')
            elif len(h3_list[1].contents) > 1:
                self.LeaderSkill1Name = h3_list[1].contents[0].string.encode('utf-8').strip().replace('\n', '').replace('\r', '')
            else:
                self.LeaderSkill1Name = ''
                print 'No leader skill 1 name, character %s, element:%s' % (self.Id, h3_list[1])

            if p_list[0].string:
                self.LeaderSkill1Description = p_list[0].string.encode('utf-8').strip().replace('\n', '').replace('\r', '')
            else:
                self.LeaderSkill1Description = ''
                print 'No leader skill 1 description, character %s, element %s' % (self.Id, p_list[0].string)

            if secondLeaderSkillNameIndex: #if there is a second leader skill, pull it
                if h3_list[secondLeaderSkillNameIndex].string:
                    self.LeaderSkill2Name = h3_list[secondLeaderSkillNameIndex].string.encode('utf8').strip().replace('\n', '').replace('\r', '')
                elif len(h3_list[secondLeaderSkillNameIndex].contents) > 1:
                    self.LeaderSkill2Name = h3_list[secondLeaderSkillNameIndex].contents[0].string.encode('utf-8').strip().replace('\n', '').replace('\r', '')
                else:
                    self.LeaderSkill2Name = ''
                    print 'No leader skill 2 name, character %s, element:%s' % (self.Id, h3_list[secondLeaderSkillNameIndex])

                if p_list[secondLeaderSkillDescIndex].string:
                    self.LeaderSkill2Description = p_list[secondLeaderSkillDescIndex].string.encode('utf-8').strip().replace('\n', '').replace('\r', '')
                else:
                    self.LeaderSkill2Description = ''
                    print 'No leader skill 2 descriptioni, character %s, element %s' % (self.Id, p_list[secondLeaderSkillDescIndex].string).replace('\n', '').replace('\r', '')
            else:
                self.LeaderSkill2Description = ''
                self.LeaderSkill2Name = ''
                print 'No second leader skill for %s' % self.Id

            #Action Skills
            ## 1st skill: 4th h3 -> {value}
            ## 1st skill cost: ...
            ## 1st skill description: 3rd p -> {value}
            ## 1st skill stats: 4th table -> tbody -> 2 tr's -> td -> {value}

            ## 2nd skill: 5th h3 -> {value}
            ## 2nd skill cost: ...
            ## 2nd skill description: 4rd p -> {value}
            ## 2nd skill stats: 5th table -> tbody -> 2 tr's -> td -> {value}

            self.ActionSkill1Name = htmlElement.contents[firstSkillNameIndex].contents[0].string.encode('utf8').strip().replace('\n', '').replace('\r', '')
            self.ActionSkill1SPCost = htmlElement.contents[firstSkillSpIndex].string.encode('utf-8').strip().replace('\n', '').replace('\r', '')

            if firstSkillSpReducedIndex:
                self.ActionSkill1ReducedSPCost = htmlElement.contents[firstSkillSpReducedIndex].string.encode('utf-8').strip().replace('\n', '').replace('\r', '').replace('(', '').replace(')', '')

            self.ActionSkill1Description = htmlElement.contents[firstSkillDescIndex].string.encode('utf8').strip().replace('\n', '').replace('\r', '')

            if firstSkillTableIndex: #Not all characters have a magnification/evaluation block
                rows = table_list[firstSkillTableIndex].find('tbody').find_all('tr')
                if len(rows) > 0 and rows[0].find('td').find('div'): #Only some magnifications are wrapped in divs
                    if rows[0].find('td').find('div').contents[0] and rows[0].find('td').find('div').contents[0].string:
                        self.ActionSkill1Magnification = rows[0].find('td').find('div').contents[0].string.encode('utf8').strip().replace('\n', '').replace('\r', '')
                    else:
                        print rows[0].find('td')
                        self.ActionSkill1Magnification = rows[0].find('td').find('div').contents[0].string.encode('utf8').strip().replace('\n', '').replace('\r', '')
                else:
                    self.ActionSkill1Magnification = ''
                if len(rows) > 1 and rows[1].find('td').string: #not all skills have an evaluation
                    self.ActionSkill1Evaluation = rows[1].find('td').string.encode('utf8').strip().replace('\n', '').replace('\r', '')
                else:
                    self.ActionSkill1Evaluation = ''
            else:
                print 'No Skill evaluation/magnifications found, character %s' % self.Id
                self.ActionSkill1Magnification = "UNKNOWN"
                self.ActionSkill1Evaluation = "UNKNOWN"



            self.ActionSkill2Name = htmlElement.contents[secondSkillNameIndex].contents[0].string.encode('utf8').strip().replace('\n', '').replace('\r', '')
            self.ActionSkill2SPCost = htmlElement.contents[secondSkillSpIndex].string.encode('utf-8').strip().replace('\n', '').replace('\r', '')

            if secondSkillSpReducedIndex:
                self.ActionSkill2ReducedSPCost = htmlElement.contents[secondSkillSpReducedIndex].string.encode('utf-8').strip().replace('\n', '').replace('\r', '').replace('(', '').replace(')', '')


            self.ActionSkill2Description = htmlElement.contents[secondSkillDescIndex].string.encode('utf8').strip().replace('\n', '').replace('\r', '')

            if secondSkillTableIndex:
                rows = table_list[secondSkillTableIndex].find('tbody').find_all('tr')
                if  len(rows) > 0 and rows[0].find('td').find('div'): #Only some magnifications are wrapped in divs
                    self.ActionSkill2Magnification = rows[0].find('td').find('div').contents[0].string.encode('utf8').strip().replace('\n', '').replace('\r', '')
                else:
                    self.ActionSkill2Magnification = ''

                if len(rows) > 1 and rows[1].find('td').string: #not all skills have an evaluation
                    self.ActionSkill2Evaluation = rows[1].find('td').string.encode('utf8').strip().replace('\n', '').replace('\r', '')
                else:
                    self.ActionSkill2Evaluation = ''
            else:
                print 'No Skill evaluation/magnifications found, character %s' % self.Id
                self.ActionSkill2Magnification = "UNKNOWN"
                self.ActionSkill2Evaluation = "UNKNOWN"
        except Exception as ex:
            print 'Offending character %s' % self.Id
            print '%s %s' % (len(h3_list), secondSkillDescIndex)
            # print htmlElement.contents
            raise

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)

    def __unicode__(self):
        return str(self.__dict__)


class Weapon(object):
    def __init__(self, htmlElement, classId): #Note, we will merge this with the character data later to get english names, owners, etc.

        self.ClassId = classId
        self.Class = getClassFromId(classId)

        #Initialize as EMPTY
        self.Attack = ''
        self.Defense = ''
        self.Crit = ''
        self.Effect = ''
        self.Attribute = ''

        #Most data comes from the weapon list pages, which sits in a nice table structured format
        weaponCells = htmlElement.find_all('td')

        for i in range(len(weaponCells)):
            weaponCell = weaponCells[i]
            if i is 0: ##1st td name/id/ingestionUrl
                anchor =  weaponCell.find('a')

                if anchor:
                    self.IngestionUrl = '/%s' % anchor['href']
                    if self.IngestionUrl:
                        self.Id = self.IngestionUrl[self.IngestionUrl.index('=') + 1:].encode('utf-8')
                        print 'Loading Weapon %s' % self.Id
                    if anchor.string:
                        self.RawName = anchor.string.encode('utf-8').strip().replace('\r', '').replace('\n', '')

                else:
                    print 'Unable to find weapon url'

            innerValue = 'UNKNOWN'
            if i is 7: #this td is of a different format, so we handle it possibly first
                self.Passives = []
                for element in weaponCell.contents:
                    if element.string:
                        #translate it to text Only
                        elementText = element.string.encode('utf-8').strip().replace('\r', '').replace('\n', '')
                        if elementText and '<br>' not in elementText:
                            self.Passives.append(elementText)
            else: #otherwise we convert it to the well known value
                innerValue = weaponCell.string

            if innerValue:
                innerValue = innerValue.encode('utf-8').strip().replace('\r', '').replace('\n', '')
                #note that we skip iteration index 1, as it is just a place holder in the site
                if i is 2:
                    self.Attack = innerValue
                if i is 3:
                    self.Defense = innerValue
                if i is 4:
                    self.Crit = innerValue
                if i is 5:
                    self.Effect = innerValue
                if i is 6:
                    self.Attribute = innerValue

        # #HTML Structue for Weapon Specific page
        # #ImageUrl = div/class=frame -> img/src
        # #Rarity = 1st table->2nd tr->1st td -> {value}
        # #Stats = 2nd table->2nd tr->tds=atk/def/crit/effect/element
        # #Passives = 1st ul -> li={value}
        # #Weapon Skill -> span/class=sp-> -1 is name, +1 is cost, +2/+3 is description (or reduced sp, if its a span)
        # #Weapon Evaluation -> skill description + 1 -> 1st tr -> 1st td -> {value}
        #
        # #First find the wrapping weapon div
        # htmlElement = htmlElement.find('div', {'id':'weapon'})
        #
        # imageDiv = htmlElement.find('div', {'class':'frame'})
        # if imageDiv:
        #     self.ImageUrl = imageDiv.find('img')['src']
        # else:
        #     self.ImageUrl = ''
        #
        # rarityTableRows = htmlElement.find('table').find_all('tr')
        # if rarityTableRows and len(rarityTableRows) > 1:
        #     self.Rarity = rarityTableRows[1].find('td').string.encode('utf-8').strip().replace('\n', '').replace('\r', '')

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)

    def __unicode__(self):
        return str(self.__dict__)
