sudo apt-get update -y && sudo apt-get upgrade -y
sudo apt-get install gfortran -y
sudo apt-get install python3-pip -y

pip-sync requirements.txt requirements-dev.txt