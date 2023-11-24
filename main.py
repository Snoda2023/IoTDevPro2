## Created by Shotaro Noda (TK220137)
## Last Update: 2023-11-24
## Class: IoT Device Programming IIA

import ambient
import requests
from all_mcp3208 import readadc # AD変換(MCP3208)
import grove_gesture_sensor # ジェスチャーセンサ
import grove_rgb_lcd        # ディスプレイ(GroveRgbLcd)
import ultrasonic_sensor    # 超音波センサ(HYSRF05)
from tm1637 import TM1637   # ディスプレイ(TM1637)
from math import ceil

from time import sleep
from os import getenv
# from dotenv import load_dotenv

# 変数
ambi_cnt:int = 0
gest_convert = ["NOTHING","FORWARD", "BACKWARD", "RIGHT", "LEFT", "UP", "DOWN", "CLOCKWISE", "ANTI-CLOCWISE", "WAVE"]

# 環境変数を取得
# load_dotenv()
# channel_id = getenv("CHANNEL_ID")
# write_key = getenv("WRITE_KEY")


# インスタンスを生成するところ
# ambi_inst = ambient.Ambient(channel_id, write_key)
gest_inst = grove_gesture_sensor.gesture()
tm1637_inst = TM1637(clk=26,dio=19,brightness=1)
grove_lcd_inst = grove_rgb_lcd.rgb_lcd()
ultrasonic_inst = ultrasonic_sensor.HYSRF05()


# Ambientにデータを送る関数
def send_ambient(ambi_inst,json_data:dict):
    try:
        ret = ambi_inst.send(json_data)
        print(ret.status_code)
    except requests.exceptions.RequestException as e:
        print(f">> Request failed: {e}")
        return e

def cds_to_rgb(value):
    if value <= 1:
        return [0,0,255]
    else:         
        red = 255 * (value / 3000)
        blue = 255 * (1 - (value / 3000))
        return [ceil(red),0,ceil(blue)] # R G B
    
# 処理の本体
try:
    while True:
        gesture_result = gest_convert[gest_inst.return_gesture()] # ジェスチャの戻り値を文字列に変換
        grove_lcd_inst.setText(text=gesture_result)               # GroveLCDにジェスチャ結果を表示
        
        us_dist = ultrasonic_inst.get_distance()                  # 超音波センサから距離を取得
        CdS = readadc(0)                                          # 光センサからの明るさ
        Potentiomater = readadc(3)                                # 半固定抵抗の値
        JoyStick_X = readadc(1)                                   # ジョイスティックのX軸値
        print(f"ジェスチャー:{us_dist}\nCdS:{CdS}\n半固定抵抗:{Potentiomater}\nJoyStick_X:{JoyStick_X}")
        
        r, g, b = cds_to_rgb(CdS)
        grove_lcd_inst.setRGB(r, g, b)
        
        tm1637_inst.number(Potentiomater)                         # TM1637に半固定抵抗の値を書き込み
        
        # if ambi_cnt == 6:
        #     send_ambient(ambi_inst, {"d1":us_dist})
        #     ambi_cnt = 0
            
        ambi_cnt += 3
        sleep(3)
except KeyboardInterrupt:
    print("interrupted!")

    
