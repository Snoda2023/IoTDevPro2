import pigpio
import time

class SG90:
    def __init__(self, pin=4):
        self.SERVO_PIN = pin
        # pigpioを初期化
        self.pi = pigpio.pi()

    # サーボモーターを特定の角度に設定する関数
    def set_angle(self, angle):
        assert 0 <= angle <= 180, '角度は0から180の間でなければなりません'
        
        # 角度を500から2500のパルス幅にマッピングする
        pulse_width = (angle / 180) * (2500 - 500) + 500
        
        # パルス幅を設定してサーボを回転させる
        self.pi.set_servo_pulsewidth(self.SERVO_PIN, pulse_width)

# 使用例
if __name__ == "__main__":
    sg90_inst = SG90()
    try:
        while True:
            sg90_inst.set_angle(90) # サーボを90度に設定
            print(90)
            time.sleep(1)
            
            sg90_inst.set_angle(0) # サーボを0度に設定
            print(0)
            time.sleep(1)
            
            sg90_inst.set_angle(90) # サーボを90度に設定
            print(90)
            time.sleep(1)
            
            sg90_inst.set_angle(180) # サーボを180度に設定
            print(180)
            time.sleep(1)

    except KeyboardInterrupt:
        pass