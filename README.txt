Download data archive from https://myaccount.nest.com/mynestdata

# might need to install
sudo apt install python3 python3-venv python3-tk python3-dev

# install nest-graph
git clone git@github.com:AlanRosenthal/nest-graph.git
python3 -m venv .venv/nest_graph
source .venv/nest_graph/bin/activate
python3 setup.py install
nest-graph --help

# example command
## 2019/02
nest-graph --archive ~/Downloads/NEST_DATA.zip --thermostat-id THERMOSTAT_ID --date 2019 02

## all months
nest-graph --archive ~/Downloads/NEST_DATA.zip --thermostat-id THERMOSTAT_ID
