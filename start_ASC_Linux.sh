#!/usr/bin/env bash
## The script is written for a Linux Mint / Ubuntu / Debian system
## feel free to alter it as you need to

#echo "This script is derived from a script written by ParisNeo"
#echo "It is used with the permission of ParisNeo (https://github.com/ParisNeo/lollms-webui)"

sleep 2

if ping -q -c 1 google.com >/dev/null 2>&1; then
    echo -e "\e[32mInternet Connection working fine\e[0m"
    # Install git
    echo -n "Checking for Git..."
    if command -v git > /dev/null 2>&1; then
      echo "is installed"
    else
      read -p "Git is not installed. Would you like to install Git? [Y/N] " choice
      if [ "$choice" = "Y" ] || [ "$choice" = "y" ] ; then
        echo "Installing Git..."
        sudo apt update
        sudo apt install -y git
      else
        echo "Please install Git and try again."
        exit 1
      fi
    fi
    ## some other packages which should be installed
    sudo apt update
    sudo apt -y install python3 python-is-python3 python3-tk
    pip install croniter pandas html5lib bs4 markdown tcl

    ## move to the $HOME directory
    cd ~

    # Check if git directory exists
    if [[ -d ./ASC/.git ]] ; then
        cd ./ASC
        echo Pulling latest changes
        git pull

    ## Check if we have an older ASC installation
    elif  [[ -d ./ASC ]] ; then
        echo Saving database and removing old installation
        cp ./ASC/asc.db .
        rm -rf ./ASC
        git clone https://github.com/tkocou/ASC ./ASC
        mv ./asc.db ./ASC
        cd ./ASC
        
    ## no ASC, then clone the repository
    else
        echo Cloning repository...
        git clone https://github.com/tkocou/ASC ./ASC
        cd ./ASC
    fi

     # Install Python 3.10 and pip
    echo -n "Checking for python3.10..."
    if command -v python3.10 > /dev/null 2>&1; then
      echo "is installed"
    else
      read -p "Python3.10 is not installed. Would you like to install Python3.10? [Y/N] " choice
      if [ "$choice" = "Y" ] || [ "$choice" = "y" ]; then
        echo "Installing Python3.10..."
        sudo apt update
        sudo apt install -y python3.10 python3.10-venv
      else
        echo "Please install Python3.10 and try again."
        exit 1
      fi
    fi

    # Install venv module
    echo -n "Checking for venv module..."
    if python3.10 -m venv env > /dev/null 2>&1; then
      echo "is installed"
    else
      read -p "venv module is not available. Would you like to install it? [Y/N] " choice
      if [ "$choice" = "Y" ] || [ "$choice" = "y" ]; then
        echo "Installing venv module..."
        sudo apt update
        sudo apt install -y python3.10-venv
      else
        echo "Please install venv module and try again."
        exit 1
      fi
    fi
# Create a new virtual environment
    echo -n "Creating virtual environment..."
    python3.10 -m venv env
    if [ $? -ne 0 ]; then
      echo "Failed to create virtual environment. Please check your Python installation and try again."
      exit 1
    else
      echo "is created"
    fi
else
    echo -e "\e[32mMissing an Internet Connection\e[0m"
fi

# Activate the virtual environment
echo -n "Activating virtual environment..."
source env/bin/activate
echo "is active"

# Install the required packages
echo "Installing requirements..."
python3.10 -m pip install pip --upgrade
python3.10 -m pip install beautifulsoup4 --index-url https://files.pythonhosted.org/packages/57/f4/a69c20ee4f660081a7dedb1ac57f29be9378e04edfcb90c526b923d4bebc/beautifulsoup4-4.12.2-py3-none-any.whl
python3.10 -m pip install --upgrade -r ~/ASC/requirements.txt



## Check if repository has already been cloned
## regardless if there is an Internet Connection
cd ~
if [ -f ~/ASC/ASC-DB.py ] ;then
    cd ~/ASC
    # Launch the Python application
    python ASC-DB.py &
fi

## The Linux desktop should now have a launcher installed
