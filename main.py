## Created by Shotaro Noda (TK220137)
## Last Update: 2023-11-20
## Class: IoT Device Programming IIA

import ambient
import requests
from time import sleep
from os import getenv
from dotenv import load_dotenv

# 環境変数を取得
load_dotenv()
channel_id = getenv("CHANNEL_ID")
write_key = getenv("WRITE_KEY")

# インスタンスを生成するところ
ambi = ambient.Ambient(channel_id, write_key)

# Ambientにデータを送る関数
def send_ambient(ambi_inst,json_data:dict):
    try:
        ret = ambi_inst.send(json_data)
        print(ret.status_code)
    except requests.exceptions.RequestException as e:
        print(f">> Request failed: {e}")
        return e
    

    
