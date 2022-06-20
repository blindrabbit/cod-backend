# cod-backend
 
sudo apt update
sudo apt upgrade
sudo apt install python3-venv build-essential python3-dev python3-pip python3-setuptools python3-wheel python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info

cd ~
git clone https://github.com/teddysun/lamp.git
cd lamp/
sudo chmod 755 *.sh
sudo ./lamp.sh

cd ~
git clone https://github.com/blindrabbit/Campus-ON-Demand-RENAN
cd Campus-ON-Demand-RENAN
python3 -m venv venv
source venv/bin/activate

pip install -r ../requirements.txt
pip install Flask

LINUX:
export FLASK_ENV=development
export OS_CLIENT_CONFIG_FILE="clouds.yaml"

WINDOWS:
$env:OS_CLIENT_CONFIG_FILE="clouds.yaml"
$env:FLASK_ENV="development"

cd .\Campus-ON-Demand-renan\app
python -m flask run --host=0.0.0.0 --debugger --reload
