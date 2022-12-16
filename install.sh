sudo apt-get update -y && sudo apt-get upgrade -y
sudo apt-get install gfortran -y
sudo apt-get install python3-pip -y

pip install pip-tools
pip install numpy

pip-compile requirements.in && pip-compile requirements-dev.in
pip-sync requirements.txt && pip-sync requirements-dev.txt
pip install -r requirements.txt
pip install -r requirements-dev.txt