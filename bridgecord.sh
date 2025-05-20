#!/bin/bash

pip install flask flask_cors request
pip install discord.py
pip install requests
pip install -r requirements.txt
pip install openai
apt install cloudflared

cd src

python main.py

cloudflared tunnel --url http://localhost:5000