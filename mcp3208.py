import RPi.GPIO as GPIO
from time import sleep

# 　SPI (Serial Peripheral Interface)
# 　SPIは同期式/全二重のメイン・サブノード型インターフェース
# メインまたはサブノードからのデータは、クロックの立ち上がりまたは
# 立下りエッジによって同期がとられる
# 4線式のSPIデバイス

# MCP3208からSPI通信で12ビットのデジタル値を取得。0から7の8チャンネル使用可
def readadc(adcnum=0, clockpin=11, mosipin=10, misopin=9, cspin=8):
    if adcnum > 7 or adcnum < 0:            # スタートビットは0番～7番の範囲
        return -1
    GPIO.output(cspin, GPIO.HIGH)           # CSをHIGHにする(確実に通信を確立するため)
    GPIO.output(clockpin, GPIO.LOW)         # CLKをLOWにする(確実に通信を確立するため)
    GPIO.output(cspin, GPIO.LOW)            # CSがLOWになったサブノードがメインとSPI通信を行う
    
    # LSB(Least Significant Bit/最下位ビット/右端ビット)
                                            # 0x00       | 0x18       = 0x18       << 3 = 0xC0
    commandout = adcnum                     # 0b00000000 | 0b00011000 = 0b00011000 << 3 = 0b11000000(0xC0)
    commandout |= 0x18                      # スタートビット+シングルエンドビット
    commandout <<= 3                        # LSBから8ビット目を送信するようにする
    for i in range(5):
        # LSBから数えて8ビット目から4ビット目まで(計5ビット)を送信
                                            # 0xC0       & 0x80       = 0x80
        if commandout & 0x80:               # 0b11000000 & 0b10000000 = 0b10000000
            GPIO.output(mosipin, GPIO.HIGH)
        else:
            GPIO.output(mosipin, GPIO.LOW)
        commandout <<= 1
        GPIO.output(clockpin, GPIO.HIGH)    # データ送信開始
        GPIO.output(clockpin, GPIO.LOW)     # データ送信終了
    adcout = 0                              # 受信(AD変換後の)データ
    # 13ビット読む(ヌルビット+12ビットデータ)
    for i in range(13):
        GPIO.output(clockpin, GPIO.HIGH)    # データ受信開始
        GPIO.output(clockpin, GPIO.LOW)     # データ受信完了
        adcout <<= 1
        if i > 0 and GPIO.input(misopin) == GPIO.HIGH:
            adcout |= 0x1
    GPIO.output(cspin, GPIO.HIGH)           # CSをHIGHにし、SPI通信を終了する
    return adcout

if __name__ == "__main__":

    GPIO.setmode(GPIO.BCM)          # BCMピン番号を使用
    # ピンの名前を変数として定義
    SPICLK = 11                     # クロック
    SPIMOSI = 10                    # 出力
    SPIMISO = 9                     # 入力
    SPICS = 8                       # チップ・セレクト
    # SPI通信用の入出力を定義
    GPIO.setup(SPICLK, GPIO.OUT)
    GPIO.setup(SPIMOSI, GPIO.OUT)
    GPIO.setup(SPIMISO, GPIO.IN)
    GPIO.setup(SPICS, GPIO.OUT)

    try:
        while True:
            CdS = readadc(0, SPICLK, SPIMOSI, SPIMISO, SPICS)
            print(f"CdS          : {CdS}")
            Potentiomater = readadc(1, SPICLK, SPIMOSI, SPIMISO, SPICS)
            print(f"Potentiomater: {Potentiomater}")
            JoyStick_X = readadc(2, SPICLK, SPIMOSI, SPIMISO, SPICS)
            print(f"JoyStick_X   : {JoyStick_X-2047}")
            JoyStick_Y = readadc(3, SPICLK, SPIMOSI, SPIMISO, SPICS)
            print(f"JoyStick_Y   : {(4095-JoyStick_Y)-2047}")
            print("========== ==========")
            sleep(0.2)

    except KeyboardInterrupt:       # Cntl+Cを押すとKeyboardInterruptが送信される
        pass                        # 何もせずに次の命令に移る

    GPIO.cleanup()                  # GPIOの設定を解除する