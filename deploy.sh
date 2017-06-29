#!/bin/bash

if [ -z $1 ]; then
	echo -e "\033[1;31m Wrong option \033[0m"
	echo -e "\033[1;31m USAGE: bash $0 dest_dir \033[0m"
fi

dest=$1

if [ -d $dest ]; then
	echo "Deploy (copy) postgrespy to destination directory: $1"
	cp README.md $dest
	cp models.py $dest
	cp __init__.py $dest
	cp db.py $dest
	cp fields.py $dest
	cp queries.py $dest
else
	echo -e "\033[1;31m Invalid directory \033[0m"
fi
