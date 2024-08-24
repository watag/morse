import RPi.GPIO as GPIO
import LCD1602
import time

# GPIOピンの設定
LED_PIN = 17      # LEDのピン
BUTTON_PIN = 27   # ボタンのピン

# モールス信号のマッピング
morse_code_map = {
    '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D',
    '.': 'E', '..-.': 'F', '--.': 'G', '....': 'H',
    '..': 'I', '.---': 'J', '-.-': 'K', '.-..': 'L',
    '--': 'M', '-.': 'N', '---': 'O', '.--.': 'P',
    '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
    '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X',
    '-.--': 'Y', '--..': 'Z',
    '-----': '0', '.----': '1', '..---': '2', '...--': '3',
    '....-': '4', '.....': '5', '-....': '6', '--...': '7',
    '---..': '8', '----.': '9',

}

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LED_PIN, GPIO.OUT)  # LEDピンを出力モードに設定
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # ボタンピンを入力モードに設定し、プルアップ抵抗を有効にする
    
    LCD1602.init(0x27, 1)  # LCDの初期化
    LCD1602.clear()
    LCD1602.write(0, 0, "Press button")
    LCD1602.write(0, 1, "to input Morse")

def read_morse_signal():
    signal = ""
    start_time = 0
    last_press_time = 0
    initial_display_done = False
    
    while True:
        if GPIO.input(BUTTON_PIN) == GPIO.LOW:  # ボタンが押されるとLOW
            GPIO.output(LED_PIN, GPIO.HIGH)  # ボタンを押している間LEDを点灯
            if start_time == 0:
                start_time = time.time()
                # ボタンが初めて押された時の初期表示をクリア
                if not initial_display_done:
                    LCD1602.clear()
                    initial_display_done = True
            last_press_time = time.time()
        else:
            GPIO.output(LED_PIN, GPIO.LOW)  # ボタンが離されたらLEDを消灯
            if start_time > 0:
                duration = time.time() - start_time
                if duration >= 0.3:  # 0.3秒以上なら「－」
                    signal += "-"
                else:  # それ以下なら「・」
                    signal += "."
                
                # リアルタイムでLCDの2段目に表示
                LCD1602.write(0, 1, signal)
                
                start_time = 0

        # 信号の確定条件：ボタンが押されていない状態が0.5秒以上続く
        if signal and (time.time() - last_press_time > 0.5):
            return signal
        
        time.sleep(0.1)

def translate_morse(signal):
    return morse_code_map.get(signal, '?')

def display_message(message):
    LCD1602.write(0, 0, message)  # 1段目のみを更新表示

def loop():
    while True:
        morse_signal = read_morse_signal()
        translated_char = translate_morse(morse_signal)
        display_message(translated_char)
        time.sleep(2)  # メッセージ表示後の待機時間
        # デフォルトメッセージに戻す
        LCD1602.clear()
        LCD1602.write(0, 0, "Press button")
        LCD1602.write(0, 1, "to input Morse")

if __name__ == "__main__":
    try:
        setup()
        loop()
    except KeyboardInterrupt:
        GPIO.cleanup()  # プログラム終了時にGPIO設定をクリーンアップ
