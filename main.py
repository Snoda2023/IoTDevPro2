## Created by Shotaro Noda (TK220137)
## Last Update: 2023-11-20
## Class: IoT Device Programming IIA

import ambient
import requests
import grove_gesture_sensor # ジェスチャーセンサ
import grove_rgb_lcd        # Groveディスプレイ
from tm1637 import TM1637   # TM1637ディスプレイ

from time import sleep
from os import getenv
from dotenv import load_dotenv

# 環境変数を取得
load_dotenv()
channel_id = getenv("CHANNEL_ID")
write_key = getenv("WRITE_KEY")

gest_convert = ["NOTHING","FORWARD", "BACKWARD", "RIGHT", "LEFT", "UP", "DOWN", "CLOCKWISE", "ANTI-CLOCWISE", "WAVE"]

# インスタンスを生成するところ
ambi_inst = ambient.Ambient(channel_id, write_key)
gest_inst = grove_gesture_sensor.gesture()
tm1637_inst = TM1637(clk=26,dio=19)
grove_lcd_inst = grove_rgb_lcd.rgb_lcd

# Ambientにデータを送る関数
def send_ambient(ambi_inst,json_data:dict):
    try:
        ret = ambi_inst.send(json_data)
        print(ret.status_code)
    except requests.exceptions.RequestException as e:
        print(f">> Request failed: {e}")
        return e
    
# 処理の本体
try:
    while True:
        gesture_result = gest_convert[gest_inst.return_gesture()] # ジェスチャの戻り値を文字列に変換
        grove_lcd_inst.setText(text=gesture_result)               # GroveLCDにジェスチャ結果を表示
        
        
        
        
        
except KeyboardInterrupt:
    print("interrupted!")

    
