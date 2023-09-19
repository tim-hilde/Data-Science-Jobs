#!/bin/zsh

DATUM=$(date +"%d.%m.%Y")
git add .
git commit -a -m "$DATUM Scraping"
git push

# python3 "./scraping.py" 

# python3 "./add_info.py"