#!/bin/bash

python3 -m pipenv --python python3 install

systemd_unit="[Unit]\nDescription=My Movie Database\nAfter=network.target\n\n[Service]\nUser=$USER\nEnvironment=\"LC_ALL=C.UTF-8\"\nEnvironment=\"LANG=C.UTF-8\"\nEnvironmentFile=$PWD/env\nWorkingDirectory=$PWD\nExecStartPre=/usr/bin/python3 -m pipenv run $PWD/manage.py migrate\nExecStart=/usr/bin/python3 -m pipenv run $PWD/manage.py runserver\n\n[Install]\nWantedBy=multi-user.target\n"

echo -e $systemd_unit | sudo tee /etc/systemd/system/mymdb.service

sudo systemctl daemon-reload
sudo systemctl enable mymdb.service
sudo systemctl start mymdb.service

echo Installed Successfully.