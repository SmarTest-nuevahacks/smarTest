#!/bin/sh

cd /home
git clone https://github.com/SmarTest-nuevahacks/smarTest.git
cd smarTest
pip3 install -r requirements.txt
python3 main.py