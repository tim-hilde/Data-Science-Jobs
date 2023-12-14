#!/bin/zsh

set -e

BASEDIR=$(dirname "$0")

cd $BASEDIR
/usr/local/bin/python3 "./scraping.py"

/usr/local/bin/python3 "./add_info.py"

cd ..

DATUM=$(date +"%d.%m.%Y")
git add . > /dev/null
git commit -a -m "$DATUM Scraping" > /dev/null
git push --quiet > /dev/null