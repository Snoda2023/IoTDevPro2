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
from dotenv import load_dotenv

# 変数
ambi_cnt = 0
gest = None

# 環境変数を取得
load_dotenv()
channel_id = getenv("CHANNEL_ID")
write_key = getenv("WRITE_KEY")

# インスタンスを生成
ambi_inst = ambient.Ambient(channel_id, write_key)
gest_inst = grove_gesture_sensor.gesture()
gest_inst.init()
tm1637_inst = TM1637(clk=26, dio=19, brightness=1)
grove_lcd_inst = grove_rgb_lcd.rgb_lcd()
ultrasonic_inst = ultrasonic_sensor.HYSRF05()

# Ambient.ioにデータを送る関数
def send_ambient(ambi_inst,json_data:dict):
    try:
        ret = ambi_inst.send(json_data)
        print(f"Ambient.io Status Code:{ret.status_code}")
    except requests.exceptions.RequestException as e:
        print(f">> Request failed: {e}")
        return e

def cds_to_rgb(value):
    red = 255 * ((value+1) / 3500)
    blue = 255 * (1 - ((value+1) / 3500))
    return [ceil(red), 0, ceil(blue)] # R G B

# 処理の本体
try:
    while True:
        us_dist = ultrasonic_inst.get_distance()                    # 超音波センサから距離を取得
        Potentiomater = readadc(3)                                  # 半固定抵抗の値
        JoyStick_X = readadc(1)                                     # ジョイスティックのX軸値
        gest_tmp = gest_inst.print_gesture()                        # ジェスチャの値をGroveLCDの文字列に反映
        if gest_tmp != "Nothing":                                   # ジェスチャの値がNothing以外なら
            gest = gest_tmp                                         # ジェスチャの戻り値を文字列に変換
            grove_lcd_inst.setText(text=gest)                       # GroveLCDにジェスチャ結果を表示
        CdS = readadc(0)                                            # 光センサからの明るさ
        r, g, b = cds_to_rgb(CdS)                                   # Cdsの値をRGBに変換()
        grove_lcd_inst.setRGB(r, g, b)                              # GroveLCDにCdS結果を表示
        tm1637_inst.number(Potentiomater)                           # TM1637に半固定抵抗の値を書き込み
        
        print(f"超音波:{us_dist}")
        print(f"CdS:{CdS}")
        print(f"CdS R:{r}")
        print(f"CdS G:{g}")
        print(f"CdS B:{b}")
        print(f"半固定抵抗:{Potentiomater}")
        print(f"JoyStick_X:{JoyStick_X}")
        print(f"ジェスチャー:{gest}")

        ambi_cnt += 1
        if ambi_cnt >= 700:
            send_ambient(ambi_inst, {"d7":us_dist})
            ambi_cnt = 1

        sleep(.1)

except KeyboardInterrupt:
    print("interrupted!")