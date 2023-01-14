sudo apt-get update -y && sudo apt-get upgrade -y
sudo apt-get install gfortran -y
sudo apt-get install python3-pip -y

pip install pip-tools
pip install numpy

pip-sync requirements.txt requirements-dev.txt