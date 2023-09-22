#!/bin/zsh
BASEDIR=$(dirname "$0")

cd $BASEDIR
/usr/local/bin/python3 "./scraping.py"

/usr/local/bin/python3 "./add_info.py"

DATUM=$(date +"%d.%m.%Y")
git add .
git commit -a -m "$DATUM Scraping"
git push