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

from time import sleep
from os import getenv
from dotenv import load_dotenv

# 変数
ambi_cnt:int = 0

# 環境変数を取得
load_dotenv()
channel_id = getenv("CHANNEL_ID")
write_key = getenv("WRITE_KEY")

gest_convert = ["NOTHING","FORWARD", "BACKWARD", "RIGHT", "LEFT", "UP", "DOWN", "CLOCKWISE", "ANTI-CLOCWISE", "WAVE"]

# インスタンスを生成するところ
ambi_inst = ambient.Ambient(channel_id, write_key)
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

    
# 処理の本体
try:
    while True:
        gesture_result = gest_convert[gest_inst.return_gesture()] # ジェスチャの戻り値を文字列に変換
        grove_lcd_inst.setText(text=gesture_result)               # GroveLCDにジェスチャ結果を表示
        
        us_dist = ultrasonic_inst.get_distance()                  # 超音波センサから距離を取得
        CdS = readadc(0)                                          # 光センサからの明るさ
        Potentiomater = readadc(1)                                # 半固定抵抗の値
        JoyStick_X = readadc(2)                                   # ジョイスティックのX軸値
        print(f"ジェスチャー:{us_dist}\nCdS:{CdS}\n半固定抵抗:{Potentiomater}\nJoyStick_X:{JoyStick_X}")
        
        tm1637_inst.number(Potentiomater)                         # TM1637に半固定抵抗の値を書き込み
        
        # if ambi_cnt == 6:
        #     send_ambient(ambi_inst, {"d1":us_dist})
        #     ambi_cnt = 0
            
        ambi_cnt += 2
        sleep(2)
except KeyboardInterrupt:
    print("interrupted!")

    
