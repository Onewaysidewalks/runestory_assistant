import beautifulsoup_helper
import models
from bs4 import BeautifulSoup

#Stuff needed for google translate api
import os
import time
from apiclient.discovery import build
import urllib

#Stuff needed for file output
import yaml

#Poor mans Configuration!
BASE_URL = 'http://shironeko.me'
RARITIES = [ '4', '3', '2', '1']
CHARACTER_TYPES = [1, 2, 3, 4, 5, 6, 7]
CHARACTER_CLASSES = [1, 2, 3, 4, 5, 6, 7, 8]
TARGET_LANGUAGE = 'en'
SOURCE_LANGUAGE = 'ja'
OUTPUT_LOCATION = 'build/basedata.yaml'

def getCharacters():
    #NOTE: There are several pages of characters for each character class
    # as such, we will just guess up to 10 pages of characters, and stop iteration if no characters exist on a page
    #Similarly, we dont know the rarity of each character without search for the rarity
    #explicity, so we must iterate once for each rarity to pull that information
    #Similarly, we dont know the type of character (AKA Defender), so we must use that as a search term too

    characters = []
    for classId in CHARACTER_CLASSES:
        for characterType in CHARACTER_TYPES:
            for rarity in RARITIES:
                for page in range(10):
                    if page == 0:
                        continue #there is no page 0

                    parser = beautifulsoup_helper.getParserForUrl(BASE_URL + '/character_list?id=%d&type=%d&rare=%s&p=%d' % (classId, characterType, rarity, page))

                    characterRows = parser.find_all(class_='character')

                    for charRow in characterRows:
                        character = models.Character(charRow, classId, rarity, characterType)

                        print 'merging character specific details %s' % character.Id
                        loadMoreCharacterDetail(character)

                        characters.append(character)
                        # break # UNCOMMENT THIS FOR TESTING PURPOSES ONLY
                    else:
                        break #if there are no character rows, break the iteration early

                    # break#REMOVE
                # break #REMOVE
            # break #REMOVE
        # break #REMOVE

    return characters

def loadMoreCharacterDetail(character):
    #NOTE: This will load a characters specific page to pull even more information about each character
    #Using this more detailed information, we will merge the extra detail onto the character object itself
    #so we have a single full representation of the character

    if not character.IngestionUrl:
        print "Unable to load character specific detail, %s: %s" % (character.Id, character.IngestionUrl)
        return
    parser = beautifulsoup_helper.getParserForUrl(BASE_URL + character.IngestionUrl)

    character.mergeCharacterDetailHtml(parser)

def saveCharactersToFile(location, characters):
    #First, since we are saving as a yaml file, dilenated by class
    #we must group together each character by its class

    characterFileData = dict()
    characterFileData['Characters'] = dict() #root level for character data

    #initialize the data with empty lists for each class
    for classId in CHARACTER_CLASSES:
        characterFileData['Characters'][models.getClassFromId(classId)] = dict()

    for character in characters:
        characterFileData['Characters'][character.Class]['%s' % (character.Id)] = character

    #Now write the file in all its yamlly glory (first creating the directory if necessary)
    if not os.path.exists(os.path.dirname(location)):
        try:
            os.makedirs(os.path.dirname(location))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    with open(location, 'w') as yaml_file: #We use safe_dump, to remove the !!python declarations from the file
        yaml_file.write(yaml.dump(characterFileData, encoding='utf-8', default_flow_style=False, allow_unicode=True))


def translateCharacters(characters, language):

    translatedCharacters = []

    apiKey = os.environ['GOOGLE_TRANSLATE_API_KEY']

    service = build('translate', 'v2', developerKey=apiKey)

    for character in characters:

        print 'performing translations for character id:%s' % character.Id

        #Format is name##passive##passive##passive...
        rawPayload = 'n:%s##' % character.RawName
        for passive in character.Passives:
            rawPayload = rawPayload + 'p:%s##' % passive

        #first skill data
        rawPayload = rawPayload + '1d:%s##1e:%s##1m:%s##1n:%s##1s:%s##' % (character.ActionSkill1Description, character.ActionSkill1Evaluation, character.ActionSkill1Magnification, character.ActionSkill1Name, character.ActionSkill1SPCost)

        #second skill data
        rawPayload = rawPayload + '2d:%s##2e:%s##2m:%s##2n:%s##2s:%s##' % (character.ActionSkill2Description, character.ActionSkill2Evaluation, character.ActionSkill2Magnification, character.ActionSkill2Name, character.ActionSkill2SPCost)

        #first leader skill
        rawPayload = rawPayload + 'l1d:%s##l1n:%s##' % (character.LeaderSkill1Description, character.LeaderSkill1Name)

        #second leader skill
        rawPayload = rawPayload + 'l2d:%s##l2n:%s##' % (character.LeaderSkill2Description, character.LeaderSkill2Name)

        #motif weapon name
        rawPayload = rawPayload + 'mt:%s##' % (character.MotifWeaponName)

        try:
            #Query for the translated text (this handles url encoding for us!)
            result = service.translations().list(source=SOURCE_LANGUAGE, target=TARGET_LANGUAGE,q=rawPayload).execute()
        except:
            #rate limited, sleep and try again
            print 'RATE LIMITED, SLEEPING 100 SECONDS'
            time.sleep(100)
            result = service.translations().list(source=SOURCE_LANGUAGE, target=TARGET_LANGUAGE,q=rawPayload).execute()

        translatedResult = result['translations'][0]['translatedText'].encode('utf-8')
        translatedParts = translatedResult.split('##')

        #Now we have the appropriate text, time to map it back onto the character model
        translatedPassives = []

        for pos in range(len(translatedParts)):
            text = ' '.join(translatedParts[pos].strip().splitlines())
            if text and len(text) > 0:

                if ':' not in text:
                    print 'ERROR: ":" not in text %s for translation'
                    continue

                index = text.index(':')

                if index is len(text):
                    print 'no data found for this entry %s character %s' % (text, character.Id)
                    continue #no data, continue

                value = text[text.index(':')+1:].strip().replace('\n', '') #substring starting at the 3 position
                if text.lower().startswith('n:'): # name
                    character.Name = value
                elif text.lower().startswith("p:"): #passives
                    translatedPassives.append(value)
                elif text.lower().startswith('1d'): #action skill 1 description
                    character.ActionSkill1Description = value
                elif text.lower().startswith('1e'): #action skill 1 evaluation
                    character.ActionSkill1Evaluation = value
                elif text.lower().startswith('1m'): #action skill 1 magnification
                    character.ActionSkill1Magnification = value
                elif text.lower().startswith('1n'): #action skill 1 name
                    character.ActionSkill1Name = value
                elif text.lower().startswith('1s'): #action skill 1 sp cost
                    character.ActionSkill1SPCost = value
                elif text.lower().startswith('2d'): #action skill 2 description
                    character.ActionSkill2Description = value
                elif text.lower().startswith('2e'): #action skill 2 evaluation
                    character.ActionSkill2Evaluation = value
                elif text.lower().startswith('2m'): #action skill 2 magnification
                    character.ActionSkill2Magnification = value
                elif text.lower().startswith('2n'): #action skill 2 name
                    character.ActionSkill2Name = value
                elif text.lower().startswith('2s'): #action skill 2 sp cost
                    character.ActionSkill2SPCost = value
                elif text.lower().startswith('l1d'): #leader skill 1 name
                    character.LeaderSkill1Description = value
                elif text.lower().startswith('l1n'): #leader skill 1 description
                    character.LeaderSkill1Name = value
                elif text.lower().startswith('l2d'): #leader skill 2 name
                    character.LeaderSkill2Description = value
                elif text.lower().startswith('l2n'): #leader skill 2 description
                    character.LeaderSkill2Name = value
                elif text.lower().startswith('mt'): #motif weapon name
                    character.MotifWeaponName = value

        character.Passives = translatedPassives

    return characters

def main():
    #First we grab a hold of all the character list
    characters = getCharacters()

    #Then we ask googles api for a translation for each character
    characters = translateCharacters(characters, 'en')

    #Save all characters to a data file, for further processing later
    saveCharactersToFile(OUTPUT_LOCATION, characters)

if __name__== '__main__':
    main()
