import requests
import RPi.GPIO as GPIO
from time import sleep

import ambient
from mcp3208 import MCP3208 # AD変換(MCP3208)
import grove_gesture_sensor # ジェスチャーセンサ
import grove_rgb_lcd        # ディスプレイ(Grove LCD RGB Backlight)
from tm1637 import TM1637   # 7セグメントLED(TM1637)
import ultrasonic_sensor    # 超音波センサ(HYSRF05)
from servo import SG90      # サーボモータ(SG90)

from os import getenv
from dotenv import load_dotenv

# Ambient.ioにデータを送る関数
def send_ambient(ambi_inst, json_data:dict):
    try:
        ret = ambi_inst.send(json_data)
        print(f"Ambient.io Status Code:{ret.status_code}")
    except requests.exceptions.RequestException as e:
        print(f">> Request failed: {e}")
        return e

# CdSのデータをRGBに変換する関数
def cds_to_rgb(value):
    MAX = 4095
    rgb = None
    if MAX/5*4 <= value:
        rgb = [21, 234, 0]  # 白
    elif MAX/5*3 <= value:
        rgb = [ 5, 250, 0]  # 黄
    elif MAX/5*2 <= value:
        rgb = [ 6, 249, 0]  # 緑
    elif MAX/5*1 <= value:
        rgb = [18, 237, 0]  # 青
    else:
        rgb = [17, 238, 0]  # 紫
    return rgb

if __name__ == "__main__":
    # (1) 変数宣言
    ambi_cnt = 1
    gest = "Nothing"
    wave_flag_l = False
    wave_flag_r = False
    is_wave = False
    r, g, b = [0]*3

    # (2) 環境変数を取得
    load_dotenv()
    channel_id = getenv("CHANNEL_ID")
    write_key = getenv("WRITE_KEY")

    # (3) インスタンスを生成
    ambi_inst = ambient.Ambient(channel_id, write_key)
    mcp3208_inst = MCP3208(clockpin=11, mosipin=10, misopin=9, cspin=8)
    gest_inst = grove_gesture_sensor.gesture()
    grove_lcd_inst = grove_rgb_lcd.rgb_lcd()
    tm1637_inst = TM1637(clk=26, dio=19, brightness=1)
    ultrasonic_inst = ultrasonic_sensor.HYSRF05(trig_pin=15, echo_pin=14)
    sg90_inst = SG90(pin=4)

    # (4) センサ初期設定
    gest_inst.init()
    grove_lcd_inst.setText(text=gest)

    # (5) 処理の本体(メインループ)
    try:
        while True:
            # データの取得
            CdS = mcp3208_inst.readadc(0)               # 光センサの値を取得(SPI)
            Potentiomater = mcp3208_inst.readadc(1)     # 半固定抵抗の値を取得(SPI)
            JoyStick_X = mcp3208_inst.readadc(2)        # ジョイスティックのX軸の値を取得(SPI)
            JoyStick_Y = mcp3208_inst.readadc(3)        # ジョイスティックのY軸の値を取得(SPI)
            gest_tmp = gest_inst.print_gesture()        # ジェスチャの値を取得(I2C)
            us_dist = ultrasonic_inst.get_distance()    # 超音波センサから距離を取得(その他)
            
            # 距離が近い場合は「警告」を表示
            if us_dist <= 20:
                grove_lcd_inst.setText(text="TOO CLOSE!\nTOO CLOSE!")
                grove_lcd_inst.setRGB(1, 254, 0)        # 赤
                tm1637_inst.show("-SOS")
                sleep(1)

            # 手を左右に振っているかどうか
            if gest == "Left":
                if wave_flag_r:
                    is_wave = True
                    wave_flag_r = False
                else:
                    wave_flag_l = True
            elif gest == "Right":
                if wave_flag_l:
                    is_wave = True
                    wave_flag_l = False
                else:
                    wave_flag_r = True
            else:
                wave_flag_l = False
                wave_flag_r = False

            # 手を振っている場合は「挨拶」
            if is_wave:
                print(True)
                grove_lcd_inst.setText(text="HelloHelloHello\nHelloHelloHello")
                grove_lcd_inst.setRGB(20, 235, 0)       # 水色
                tm1637_inst.show("Helo")
                # サーボモータを動かす処理
                for _ in range(3):
                    for _ in range(2):
                        sg90_inst.set_angle(0)
                        sleep(1)
                        sg90_inst.set_angle(180)
                        sleep(1)
                    tm1637_inst.scroll('Hello', 500)    # 2 fps
                    tm1637_inst.show("Helo")
                is_wave = False
                wave_flag_l = False
                wave_flag_r = False
                gest = "Nothing"

            # データの加工と反映
            if gest_tmp != "Nothing":                   # ジェスチャの値がNothing以外なら
                gest = gest_tmp                         # ジェスチャの戻り値を文字列に変換
            grove_lcd_inst.setRGB(r, g, b)
            grove_lcd_inst.setText(text=f"{gest},dist:{int(us_dist)}\nX:{JoyStick_X}, Y:{JoyStick_Y}")# GroveLCDにジェスチャ結果を表示
            r_tmp, g_tmp, b_tmp = cds_to_rgb(CdS)       # Cdsの値をRGBに変換()
            if r_tmp != r:
                r, g, b = [r_tmp, g_tmp, b_tmp]
                grove_lcd_inst.setRGB(r, g, b)          # GroveLCDにCdS結果を表示
            tm1637_inst.number(Potentiomater)           # TM1637に半固定抵抗の値を書き込み
            
            # ターミナルへ出力
            print(f"CdS:{CdS}")
            print(f"半固定抵抗:{Potentiomater}")
            print(f"JoyStick_X:{JoyStick_X}")
            print(f"JoyStick_Y:{JoyStick_Y}")
            print(f"ジェスチャー:{gest}")
            print(f"超音波:{us_dist}")
            print(f"ambi_cnt:{ambi_cnt}")
            print(f"========== ========== ==========")

            # 7秒おきにAmbient.ioに計測したデータを送信(0.5秒*14回=7秒)
            ambi_cnt += 1
            if ambi_cnt > 14:
                send_ambient(ambi_inst, {
                    "d1": CdS,
                    "d2": Potentiomater,
                    "d3": JoyStick_X,
                    "d4": JoyStick_Y,
                    "d5": gest,
                    "d6": us_dist
                })
                print(f"========== ========== ==========")
                ambi_cnt = 1

            sleep(.5)

    except KeyboardInterrupt:
        print("interrupted!")
        grove_lcd_inst.setRGB(0, 0, 0)
        grove_lcd_inst.setText("                \n                ")
        tm1637_inst.write([0, 0, 0, 0])
        GPIO.cleanup()