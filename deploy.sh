#!/bin/bash

#reingest data
#echo 'ingesting data...'
#python -u ingestion/shironeko_scraper.py

#perform overrides
echo 'performing overrides'
python -u overrides/overrides.py

#deploy data file
echo 'deploying data file locally...'
cp 'build/data.yaml' 'website/static/data.yaml'

echo 'creating commit to deploy to heroku...'
echo '$(date) deployment' > deployment.file
git add --all

git commit -m "Deployment Commit"

git push heroku master --force

echo 'removing commit from heroku deployment'
git reset HEAD~1
rm deployment.file

echo 'scaling instances to 1 free instance for heroku...'
heroku ps:scale web=1
