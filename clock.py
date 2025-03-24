import requests
import datetime
import tkinter as tk
from PIL import Image, ImageTk
from io import BytesIO
import time
import threading

# APIキーの設定（実際のキーに置き換えてください）
WEATHER_API_KEY = "あなたのOpenWeatherMapキー"
# 都市設定
CITY = "Tokyo"

class WeatherTimeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("天気と時刻")
        self.root.geometry("800x480")  # 7インチディスプレイ用
        
        # 全画面表示（オプション）
        # self.root.attributes('-fullscreen', True)
        
        # 時刻表示ラベル
        self.time_label = tk.Label(root, font=("Arial", 72), bg="black", fg="white")
        self.time_label.pack(fill=tk.X, pady=20)
        
        # 日付表示ラベル
        self.date_label = tk.Label(root, font=("Arial", 24), bg="black", fg="white")
        self.date_label.pack(fill=tk.X)
        
        # 天気表示フレーム
        self.weather_frame = tk.Frame(root, bg="black")
        self.weather_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        # 天気アイコン
        self.weather_icon = tk.Label(self.weather_frame, bg="black")
        self.weather_icon.pack(side=tk.LEFT, padx=20)
        
        # 天気情報
        self.weather_info = tk.Label(self.weather_frame, font=("Arial", 24), 
                                    bg="black", fg="white", justify=tk.LEFT)
        self.weather_info.pack(side=tk.LEFT, padx=20)
        
        # 時計の更新
        self.update_clock()
        
        # 天気の更新（別スレッドで実行）
        threading.Thread(target=self.update_weather, daemon=True).start()
    
    def update_clock(self):
        # 現在時刻の取得と表示
        now = datetime.datetime.now()
        time_str = now.strftime("%H:%M:%S")
        date_str = now.strftime("%Y年%m月%d日 %A")
        
        self.time_label.config(text=time_str)
        self.date_label.config(text=date_str)
        
        # 1秒後に再度更新
        self.root.after(1000, self.update_clock)
    
    def update_weather(self):
        while True:
            try:
                # OpenWeatherMap APIからデータ取得
                url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={WEATHER_API_KEY}&units=metric&lang=ja"
                response = requests.get(url)
                data = response.json()
                
                if response.status_code == 200:
                    # 天気情報の抽出
                    temp = data["main"]["temp"]
                    feels_like = data["main"]["feels_like"]
                    humidity = data["main"]["humidity"]
                    description = data["weather"][0]["description"]
                    
                    # 情報を表示用に整形
                    weather_text = f"天気: {description}\n"
                    weather_text += f"気温: {temp}°C (体感: {feels_like}°C)\n"
                    weather_text += f"湿度: {humidity}%"
                    
                    # UIスレッドで表示を更新
                    self.root.after(0, lambda: self.weather_info.config(text=weather_text))
                    
                    # 天気アイコンを取得して表示
                    icon_code = data["weather"][0]["icon"]
                    icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
                    icon_response = requests.get(icon_url)
                    if icon_response.status_code == 200:
                        icon_image = Image.open(BytesIO(icon_response.content))
                        icon_photo = ImageTk.PhotoImage(icon_image)
                        self.root.after(0, lambda: self.update_icon(icon_photo))
            
            except Exception as e:
                print(f"天気情報の取得エラー: {e}")
            
            # 30分ごとに天気を更新
            time.sleep(1800)
    
    def update_icon(self, photo):
        self.weather_icon.config(image=photo)
        self.weather_icon.image = photo  # 参照を保持


if __name__ == "__main__":
    root = tk.Tk()
    root.configure(bg="black")
    app = WeatherTimeApp(root)
    root.mainloop()