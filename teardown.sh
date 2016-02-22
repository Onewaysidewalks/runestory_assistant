#!/bin/bash

echo 'tearing down instances in heroku'
heroku ps:scale web=0
