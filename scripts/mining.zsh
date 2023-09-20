#!/bin/zsh
BASEDIR=$(dirname "$0")

cd $BASEDIR
python3 ./scraping.py

python3 ./add_info.py

DATUM=$(date +"%d.%m.%Y")
git add .
git commit -a -m "$DATUM Scraping"
git push