import beautifulsoup_helper
import models
from bs4 import BeautifulSoup

#Stuff needed for google translate api
import os
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
    # as such, we will just guess up to 10 pages of characters, and stop iteration
    #Similarly, we dont know the rarity of each character without search for the rarity
    #explicity, so we must iterate once for each rarity to pull that information
    #Similarly, we dont know the type of character (AKA Defender), so we must use that as a search term too

    characters = []
    for classId in CHARACTER_CLASSES:
        for characterType in CHARACTER_TYPES:
            for rarity in RARITIES:
                for page in range(10):

                    parser = beautifulsoup_helper.getParserForUrl(BASE_URL + '/character_list?id=%d&type=%d&rare=%s&p=%d' % (classId, characterType, rarity, page))

                    characterRows = parser.find_all(class_='character')

                    for charRow in characterRows:
                        character = models.Character(charRow, classId, rarity, characterType)
                        characters.append(character)
                    else:
                        break #if there are no character rows, break the iteration early
    return characters

def saveCharactersToFile(location, characters):
    #First, since we are saving as a yaml file, dilenated by class
    #we must group together each character by its class

    characterFileData = dict()
    characterFileData['Characters'] = dict() #root level for character data

    #initialize the data with empty lists for each class
    for classId in CHARACTER_CLASSES:
        characterFileData['Characters'][models.getClassFromId(classId)] = dict()

    for character in characters:
        if hasattr(character, 'Name'):
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
        rawPayload = '%s##' % character.RawName
        for passive in character.Passives:
            rawPayload = rawPayload + '%s##' % passive

        #Query for the translated text (this handles url encoding for us!)
        result = service.translations().list(source=SOURCE_LANGUAGE, target=TARGET_LANGUAGE,q=rawPayload).execute()

        translatedResult = result['translations'][0]['translatedText'].encode('utf-8')
        translatedParts = translatedResult.split('##')

        #Now we have the appropriate text, time to map it back onto the character model
        translatedPassives = []

        for pos in range(len(translatedParts)):
            text = translatedParts[pos].strip()
            if pos is 0:
                character.Name = text
            elif text and len(text) > 0:
                translatedPassives.append(text)

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
