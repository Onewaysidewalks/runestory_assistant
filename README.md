# Runestory Assistant
This is a site to help gamers playing Colopl's "Runestory" with information about the game, much like a wiki
This project is meant to fill the hole that, while there is a few vastly populated wikis in japanese, there are
none for the global/english version of the game!

## Project Structure
This project is divided into 3 basic pieces:

1. Ingestion - How this project gets a baseline for data
2. Overrides - How others can contribute to the data
3. Website - a site to host the data in a filterable and searchable way

### Ingestion
The ingestion piece is done by scraping a well known japanese wiki for Colopls Shirneko Project (Runestory). The tech used are:

1. Python - I wanted to learn it and so used it for this part of the project. Be gentle :)
2. Beautifulsoup - an excellent library for DOM parsing a websites contents!
3. Google Translate API - used to translate the japanese wiki into broken, but legible, english.

### Overrides
The purpose of this piece of the assistant is to fix and/or correct any data provided from the ingestion pipeline. Example fixes are:

1. Incorrect stats/skills, as Global Runestory differs from the japanese version.
2. Add global exclusive character information, as these will not be in the ingestion based data
3. Fix any translation errors into nicer english, etc.

The overrides are done using basic yaml file merging, and taking precedence to the override.yaml. Note: the merging is done in a strictly add/replace manner, so nothing can be removed with the override file.

Tech used for this:

1. Python - again, one of my first python forays, so be gentle!
2. Pyyaml - seems to be a pretty standard way of manipulating yaml files in pythong

### Website
God save me

- - -

## Repository usage
Follow these guidelines for contribution and usage of the project

### Ingestion
NOTE: THIS COSTS MONEY, BEWARE DANGER DANGER

To run the ingestion piece:

1. `pip install`
  - Installs all required python frameworks for working with Runestory Assistant
2. Add environment variable `GOOGLE_TRANSLATE_API_KEY` with the value of the developerKey from googles developer console
  - this MUST be done in order to get translations to work for ingestion
3. `python -u ingestion/shironeko_scraper.py`
  - Once properly configured, this will run and output a file to `build/basedata.yaml`. This file will be the fully translated raw baseline data

### Overrides
TODO

### Website
To deploy the website a few scripts have been provided for convenience:

1. To deploy: `./deploy.sh`
2. To teardown: `./teardown.sh`
