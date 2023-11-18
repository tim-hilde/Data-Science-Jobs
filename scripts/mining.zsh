#!/bin/zsh

set -e

BASEDIR=$(dirname "$0")

cd $BASEDIR
/usr/local/bin/python3 "./scraping.py"

/usr/local/bin/python3 "./add_info.py"

cd ..
cd notebooks

jupyter nbconvert --execute --to notebook --inplace "01-Statistics.ipynb" > /dev/null 2>&1
jupyter nbconvert --execute --to notebook --inplace "02-Analysis.ipynb" > /dev/null 2>&1
jupyter nbconvert --execute --to html "02-Analysis.ipynb" --output-dir="../output" --output "Analysis" > /dev/null 2>&1

cd ..

DATUM=$(date +"%d.%m.%Y")
git add . > /dev/null
git commit -a -m "$DATUM Scraping" > /dev/null
git push --quiet 