#!/bin/bash
## This script was written by Shaun, KT2O
## edit this script to enable features which you would need

## Install HomeBrew (visit https://brew.sh) if you don't have it already
## Uncomment the next line as needed
#/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

## Install Updated Python (minimum 3.11)
##
brew install python@3.11
brew install python-tk@3.11
## fix any broken links
brew link --overwrite python@3.11

## If you do not have git installed:
## Uncomment the next line as needed
#brew install git

## install deps; change pip command to match the python version install
pip3.11 install html5lib bs4 tk pandas croniter markdown tcl
## Check for existing installation
if [[ -d ~/ASC/.git ]] ; then
        cd ~/ASC
        echo Pulling latest changes
        git pull 
else
    echo Cloning repository...
    git clone https://github.com/tkocou/ASC
    cd ~/ASC
fi


## Run the application - note the python3 being run here MUST match the version used above otherwise it will break.
python3.11 ASC-DB.py &

## Add an alias for ease of use 
## Add the following to your ~/.zshrc
##
## Uncomment the next line and edit the line as needed. Replace '/full/path/here/'
## with your machine's path to the ASC directory
#alias ASC='python3.11 /full/path/here/ASC/ASC-DB.py'