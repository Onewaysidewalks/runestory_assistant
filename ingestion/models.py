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

    def mergeCharacterDetailFromShironeko(self, htmlElement):
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
        firstLeaderSkillNameIndex = 1
        firstLeaderSkillDescIndex = 0
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

            if p_list[0].has_attr('class'): #we know leader skill p tags dont have classes, this must mean there is an offset needed
                print 'false <P> tag found, adjusting leader skill description indices'
                firstLeaderSkillDescIndex = 1
                secondLeaderSkillDescIndex = 2

            if len(h3_list) < 7: #not enough to have two leader skills
                secondLeaderSkillNameIndex = None
                secondLeaderSkillDescIndex = None
                firstSkillNameIndex = 2
                firstSkillDescIndex = 1
                secondSkillNameIndex = 3
                secondSkillDescIndex = 2

            #set the skill indexes based on their adjacent SP-classed span
            foundFirst = False
            firstWrappingSpCostElementIndex = None
            secondWrappingSpCostElementIndex = None
            for elementIndex in range(len(htmlElement.contents)):
                if 'class="sp"' in '%s' % htmlElement.contents[elementIndex]:
                    print 'sp class found at %s. element: %s' % (elementIndex, str(htmlElement.contents[elementIndex]))
                    if foundFirst:
                        if '<p>' in str(htmlElement.contents[elementIndex]):
                            #The sp bits are wrapped in a <p> tag. when they are, there are at MOST 3 elements in the tag. the SP marker,
                            #the unaltered cost, and the reduced cost. no additional indicies are needed
                            secondWrappingSpCostElementIndex = elementIndex

                        secondSkillSpIndex = elementIndex + 1

                        secondSkillDescIndex = elementIndex + 2
                        #Now we have to see if the desc index is a span (if it is, its actually the reduced SP cost, and the next one is the desc)
                        if 'span' in str(htmlElement.contents[secondSkillDescIndex]):
                            print 'Found Reduced SP Cost skill 2'
                            secondSkillSpReducedIndex = secondSkillDescIndex
                            secondSkillDescIndex = secondSkillDescIndex + 2

                        secondSkillNameIndex = elementIndex - 2
                    else:
                        if '<p>' in str(htmlElement.contents[elementIndex]):
                            #The sp bits are wrapped in a <p> tag. when they are, there are at MOST 3 elements in the tag. the SP marker,
                            #the unaltered cost, and the reduced cost. no additional indicies are needed
                            firstWrappingSpCostElementIndex = elementIndex

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
                self.LeaderSkill1Name = h3_list[firstLeaderSkillNameIndex].string.encode('utf8').strip().replace('\n', '').replace('\r', '')
            elif len(h3_list[1].contents) > 1:
                self.LeaderSkill1Name = h3_list[firstLeaderSkillNameIndex].contents[0].string.encode('utf-8').strip().replace('\n', '').replace('\r', '')
            else:
                self.LeaderSkill1Name = ''
                print 'No leader skill 1 name, character %s, element:%s' % (self.Id, h3_list[firstLeaderSkillNameIndex])

            if p_list[firstLeaderSkillDescIndex].string:
                self.LeaderSkill1Description = p_list[firstLeaderSkillDescIndex].string.encode('utf-8').strip().replace('\n', '').replace('\r', '')
            else:
                self.LeaderSkill1Description = ''
                print 'No leader skill 1 description, character %s, element %s' % (self.Id, p_list[firstLeaderSkillDescIndex])

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
                    print 'No leader skill 2 descriptioni, character %s, element %s' % (self.Id, p_list[secondLeaderSkillDescIndex])
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

            if firstWrappingSpCostElementIndex:
                #a wrapping <P> was found for the sp bits, which is in a well known format of <P><span>SP</span>{value}<span>{reduced value}</span>
                self.ActionSkill1SPCost = htmlElement.contents[firstWrappingSpCostElementIndex].contents[1].string.encode('utf-8').strip().replace('\n', '').replace('\r', '')
                if len(htmlElement.contents[firstWrappingSpCostElementIndex]) > 2:
                    self.ActionSkill1ReducedSPCost = htmlElement.contents[firstWrappingSpCostElementIndex].contents[2].string.encode('utf-8').strip().replace('\n', '').replace('\r', '').replace('(', '').replace(')', '')
            else:
                self.ActionSkill1SPCost = htmlElement.contents[firstSkillSpIndex].string.encode('utf-8').strip().replace('\n', '').replace('\r', '')
                if firstSkillSpReducedIndex:
                    self.ActionSkill1ReducedSPCost = htmlElement.contents[firstSkillSpReducedIndex].string.encode('utf-8').strip().replace('\n', '').replace('\r', '').replace('(', '').replace(')', '')

            if htmlElement.contents[firstSkillDescIndex].string: #if the inner contents isnt html, than simply represent as a string
                self.ActionSkill1Description = htmlElement.contents[firstSkillDescIndex].string.encode('utf8').strip().replace('\n', '').replace('\r', '')
            else:
                print 'found html based skill description, parsing...'
                self.ActionSkill1Description = ''
                for content in htmlElement.contents[firstSkillDescIndex]:
                    if content.string and '<br' not in content.string.encode('utf8'):
                        self.ActionSkill1Description = '%s %s' % (self.ActionSkill1Description, content.string.encode('utf8').strip().replace('\n', '').replace('\r', ''))

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
                self.ActionSkill1Magnification = "UNKNOWN"
                self.ActionSkill1Evaluation = "UNKNOWN"

            #Parse second action skill...
            self.ActionSkill2Name = htmlElement.contents[secondSkillNameIndex].contents[0].string.encode('utf8').strip().replace('\n', '').replace('\r', '')

            if secondWrappingSpCostElementIndex and htmlElement.contents[secondWrappingSpCostElementIndex].contents and len(htmlElement.contents[secondWrappingSpCostElementIndex].contents) > 1:
                #a wrapping <P> was found for the sp bits, which is in a well known format of <P><span>SP</span>{value}<span>{reduced value}</span>
                self.ActionSkill2SPCost = htmlElement.contents[secondWrappingSpCostElementIndex].contents[1].string.encode('utf-8').strip().replace('\n', '').replace('\r', '')
                if len(htmlElement.contents[secondWrappingSpCostElementIndex]) > 2:
                    self.ActionSkill2ReducedSPCost = htmlElement.contents[secondWrappingSpCostElementIndex].contents[2].string.encode('utf-8').strip().replace('\n', '').replace('\r', '').replace('(', '').replace(')', '')
            else:
                self.ActionSkill2SPCost = htmlElement.contents[secondSkillSpIndex].string.encode('utf-8').strip().replace('\n', '').replace('\r', '')
                if secondSkillSpReducedIndex:
                    self.ActionSkill2ReducedSPCost = htmlElement.contents[secondSkillSpReducedIndex].string.encode('utf-8').strip().replace('\n', '').replace('\r', '').replace('(', '').replace(')', '')

            if htmlElement.contents[secondSkillDescIndex].string: #if the inner contents isnt html, than simply represent as a string
                self.ActionSkill2Description = htmlElement.contents[secondSkillDescIndex].string.encode('utf8').strip().replace('\n', '').replace('\r', '')
            else:
                print 'found html based skill description, parsing...'
                self.ActionSkill2Description = ''
                for content in htmlElement.contents[secondSkillDescIndex]:
                    if content.string and '<br' not in content.string.encode('utf8'):
                        self.ActionSkill2Description = '%s %s' % (self.ActionSkill2Description, content.string.encode('utf8').strip().replace('\n', '').replace('\r', ''))

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

    def mergeCharacterDetailFromFamitsu(self, htmlElement):
        #We pull the following data out of the famitsu site:
        #1) skill images
        #2) rankings

        #First we check for a 404 like page. This is known by the title of the page being "Pages"
        if htmlElement.find('title').text and 'Pages' in htmlElement.find('title').text:
            print "unable to find famitsu page for %s: %s" % (self.Id, str(self.RawName))
            return

        #search for all images, then filter by src/alt of image
        skillImages = []
        imageElements = htmlElement.find_all('img')
        for imageElement in imageElements:
            src = imageElement['src']
            if imageElement.has_attr('alt'): #gifs are hidden with an altTag of NameAS1.gif
                alt = imageElement['alt'].encode('utf-8')
                if 'AS1' in alt or 'AS2' in alt:
                    skillImages.append(src)
            elif 'ref_upload' in src:
                skillImages.append(src)
        if len(skillImages) == 0:
            print 'No images found for character: %s' % self.Id
        else:
            print 'Found %d images for skills: %s' % (len(skillImages), skillImages)

        if len(skillImages) > 0:
            self.ActionSkill1Image = skillImages[0]
        if len(skillImages) > 1:
            self.ActionSkill2Image = skillImages[1]


        #to get ranking, we find all divs with class ie5, and iterate their tables looking for a small enough cell
        divs = htmlElement.find_all('div', {'class': 'ie5'})

        for characterRankDiv in divs:
            foundRank = False
            #now that we have the div, we iterate its tables looking for a 3 or less character table cell. Should one exist, we assume thats the rank!
            for tableCell in characterRankDiv.find_all('td'):
                if tableCell.text and len(tableCell.text) <= 3 and any(rank in tableCell.text for rank in [ 'S', 'A', 'B', 'C', 'D']):
                    self.JpRanking = tableCell.text
                    print 'Setting rank %s' % self.JpRanking
                    foundRank = True
                    break #we assum that the first td of that length is the only one that could have a grade, so we stop at that point
            if foundRank:
                break; #we are done


        # h3s = htmlElement.find_all('h3')
        #
        # for h3 in h3s:
        #     if h3.string and "App" in h3.string:
        #         print 'found app header, pulling rank from subsequent div'
        #         h3Index = htmlElement.findAll().index(h3)
        #         print 'h3 index %s' % h3Index
        #         containingDiv = htmlElement.findAll()[h3Index + 1]
        #
        #         if containingDiv:
        #             print 'found containing div, pulling rank from first td in div'
        #             possibleRank = containingDiv.find('td').text
        #
        #             if len(possibleRank) > 3: #we assume in this case, that there is no ranking for the character
        #                 print 'Invalid ranking found for id:%s, raw name: %s' % (self.Id, str(self.RawName))
        #             else:
        #                 self.JpRanking = possibleRank
        #                 print 'Setting rank %s' % self.JpRanking
        #
        #             break #we know that the first app is the only one that could have a grade, so we stop at that point

        if not hasattr(self, 'JpRanking'):
            print 'No ranking found for id: %s, raw name: %s' % (self.Id, str(self.RawName))

        return

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
    def mergeWeaponDetailFromShironeko(self, htmlElement):
        # #HTML Structue for Weapon Specific page
        # #ImageUrl = div/class=frame -> img/src
        # #Rarity = 1st table->2nd tr->1st td -> {value}
        # #Stats = 2nd table->2nd tr->tds=atk/def/crit/effect/element
        # #Passives = 1st ul -> li={value}
        # #Weapon Skill -> span/class=sp-> -2 is name, +1 is cost, +2/+3 is description (or reduced sp, if its a span)
        # #Weapon Evaluation -> skill description + 1 -> 1st tr -> 1st td -> {value}

        #First find the wrapping weapon div
        htmlElement = htmlElement.find('div', {'id':'weapon'})

        tables = htmlElement.find_all('table', recursive=False)

        #Pull image Url
        imageDiv = htmlElement.find('div', {'class':'frame'})
        if imageDiv:
            self.ImageUrl = imageDiv.find('img')['src']
        else:
            self.ImageUrl = ''

        #Pull Rarity
        rarityTableRows = tables[0].find_all('tr') #first table always contains rarity
        if rarityTableRows and len(rarityTableRows) > 1:
            self.Rarity = rarityTableRows[1].find('td').string.encode('utf-8').strip().replace('\n', '').replace('\r', '')

        #Pull Weapon Skill SP, skill, name
        for elementIndex in range(len(htmlElement.contents)):
            if 'class="sp"' in '%s' % htmlElement.contents[elementIndex]:
                print 'found weapon action skill sp cost'
                #this element should be a span, as such, you know the following value is a cost
                self.WeaponSkillRawName = htmlElement.contents[elementIndex - 2].string.encode('utf-8').strip().replace('\n', '').replace('\r', '')
                self.WeaponSkillSpCost = htmlElement.contents[elementIndex + 1].string.encode('utf-8').strip().replace('\n', '').replace('\r', '')

                weaponSkillSummaryIndex = elementIndex + 2
                if 'span' in str(htmlElement.contents[elementIndex + 2]): #this is a reduced sp cost
                    weaponSkillSummaryIndex = elementIndex + 3

                self.WeaponSkillSummary = htmlElement.contents[weaponSkillSummaryIndex].string.encode('utf-8').strip().replace('\n', '').replace('\r', '')

        if len(tables) > 3: #there are at least 4 tables, the third contains skill magnifications
            magnificationAndEvaluationTable = tables[2]

            if len(magnificationAndEvaluationTable.find_all('td')) > 1: #if there are 2 cells, then it has both an evaluation and a magnification
                #the magnification/evaluation table is strucutred in two cells. the first cell is the magnification, the second is the description
                magnificationCell = magnificationAndEvaluationTable.find_all('td')[0]

                self.WeaponSkillBaseMagnification = magnificationCell.contents[0].string.encode('utf-8').strip().replace('\n', '').replace('\r', '')
                if len(magnificationCell.contents) > 1 and magnificationCell.contents[1].string:
                    self.WeaponSkillElementMagnification = magnificationCell.contents[1].string.encode('utf-8').strip().replace('\n', '').replace('\r', '')

                descriptionCell = magnificationAndEvaluationTable.find_all('td')[1]

                self.WeaponSkillDescription = ''
                for content in descriptionCell.contents:
                    if content.string:
                        self.WeaponSkillDescription = '%s %s' % (self.WeaponSkillDescription, content.string.encode('utf-8').strip().replace('\n', '').replace('\r', ''))
            else:
                #only one cell available, only an evaluation
                descriptionCell = magnificationAndEvaluationTable.find_all('td')[0]

                self.WeaponSkillDescription = ''
                for content in descriptionCell.contents:
                    if content.string:
                        self.WeaponSkillDescription = '%s %s' % (self.WeaponSkillDescription, content.string.encode('utf-8').strip().replace('\n', '').replace('\r', ''))

        if not hasattr(self, 'WeaponSkillRawName'):
            self.WeaponSkillRawName = None

        if not hasattr(self, 'WeaponSkillSpCost'):
            self.WeaponSkillSpCost = None

        if not hasattr(self, 'WeaponSkillSummary'):
            self.WeaponSkillSummary = None

        if not hasattr(self, 'WeaponSkillBaseMagnification'):
            self.WeaponSkillBaseMagnification = None

        if not hasattr(self, 'WeaponSkillElementMagnification'):
            self.WeaponSkillElementMagnification = None

        if not hasattr(self, 'WeaponSkillDescription'):
            self.WeaponSkillDescription = None

        #we remove the passive that is the weapon skill, as that will have its own section dedicated to it
        if self.WeaponSkillRawName in self.Passives:
            self.Passives.remove(self.WeaponSkillRawName)



        return

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)

    def __unicode__(self):
        return str(self.__dict__)
