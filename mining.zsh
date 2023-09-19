#!/bin/zsh

datum= date +%d.%m.%Y
git add .
git commit -a -m datum

# python3 "./scraping.py" 

# python3 "./add_info.py"