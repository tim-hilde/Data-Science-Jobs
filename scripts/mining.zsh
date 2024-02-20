#!/bin/zsh

set -e

BASEDIR=$(dirname "$0")

cd $BASEDIR
rm log.txt
/usr/local/bin/python3 "./scraping.py" &>> log.txt

/usr/local/bin/python3 "./add_info.py" &>> log.txt

cd ..
jupyter execute "notebooks/01-Statistics.ipynb" "notebooks/02-Analysis.ipynb" "notebooks/03-Gehalt.ipynb" &>> log.txt

DATUM=$(date +"%d.%m.%Y")
git add . > /dev/null
git commit -a -m "$DATUM Scraping" > /dev/null
git push --quiet &>> scripts/log.txt