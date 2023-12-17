#!/bin/zsh

set -e

BASEDIR=$(dirname "$0")

cd $BASEDIR
/usr/local/bin/python3 "./scraping.py" &>> log.txt

/usr/local/bin/python3 "./add_info.py" &>> log.txt

cd ..

DATUM=$(date +"%d.%m.%Y")
git add . &>> log.txt
git commit -a -m "$DATUM Scraping" &>> log.txt
git push --quiet &>> log.txt