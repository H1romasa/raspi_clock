import requests
import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from io import BytesIO
import time
import threading
import random
import math
import os
import json

# APIキーの設定
WEATHER_API_KEY = "23c11bc47e316ef930b5b337848ce6ec"
# 都市設定
CITY = "Saga"

class WeatherBackgroundManager:
    """天気に応じた背景画像を管理するクラス"""
    
    def __init__(self, parent, canvas, width, height):
        self.parent = parent
        self.canvas = canvas
        self.width = width
        self.height = height
        self.background_image = None
        self.background_photo = None
        self.background_id = None
        self.current_weather_type = None
        
        # 天気タイプごとの背景画像パス
        self.weather_backgrounds = {
            "clear": None,     # 晴れ
            "clouds": None,    # 曇り
            "rain": None,      # 雨
            "snow": None,      # 雪
            "mist": None,      # 霧
            "thunderstorm": None,  # 雷雨
            "default": None    # デフォルト/その他
        }
        
        # 設定ファイルのパス
        self.settings_file = os.path.join(os.path.expanduser("~"), "weather_backgrounds.json")
        
        # 設定を読み込む
        self.load_background_settings()
    
    def set_background_color(self, color):
        """背景色を設定"""
        self.canvas.config(bg=color)
        # 画像が設定されていれば削除
        if self.background_id:
            self.canvas.delete(self.background_id)
            self.background_id = None
            self.background_photo = None
    
    def load_background_image(self, file_path=None, weather_type=None):
        """背景画像をロード"""
        if file_path is None:
            # ファイル選択ダイアログを表示
            file_path = filedialog.askopenfilename(
                title="背景画像を選択",
                filetypes=[
                    ("画像ファイル", "*.jpg *.jpeg *.png *.bmp *.gif"),
                    ("すべてのファイル", "*.*")
                ]
            )
        
        if not file_path:
            return False
        
        try:
            # 天気タイプが指定されている場合は保存
            if weather_type:
                self.weather_backgrounds[weather_type] = file_path
                # 設定を保存
                self.save_background_settings()
                
                # 現在表示中の天気タイプと異なる場合は画像を変更しない
                if self.current_weather_type != weather_type:
                    return True
            
            # 画像をロード
            self.background_image = Image.open(file_path)
            
            # キャンバスのサイズに合わせてリサイズ
            self.update_background_size()
            
            return True
        except Exception as e:
            print(f"画像のロードエラー: {e}")
            return False
    
    def update_weather_background(self, weather_condition):
        """現在の天気に基づいて背景画像を更新"""
        # 天気条件からタイプを決定
        weather_type = self.get_weather_type(weather_condition)
        self.current_weather_type = weather_type
        
        # 対応する背景画像が設定されているか確認
        background_path = self.weather_backgrounds.get(weather_type)
        
        # 設定されていなければデフォルトを使用
        if not background_path and weather_type != "default":
            background_path = self.weather_backgrounds.get("default")
        
        # 背景画像が設定されていれば読み込む
        if background_path and os.path.exists(background_path):
            self.load_background_image(background_path)
            return True
        
        return False
    
    def get_weather_type(self, weather_condition):
        """天気の説明文から天気タイプを決定"""
        weather_condition = weather_condition.lower()
        
        if "雷" in weather_condition:
            return "thunderstorm"
        elif "雨" in weather_condition:
            return "rain"
        elif "雪" in weather_condition:
            return "snow"
        elif "霧" in weather_condition or "もや" in weather_condition:
            return "mist"
        elif "曇" in weather_condition:
            return "clouds"
        elif "晴" in weather_condition:
            return "clear"
        else:
            return "default"
    
    def update_background_size(self):
        """背景画像のサイズをキャンバスに合わせる"""
        if not self.background_image:
            return
        
        # キャンバスの現在のサイズを取得
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # サイズが有効でない場合は設定値を使用
        if canvas_width <= 1:
            canvas_width = self.width
        if canvas_height <= 1:
            canvas_height = self.height
        
        # 画像をキャンバスサイズに合わせてリサイズ
        resized_image = self.background_image.copy()
        resized_image = resized_image.resize((canvas_width, canvas_height), Image.LANCZOS)
        
        # tkinter用のPhotoImageに変換
        self.background_photo = ImageTk.PhotoImage(resized_image)
        
        # 既存の背景画像を削除
        if self.background_id:
            self.canvas.delete(self.background_id)
        
        # 新しい背景画像をキャンバスの最背面に配置
        self.background_id = self.canvas.create_image(
            canvas_width // 2, canvas_height // 2,
            image=self.background_photo
        )
        
        # 背景を最背面に移動
        self.canvas.tag_lower(self.background_id)
    
    def load_background_settings(self):
        """背景画像の設定を読み込む"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    self.weather_backgrounds = settings
                print("背景画像の設定を読み込みました")
        except Exception as e:
            print(f"背景設定の読み込みエラー: {e}")
    
    def save_background_settings(self):
        """背景画像の設定を保存する"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.weather_backgrounds, f)
            print("背景画像の設定を保存しました")
        except Exception as e:
            print(f"背景設定の保存エラー: {e}")


class WeatherAnimation:
    """天気に応じたアニメーション効果を生成するクラス"""
    
    def __init__(self, canvas, width, height):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.animation_items = []
        self.animation_running = False
        self.current_weather = None
    
    def start_animation(self, weather_condition):
        """天気に応じたアニメーションを開始"""
        # すでに動いているアニメーションを停止
        self.stop_animation()
        
        # 新しい天気状態を保存
        self.current_weather = weather_condition
        
        # 天気状態に基づいてアニメーションを選択
        if "雨" in weather_condition:
            self.create_rain_animation()
        elif "雪" in weather_condition:
            self.create_snow_animation()
        elif "晴れ" in weather_condition:
            self.create_sun_animation()
        elif "曇" in weather_condition:
            self.create_cloud_animation()
        
        # アニメーションフラグをオン
        self.animation_running = True
        
        # アニメーションのメインループを開始
        self.animate()
    
    def stop_animation(self):
        """アニメーションを停止"""
        self.animation_running = False
        # キャンバス上のすべてのアニメーションアイテムを削除
        for item in self.animation_items:
            if isinstance(item['id'], list):
                for sub_id in item['id']:
                    self.canvas.delete(sub_id)
            else:
                self.canvas.delete(item['id'])
        self.animation_items = []
    
    def create_rain_animation(self):
        """雨のアニメーションを作成"""
        # 雨粒の数
        num_drops = 100
        
        # 雨粒を生成
        for _ in range(num_drops):
            x = random.randint(0, self.width)
            y = random.randint(-100, 0)
            length = random.randint(10, 30)
            speed = random.uniform(5, 15)
            
            # 雨粒を描画
            drop = self.canvas.create_line(
                x, y, x, y + length, 
                fill='#3a95e3', width=2,
                tags='rain'
            )
            
            # アニメーションアイテムリストに追加
            self.animation_items.append({
                'id': drop,
                'x': x,
                'y': y,
                'length': length,
                'speed': speed,
                'type': 'rain'
            })
    
    def create_snow_animation(self):
        """雪のアニメーションを作成"""
        # 雪片の数
        num_flakes = 50
        
        # 雪片を生成
        for _ in range(num_flakes):
            x = random.randint(0, self.width)
            y = random.randint(-50, 0)
            size = random.randint(3, 8)
            speed = random.uniform(1, 4)
            sway = random.uniform(-1, 1)
            
            # 雪片を描画
            flake = self.canvas.create_oval(
                x-size, y-size, x+size, y+size, 
                fill='white', outline='white',
                tags='snow'
            )
            
            # アニメーションアイテムリストに追加
            self.animation_items.append({
                'id': flake,
                'x': x,
                'y': y,
                'size': size,
                'speed': speed,
                'sway': sway,
                'type': 'snow'
            })
    
    def create_sun_animation(self):
        """太陽光のアニメーションを作成"""
        # 中心の太陽
        sun_x = self.width // 4
        sun_y = self.height // 4
        sun_size = 40
        
        sun = self.canvas.create_oval(
            sun_x-sun_size, sun_y-sun_size, 
            sun_x+sun_size, sun_y+sun_size, 
            fill='#FFD700', outline='#FFA500',
            width=2, tags='sun'
        )
        
        self.animation_items.append({
            'id': sun,
            'x': sun_x,
            'y': sun_y,
            'size': sun_size,
            'phase': 0,
            'type': 'sun'
        })
        
        # 光線を追加
        for i in range(8):
            angle = i * (360 / 8)
            ray = self.canvas.create_line(
                sun_x, sun_y, 
                sun_x + sun_size * 2 * math.cos(math.radians(angle)), 
                sun_y + sun_size * 2 * math.sin(math.radians(angle)),
                fill='#FFD700', width=3, tags='sun_ray'
            )
            
            self.animation_items.append({
                'id': ray,
                'x': sun_x,
                'y': sun_y,
                'angle': angle,
                'length': sun_size * 2,
                'phase': 0,
                'type': 'sun_ray'
            })
    
    def create_cloud_animation(self):
        """雲のアニメーションを作成"""
        # 雲の数
        num_clouds = 5
        
        for i in range(num_clouds):
            x = random.randint(-100, self.width)
            y = random.randint(50, self.height // 2)
            size = random.randint(40, 80)
            speed = random.uniform(0.5, 1.5)
            
            # 複数の円を組み合わせて雲を作成
            cloud_parts = []
            
            # 雲の本体
            for j in range(3):
                offset_x = j * size / 2
                offset_y = random.randint(-10, 10)
                part = self.canvas.create_oval(
                    x + offset_x, y + offset_y,
                    x + offset_x + size, y + offset_y + size,
                    fill='#CCCCCC', outline='#CCCCCC', tags='cloud'
                )
                cloud_parts.append(part)
            
            # 雲の上部
            part = self.canvas.create_oval(
                x + size/2, y - size/3,
                x + size/2 + size, y - size/3 + size,
                fill='#CCCCCC', outline='#CCCCCC', tags='cloud'
            )
            cloud_parts.append(part)
            
            # アニメーションアイテムリストに追加
            self.animation_items.append({
                'id': cloud_parts,
                'x': x,
                'y': y,
                'size': size,
                'speed': speed,
                'type': 'cloud'
            })
    
    def animate(self):
        """アニメーションのメインループ"""
        if not self.animation_running:
            return
        
        # 各アニメーションアイテムを更新
        new_items = []
        
        for item in self.animation_items:
            if item['type'] == 'rain':
                # 雨粒のアニメーション
                item['y'] += item['speed']
                
                # 画面から出たら上に戻す
                if item['y'] > self.height:
                    item['y'] = random.randint(-100, 0)
                    item['x'] = random.randint(0, self.width)
                
                # 雨粒の位置を更新
                self.canvas.coords(
                    item['id'], 
                    item['x'], item['y'], 
                    item['x'], item['y'] + item['length']
                )
                new_items.append(item)
                
            elif item['type'] == 'snow':
                # 雪片のアニメーション
                item['y'] += item['speed']
                item['x'] += item['sway']
                
                # 画面から出たら上に戻す
                if item['y'] > self.height:
                    item['y'] = random.randint(-50, 0)
                    item['x'] = random.randint(0, self.width)
                    item['sway'] = random.uniform(-1, 1)
                
                # 雪片の位置を更新
                self.canvas.coords(
                    item['id'], 
                    item['x']-item['size'], item['y']-item['size'], 
                    item['x']+item['size'], item['y']+item['size']
                )
                new_items.append(item)
                
            elif item['type'] == 'sun':
                # 太陽のパルスアニメーション
                item['phase'] = (item['phase'] + 0.05) % (2 * 3.14159)
                pulse = 1 + 0.1 * math.sin(item['phase'])
                
                new_size = item['size'] * pulse
                
                # 太陽の大きさを更新
                self.canvas.coords(
                    item['id'],
                    item['x']-new_size, item['y']-new_size,
                    item['x']+new_size, item['y']+new_size
                )
                new_items.append(item)
                
            elif item['type'] == 'sun_ray':
                # 太陽光のアニメーション
                item['phase'] = (item['phase'] + 0.05) % (2 * 3.14159)
                pulse = 1 + 0.3 * math.sin(item['phase'])
                
                new_length = item['length'] * pulse
                new_x = item['x'] + new_length * math.cos(math.radians(item['angle']))
                new_y = item['y'] + new_length * math.sin(math.radians(item['angle']))
                
                # 光線の長さを更新
                self.canvas.coords(
                    item['id'],
                    item['x'], item['y'],
                    new_x, new_y
                )
                new_items.append(item)
                
            elif item['type'] == 'cloud':
                # 雲のアニメーション
                item['x'] += item['speed']
                
                # 画面から出たら左に戻す
                if item['x'] > self.width + 100:
                    item['x'] = -200
                
                # 雲の各パーツを移動
                for i, part_id in enumerate(item['id']):
                    if i < 3:  # 基本パーツ
                        offset_x = i * item['size'] / 2
                        offset_y = random.randint(-10, 10)
                        self.canvas.coords(
                            part_id,
                            item['x'] + offset_x, item['y'] + offset_y,
                            item['x'] + offset_x + item['size'], item['y'] + offset_y + item['size']
                        )
                    else:  # 上部パーツ
                        self.canvas.coords(
                            part_id,
                            item['x'] + item['size']/2, item['y'] - item['size']/3,
                            item['x'] + item['size']/2 + item['size'], item['y'] - item['size']/3 + item['size']
                        )
                
                new_items.append(item)
        
        # アイテムリストを更新
        self.animation_items = new_items
        
        # 次のフレームをスケジュール
        self.canvas.after(33, self.animate)  # 約30FPS


class WeatherTimeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("天気と時刻")
        self.root.geometry("800x480")  # 7インチディスプレイ用
        
        # 全画面表示（オプション）
        # self.root.attributes('-fullscreen', True)
        
        # メインフレーム
        self.main_frame = tk.Frame(root, bg="black")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # アニメーション用キャンバスを背景に配置
        self.canvas = tk.Canvas(self.main_frame, bg="black", highlightthickness=0)
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)
        
        # 背景管理クラスの初期化
        self.background_manager = WeatherBackgroundManager(self.root, self.canvas, 800, 480)
        
        # アニメーションクラスの初期化
        self.animation = WeatherAnimation(self.canvas, 800, 480)
        
        # メニューバーの作成
        self.create_menu()
        
        # 半透明のオーバーレイパネル (天気情報表示用)
        self.overlay = tk.Frame(self.main_frame, bg="#000000")
        self.overlay.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.8)
        
        # 時刻表示ラベル
        self.time_label = tk.Label(self.overlay, font=("Arial", 72), bg="#000000", fg="white")
        self.time_label.pack(fill=tk.X, pady=(20, 0))
        
        # 日付表示ラベル
        self.date_label = tk.Label(self.overlay, font=("Arial", 24), bg="#000000", fg="white")
        self.date_label.pack(fill=tk.X)
        
        # 天気表示フレーム
        self.weather_frame = tk.Frame(self.overlay, bg="#000000")
        self.weather_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        # 天気アイコン
        self.weather_icon = tk.Label(self.weather_frame, bg="#000000")
        self.weather_icon.pack(side=tk.LEFT, padx=20)
        
        # 天気情報
        self.weather_info = tk.Label(self.weather_frame, font=("Arial", 24), 
                                    bg="#000000", fg="white", justify=tk.LEFT)
        self.weather_info.pack(side=tk.LEFT, padx=20)
        
        # 現在のアイコン画像を保持する変数
        self.current_icon_photo = None
        self.current_weather_condition = None
        
        # 設定ファイルの読み込み（設定を保存する場合）
        self.load_settings()
        
        # 時計の更新
        self.update_clock()
        
        # ウィンドウサイズ変更時にキャンバスのサイズも更新
        self.root.bind("<Configure>", self.on_resize)
        
        # 初回の天気更新（メインスレッドで一度実行）
        self.update_weather_once()
        
        # 天気の定期更新（別スレッドで実行）
        threading.Thread(target=self.update_weather_periodically, daemon=True).start()
    
    def create_menu(self):
        """メニューの作成"""
        menu_bar = tk.Menu(self.root)
        
        # 背景メニュー
        background_menu = tk.Menu(menu_bar, tearoff=0)
        
        # 天気ごとの背景設定サブメニュー
        weather_bg_menu = tk.Menu(background_menu, tearoff=0)
        weather_bg_menu.add_command(label="晴れの背景を設定", 
                                    command=lambda: self.set_weather_background("clear"))
        weather_bg_menu.add_command(label="曇りの背景を設定", 
                                    command=lambda: self.set_weather_background("clouds"))
        weather_bg_menu.add_command(label="雨の背景を設定", 
                                    command=lambda: self.set_weather_background("rain"))
        weather_bg_menu.add_command(label="雪の背景を設定", 
                                    command=lambda: self.set_weather_background("snow"))
        weather_bg_menu.add_command(label="霧の背景を設定", 
                                    command=lambda: self.set_weather_background("mist"))
        weather_bg_menu.add_command(label="雷雨の背景を設定", 
                                    command=lambda: self.set_weather_background("thunderstorm"))
        weather_bg_menu.add_command(label="デフォルト背景を設定", 
                                    command=lambda: self.set_weather_background("default"))
        
        background_menu.add_cascade(label="天気ごとの背景設定", menu=weather_bg_menu)
        background_menu.add_command(label="現在の背景をクリア", 
                                    command=lambda: self.background_manager.set_background_color("black"))
        
        # 色メニュー
        color_menu = tk.Menu(background_menu, tearoff=0)
        for color_name, color_code in [
            ("黒", "black"), 
            ("紺色", "navy"), 
            ("青", "blue"), 
            ("空色", "skyblue"),
            ("緑", "green"),
            ("暗緑", "darkgreen"),
            ("茶色", "brown"),
            ("赤", "red"),
            ("紫", "purple")
        ]:
            color_menu.add_command(
                label=color_name, 
                command=lambda c=color_code: self.background_manager.set_background_color(c)
            )
        
        background_menu.add_cascade(label="背景色を選択", menu=color_menu)
        menu_bar.add_cascade(label="背景", menu=background_menu)
        
        # 設定メニュー
        settings_menu = tk.Menu(menu_bar, tearoff=0)
        settings_menu.add_command(label="都市の変更", command=self.change_city)
        settings_menu.add_command(label="APIキーの変更", command=self.change_api_key)
        
        # 表示・非表示の切り替え
        self.show_animation_var = tk.BooleanVar(value=True)
        settings_menu.add_checkbutton(
            label="アニメーションを表示", 
            variable=self.show_animation_var,
            command=self.toggle_animation
        )
        
        self.show_overlay_var = tk.BooleanVar(value=True)
        settings_menu.add_checkbutton(
            label="情報パネルを表示", 
            variable=self.show_overlay_var,
            command=self.toggle_overlay
        )
        
        menu_bar.add_cascade(label="設定", menu=settings_menu)
        
        # 更新メニュー
        update_menu = tk.Menu(menu_bar, tearoff=0)
        update_menu.add_command(label="天気情報を今すぐ更新", command=self.update_weather_once)
        menu_bar.add_cascade(label="更新", menu=update_menu)
        
        # メニューバーを設定
        self.root.config(menu=menu_bar)
    
    def set_weather_background(self, weather_type):
        """特定の天気タイプの背景画像を設定"""
        file_path = filedialog.askopenfilename(
            title=f"{weather_type}の背景画像を選択",
            filetypes=[
                ("画像ファイル", "*.jpg *.jpeg *.png *.bmp *.gif"),
                ("すべてのファイル", "*.*")
            ]
        )
        
        if file_path:
            # 画像を設定
            if self.background_manager.load_background_image(file_path, weather_type):
                # 現在の天気がこのタイプの場合、表示を更新
                if self.current_weather_condition:
                    current_type = self.background_manager.get_weather_type(self.current_weather_condition)
                    if current_type == weather_type:
                        self.background_manager.update_weather_background(self.current_weather_condition)
                
                messagebox.showinfo("背景設定", f"{weather_type}の背景画像を設定しました。")
    
    def toggle_animation(self):
        """アニメーションの表示・非表示を切り替え"""
        if self.show_animation_var.get():
            # アニメーションを再開
            if self.current_weather_condition:
                self.animation.start_animation(self.current_weather_condition)
        else:
            # アニメーションを停止
            self.animation.stop_animation()
    
    def toggle_overlay(self):
        """オーバーレイパネルの表示・非表示を切り替え"""
        if self.show_overlay_var.get():
            self.overlay.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.8)
        else:
            self.overlay.place_forget()
    
    def change_city(self):
        """都市を変更するダイアログ"""
        # 簡易的なトップレベルウィンドウを作成
        dialog = tk.Toplevel(self.root)
        dialog.title("都市の変更")
        dialog.geometry("300x100")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="都市名 (英語):").pack(pady=(10, 0))
        
        city_var = tk.StringVar(value=CITY)
        entry = tk.Entry(dialog, textvariable=city_var, width=30)
        entry.pack(pady=5)
        
        def on_ok():
            global CITY
            CITY = city_var.get()
            dialog.destroy()
            # 設定を適用して天気情報を更新
            self.update_weather_once()
            # 設定を保存
            self.save_settings()
        
        tk.Button(dialog, text="OK", command=on_ok).pack(pady=5)
    
    def change_api_key(self):
        """APIキーを変更するダイアログ"""
        # 簡易的なトップレベルウィンドウを作成
        dialog = tk.Toplevel(self.root)
        dialog.title("APIキーの変更")
        dialog.geometry("400x100")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="OpenWeatherMap APIキー:").pack(pady=(10, 0))
        
        api_key_var = tk.StringVar(value=WEATHER_API_KEY)
        entry = tk.Entry(dialog, textvariable=api_key_var, width=40)
        entry.pack(pady=5)
        
        def on_ok():
            global WEATHER_API_KEY
            WEATHER_API_KEY = api_key_var.get()
            dialog.destroy()
            # 設定を適用して天気情報を更新
            self.update_weather_once()
            # 設定を保存
            self.save_settings()
        
        tk.Button(dialog, text="OK", command=on_ok).pack(pady=5)
    
    def load_settings(self):
        """設定を読み込む"""
        try:
            # 設定ファイルのパス
            settings_file = os.path.join(os.path.expanduser("~"), "weather_app_settings.txt")
            
            if os.path.exists(settings_file):
                with open(settings_file, "r") as f:
                    lines = f.readlines()
                    
                    for line in lines:
                        if "=" in line:
                            key, value = line.strip().split("=", 1)
                            if key == "CITY":
                                global CITY
                                CITY = value
                            elif key == "API_KEY":
                                global WEATHER_API_KEY
                                WEATHER_API_KEY = value
        except Exception as e:
            print(f"設定の読み込みエラー: {e}")
    
    def save_settings(self):
        """設定を保存する"""
        try:
            # 設定ファイルのパス
            settings_file = os.path.join(os.path.expanduser("~"), "weather_app_settings.txt")
            
            with open(settings_file, "w") as f:
                f.write(f"CITY={CITY}\n")
                f.write(f"API_KEY={WEATHER_API_KEY}\n")
        except Exception as e:
            print(f"設定の保存エラー: {e}")
    
    def on_resize(self, event):
        """ウィンドウリサイズ時の処理"""
        # キャンバスのサイズをウィンドウに合わせる
        self.canvas.config(width=event.width, height=event.height)
        # アニメーションのサイズも更新
        self.animation.width = event.width
        self.animation.height = event.height
        # 背景画像のサイズも更新
        self.background_manager.update_background_size()
        
        # 現在の天気に応じて再度アニメーションを開始
        if self.current_weather_condition and self.show_animation_var.get():
            self.animation.start_animation(self.current_weather_condition)
    
    def update_clock(self):
        # 現在時刻の取得と表示
        now = datetime.datetime.now()
        time_str = now.strftime("%H:%M:%S")
        date_str = now.strftime("%Y年%m月%d日 %A")
        
        self.time_label.config(text=time_str)
        self.date_label.config(text=date_str)
        
        # 1秒後に再度更新
        self.root.after(1000, self.update_clock)
    
    def update_weather_once(self):
        """天気情報を一度だけ更新する"""
        try:
            # APIキーが設定されているか確認
            if WEATHER_API_KEY == "あなたのOpenWeatherMapキー":
                self.weather_info.config(text="APIキーが設定されていません。\nWEATHER_API_KEYを実際のキーに\n置き換えてください。")
                return
                
            # OpenWeatherMap APIからデータ取得
            url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={WEATHER_API_KEY}&units=metric&lang=ja"
            print(f"APIリクエスト: {url}")  # デバッグ用
            
            response = requests.get(url)
            print(f"APIレスポンス: ステータスコード {response.status_code}")  # デバッグ用
            
            data = response.json()
            
            if response.status_code == 200:
                # 天気情報の抽出
                temp = data["main"]["temp"]
                feels_like = data["main"]["feels_like"]
                humidity = data["main"]["humidity"]
                description = data["weather"][0]["description"]
                
                # 天気状態を保存
                self.current_weather_condition = description
                
                # 背景画像の更新
                self.background_manager.update_weather_background(description)
                
                # 背景アニメーションの更新（表示設定がオンの場合）
                if self.show_animation_var.get():
                    self.animation.start_animation(description)
                
                # 情報を表示用に整形
                weather_text = f"天気: {description}\n"
                weather_text += f"気温: {temp}°C (体感: {feels_like}°C)\n"
                weather_text += f"湿度: {humidity}%"
                
                # 表示を更新
                self.weather_info.config(text=weather_text)
                
                # 天気アイコンを取得して表示
                icon_code = data["weather"][0]["icon"]
                icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
                
                try:
                    icon_response = requests.get(icon_url)
                    if icon_response.status_code == 200:
                        icon_image = Image.open(BytesIO(icon_response.content))
                        self.current_icon_photo = ImageTk.PhotoImage(icon_image)
                        self.weather_icon.config(image=self.current_icon_photo)
                except Exception as e:
                    print(f"アイコン取得エラー: {e}")
            else:
                error_msg = f"天気取得エラー: {data.get('message', '不明なエラー')}"
                print(error_msg)
                self.weather_info.config(text=error_msg)
        
        except Exception as e:
            error_msg = f"天気情報の取得エラー: {e}"
            print(error_msg)
            self.weather_info.config(text=error_msg)
    
    def update_weather_periodically(self):
        """30分ごとに天気を更新するスレッド"""
        while True:
            # UIスレッドで天気更新を実行
            self.root.after(0, self.update_weather_once)
            
            # 30分待機
            time.sleep(1800)


# 天気の種類についての説明ウィンドウ
class WeatherInfoDialog:
    def __init__(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("天気タイプについて")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        
        # スクロールバー付きテキストエリア
        frame = tk.Frame(self.dialog)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text = tk.Text(frame, wrap=tk.WORD, yscrollcommand=scrollbar.set)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=text.yview)
        
        # 説明文を追加
        text.insert(tk.END, "天気タイプと対応する日本語天気表現の対応表\n\n")
        text.insert(tk.END, "1. clear: 晴れ、快晴、晴天\n")
        text.insert(tk.END, "   - 雲がほとんどなく、太陽や月が明るく見える状態\n\n")
        text.insert(tk.END, "2. clouds: 曇り、薄曇り、曇天\n")
        text.insert(tk.END, "   - 雲が空を覆っている状態\n\n")
        text.insert(tk.END, "3. rain: 雨、小雨、大雨、にわか雨\n")
        text.insert(tk.END, "   - 水滴が空から降ってくる状態\n\n")
        text.insert(tk.END, "4. snow: 雪、小雪、大雪、みぞれ\n")
        text.insert(tk.END, "   - 雪片が空から降ってくる状態\n\n")
        text.insert(tk.END, "5. mist: 霧、もや、靄、煙霧\n")
        text.insert(tk.END, "   - 視界が霧などによって制限される状態\n\n")
        text.insert(tk.END, "6. thunderstorm: 雷雨、雷、雷を伴う雨\n")
        text.insert(tk.END, "   - 雷鳴や稲妻を伴う状態\n\n")
        text.insert(tk.END, "7. default: その他すべての天気状態\n")
        text.insert(tk.END, "   - 上記に該当しない天気状態（例：ひょう、砂塵など）\n\n")
        text.insert(tk.END, "天気タイプごとに背景画像を設定することで、現在の天気に合わせた背景が自動的に表示されます。")
        
        text.config(state=tk.DISABLED)  # 読み取り専用に設定
        
        # 閉じるボタン
        tk.Button(self.dialog, text="閉じる", command=self.dialog.destroy).pack(pady=10)


if __name__ == "__main__":
    root = tk.Tk()
    root.configure(bg="black")
    app = WeatherTimeApp(root)
    
    # 初回起動時に背景画像がなければ説明を表示（オプション）
    if not any(app.background_manager.weather_backgrounds.values()):
        # 数秒後に説明ウィンドウを表示（アプリが完全に起動した後）
        root.after(3000, lambda: messagebox.showinfo(
            "天気背景の設定",
            "メニューの「背景」>「天気ごとの背景設定」から、\n各天気タイプごとに背景画像を設定できます。\n\n"
            "設定した背景は天気に応じて自動的に切り替わります。"
        ))
    
    root.mainloop()
