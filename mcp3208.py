import RPi.GPIO as GPIO
from time import sleep

# 　SPI (Serial Peripheral Interface)
# 　SPIは同期式/全二重のメイン・サブノード型インターフェース
# メインまたはサブノードからのデータは、クロックの立ち上がりまたは
# 立下りエッジによって同期がとられる
# 4線式のSPIデバイス

class MCP3208:
    def __init__(self, clockpin=11, mosipin=10, misopin=9, cspin=8):
        GPIO.setmode(GPIO.BCM)              # BCMピン番号を使用
        # ピンの名前を変数として定義
        self.clockpin = clockpin                   # クロック
        self.mosipin = mosipin                   # 出力
        self.misopin = misopin                   # 入力
        self.cspin = cspin                       # チップ・セレクト
        # SPI通信用の入出力を定義
        GPIO.setup(self.clockpin, GPIO.OUT)
        GPIO.setup(self.mosipin, GPIO.OUT)
        GPIO.setup(self.misopin, GPIO.IN)
        GPIO.setup(self.cspin, GPIO.OUT)

    # MCP3208からSPI通信で12ビットのデジタル値を取得。0から7の8チャンネル使用可
    def readadc(self, adcnum=0):
        if adcnum > 7 or adcnum < 0:            # スタートビットは0番～7番の範囲
            return -1
        GPIO.output(self.cspin, GPIO.HIGH)           # CSをHIGHにする(確実に通信を確立するため)
        GPIO.output(self.clockpin, GPIO.LOW)         # CLKをLOWにする(確実に通信を確立するため)
        GPIO.output(self.cspin, GPIO.LOW)            # CSがLOWになったサブノードがメインとSPI通信を行う
        
        # LSB(Least Significant Bit/最下位ビット/右端ビット)
                                                # 0x00       | 0x18       = 0x18       << 3 = 0xC0
        commandout = adcnum                     # 0b00000000 | 0b00011000 = 0b00011000 << 3 = 0b11000000(0xC0)
        commandout |= 0x18                      # スタートビット+シングルエンドビット
        commandout <<= 3                        # LSBから8ビット目を送信するようにする
        for i in range(5):
            # LSBから数えて8ビット目から4ビット目まで(計5ビット)を送信
                                                # 0xC0       & 0x80       = 0x80
            if commandout & 0x80:               # 0b11000000 & 0b10000000 = 0b10000000
                GPIO.output(self.mosipin, GPIO.HIGH)
            else:
                GPIO.output(self.mosipin, GPIO.LOW)
            commandout <<= 1
            GPIO.output(self.clockpin, GPIO.HIGH)    # データ送信開始
            GPIO.output(self.clockpin, GPIO.LOW)     # データ送信終了
        adcout = 0                              # 受信(AD変換後の)データ
        # 13ビット読む(ヌルビット+12ビットデータ)
        for i in range(13):
            GPIO.output(self.clockpin, GPIO.HIGH)    # データ受信開始
            GPIO.output(self.clockpin, GPIO.LOW)     # データ受信完了
            adcout <<= 1
            if i > 0 and GPIO.input(self.misopin) == GPIO.HIGH:
                adcout |= 0x1
        GPIO.output(self.cspin, GPIO.HIGH)           # CSをHIGHにし、SPI通信を終了する
        return adcout

if __name__ == "__main__":
    mcp3208_inst = MCP3208()
    try:
        while True:
            CdS = mcp3208_inst.readadc(0)
            print(f"CdS          : {CdS}")
            Potentiomater = mcp3208_inst.readadc(1)
            print(f"Potentiomater: {Potentiomater}")
            JoyStick_X = mcp3208_inst.readadc(2)
            print(f"JoyStick_X   : {JoyStick_X}")
            JoyStick_Y = mcp3208_inst.readadc(3)
            print(f"JoyStick_Y   : {JoyStick_Y}")
            print("========== ==========")
            sleep(0.2)

    except KeyboardInterrupt:       # Cntl+Cを押すとKeyboardInterruptが送信される
        pass                        # 何もせずに次の命令に移る

    GPIO.cleanup()                  # GPIOの設定を解除する