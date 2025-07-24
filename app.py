import tkinter
import customtkinter
from tkintermapview import TkinterMapView
import json
import os
import requests
from tkinter import messagebox, filedialog
import webbrowser
from datetime import datetime
import threading
import time
import bcrypt
import shutil
from PIL import Image, ImageTk
import subprocess
import platform
import calendar
from collections import Counter, defaultdict
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

APP_TITLE = "🗺️ Seyahat Takip - Dünyayı Keşfet!"
GEOMETRY = "400x200"
USERS_FILE = "users.json"

# Modern renk paleti
COLORS = {
    'primary': '#1F2937',  # Koyu gri-mavi
    'secondary': '#374151',  # Orta gri
    'accent': '#3B82F6',  # Parlak mavi
    'success': '#10B981',  # Yeşil
    'warning': '#F59E0B',  # Turuncu
    'danger': '#EF4444',  # Kırmızı
    'surface': '#111827',  # Çok koyu
    'text': '#F9FAFB',  # Beyaz
    'text_secondary': '#9CA3AF'  # Gri
}

customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("blue")


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def check_password(password, hashed):
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed)
    except ValueError:
        return False


def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)


class AnimatedButton(customtkinter.CTkButton):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.original_fg_color = self.cget("fg_color")
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, event):
        self.configure(cursor="hand2")
        current_font = self.cget("font")
        if current_font:
            try:
                font_size = current_font.cget("size")
                self.configure(font=customtkinter.CTkFont(size=font_size + 1, weight="bold"))
            except:
                pass

    def on_leave(self, event):
        self.configure(cursor="arrow")
        current_font = self.cget("font")
        if current_font:
            try:
                font_size = self.cget("font").cget("size")
                self.configure(font=customtkinter.CTkFont(size=font_size - 1, weight="bold"))
            except:
                pass


class GradientFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=COLORS['primary'])


class RegisterWindow(customtkinter.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("🚀 Kayıt Ol - Keşfe Başla!")
        self.geometry("400x500")
        self.resizable(False, False)
        self.parent = parent
        self.configure(fg_color=COLORS['surface'])
        self.attributes("-topmost", True)
        main_frame = GradientFrame(self, corner_radius=20)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        title_label = customtkinter.CTkLabel(
            main_frame,
            text="🌟 Yeni Hesap Oluştur",
            font=customtkinter.CTkFont(size=28, weight="bold"),
            text_color=COLORS['text']
        )
        title_label.pack(pady=(30, 10))

        subtitle_label = customtkinter.CTkLabel(
            main_frame,
            text="Seyahat maceranız burada başlıyor!",
            font=customtkinter.CTkFont(size=14),
            text_color=COLORS['text_secondary']
        )
        subtitle_label.pack(pady=(0, 30))

        self.create_form_field(main_frame, "👤 Kullanıcı Adı:", "entry_user")
        self.create_form_field(main_frame, "🔒 Şifre:", "entry_pass", show="*")
        self.create_form_field(main_frame, "🔒 Şifre (Tekrar):", "entry_pass2", show="*")

        self.register_button = AnimatedButton(
            main_frame,
            text="✨ Kayıt Ol ve Keşfet!",
            command=self.register_user,
            font=customtkinter.CTkFont(size=16, weight="bold"),
            fg_color=COLORS['success'],
            hover_color="#059669",
            height=50,
            corner_radius=25
        )
        self.register_button.pack(pady=30, padx=40, fill="x")

        self.bind('<Return>', lambda event: self.register_user())

    def create_form_field(self, parent, label_text, entry_name, show=None):
        label = customtkinter.CTkLabel(
            parent,
            text=label_text,
            font=customtkinter.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text']
        )
        label.pack(pady=(10, 5))

        entry = customtkinter.CTkEntry(
            parent,
            font=customtkinter.CTkFont(size=14),
            height=40,
            corner_radius=20,
            show=show
        )
        entry.pack(pady=5, padx=40, fill="x")
        setattr(self, entry_name, entry)

    def register_user(self):
        username = self.entry_user.get().strip()
        password = self.entry_pass.get()
        password2 = self.entry_pass2.get()

        if not username or not password:
            self.show_error("❌ Hata", "Kullanıcı adı ve şifre boş olamaz.")
            return
        if password != password2:
            self.show_error("❌ Hata", "Şifreler eşleşmiyor.")
            return

        users = load_users()
        if username in users:
            self.show_error("❌ Hata", "Bu kullanıcı adı zaten kayıtlı.")
            return

        hashed_password = hash_password(password).decode('utf-8')
        users[username] = hashed_password
        save_users(users)
        self.show_success("🎉 Başarılı!", "Kayıt tamamlandı! Şimdi giriş yapabilirsiniz.")
        self.destroy()
        self.parent.focus()

    def show_error(self, title, message):
        messagebox.showerror(title, message)

    def show_success(self, title, message):
        messagebox.showinfo(title, message)


class LoginWindow(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("🗺️ Seyahat Takip - Giriş")
        self.geometry("450x800")
        self.resizable(False, False)
        self.configure(fg_color=COLORS['surface'])

        main_frame = GradientFrame(self, corner_radius=20)
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)

        logo_label = customtkinter.CTkLabel(
            main_frame,
            text="🌍",
            font=customtkinter.CTkFont(size=80)
        )
        logo_label.pack(pady=(40, 10))

        title_label = customtkinter.CTkLabel(
            main_frame,
            text="Seyahat Takip",
            font=customtkinter.CTkFont(size=32, weight="bold"),
            text_color=COLORS['text']
        )
        title_label.pack(pady=(0, 10))

        subtitle_label = customtkinter.CTkLabel(
            main_frame,
            text="Dünyayı keşfetmeye hazır mısın?",
            font=customtkinter.CTkFont(size=16),
            text_color=COLORS['text_secondary']
        )
        subtitle_label.pack(pady=(0, 40))

        self.create_login_field(main_frame, "👤 Kullanıcı Adı:", "entry_user")
        self.create_login_field(main_frame, "🔒 Şifre:", "entry_pass", show="*")

        self.login_button = AnimatedButton(
            main_frame,
            text="🚀 Keşfe Başla!",
            command=self.check_login,
            font=customtkinter.CTkFont(size=18, weight="bold"),
            fg_color=COLORS['accent'],
            hover_color="#2563EB",
            height=55,
            corner_radius=25
        )
        self.login_button.pack(pady=30, padx=50, fill="x")

        self.register_button = AnimatedButton(
            main_frame,
            text="✨ Yeni Hesap Oluştur",
            command=self.open_register,
            font=customtkinter.CTkFont(size=14, weight="bold"),
            fg_color="transparent",
            border_width=2,
            border_color=COLORS['accent'],
            text_color=COLORS['accent'],
            hover_color=COLORS['secondary'],
            height=45,
            corner_radius=20
        )
        self.register_button.pack(pady=10, padx=50, fill="x")

        self.bind('<Return>', lambda event: self.check_login())

    def create_login_field(self, parent, label_text, entry_name, show=None):
        label = customtkinter.CTkLabel(
            parent,
            text=label_text,
            font=customtkinter.CTkFont(size=16, weight="bold"),
            text_color=COLORS['text']
        )
        label.pack(pady=(15, 8))

        entry = customtkinter.CTkEntry(
            parent,
            font=customtkinter.CTkFont(size=16),
            height=45,
            corner_radius=20,
            show=show
        )
        entry.pack(pady=5, padx=50, fill="x")
        setattr(self, entry_name, entry)

    def check_login(self):
        username = self.entry_user.get().strip()
        password = self.entry_pass.get()

        users = load_users()
        if username in users and check_password(password, users[username].encode('utf-8')):
            self.destroy()
            self.open_main_app(username)
        else:
            messagebox.showerror("❌ Giriş Hatası", "Kullanıcı adı veya şifre hatalı!")

    def open_register(self):
        RegisterWindow(self)

    def open_main_app(self, username):
        app = App(username=username)
        app.mainloop()


def geocode_photon_multiple(address, parent):
    url = "https://photon.komoot.io/api/"
    params = {
        "q": address,
        "limit": 10
    }
    try:
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            features = data.get("features", [])
            if not features:
                messagebox.showerror("❌ Hata", "Adres bulunamadı.", parent=parent)
                return None

            options = []
            coords_list = []
            for f in features:
                props = f.get("properties", {})
                display_name = props.get("name", "")
                city = props.get("city", "")
                country = props.get("country", "")
                label = f"{display_name}"
                if city:
                    label += f", {city}"
                if country:
                    label += f", {country}"
                options.append(label)
                coords = f["geometry"]["coordinates"]
                coords_list.append((coords[1], coords[0]))

            dialog = customtkinter.CTkToplevel(parent)
            dialog.title("🎯 Yer Seçimi")
            dialog.geometry("450x400")
            dialog.configure(fg_color=COLORS['surface'])
            dialog.grab_set()

            main_frame = GradientFrame(dialog, corner_radius=15)
            main_frame.pack(fill="both", expand=True, padx=20, pady=20)

            label = customtkinter.CTkLabel(
                main_frame,
                text="📍 Lütfen adreslerden birini seçin:",
                font=customtkinter.CTkFont(size=16, weight="bold"),
                text_color=COLORS['text']
            )
            label.pack(pady=(20, 15))

            combo = customtkinter.CTkComboBox(
                main_frame,
                values=options,
                width=400,
                height=40,
                font=customtkinter.CTkFont(size=14),
                corner_radius=15
            )
            combo.pack(pady=10)
            combo.set(options[0])

            selected_coords = {"coords": None}

            def on_select():
                idx = combo.get()
                try:
                    index = options.index(idx)
                    selected_coords["coords"] = coords_list[index]
                    dialog.destroy()
                except ValueError:
                    messagebox.showerror("❌ Hata", "Geçersiz seçim", parent=dialog)

            btn = AnimatedButton(
                main_frame,
                text="✅ Seç ve Devam Et",
                command=on_select,
                font=customtkinter.CTkFont(size=14, weight="bold"),
                fg_color=COLORS['success'],
                height=40,
                corner_radius=20
            )
            btn.pack(pady=20)

            parent.wait_window(dialog)
            return selected_coords["coords"]

        else:
            messagebox.showerror("❌ Hata", f"Sunucu hatası: {response.status_code}", parent=parent)
    except Exception as e:
        messagebox.showerror("❌ Hata", f"İstek sırasında hata oluştu:\n{e}", parent=parent)
    return None


class CollapsibleFrame(customtkinter.CTkFrame):
    def __init__(self, master, text="", **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=COLORS['secondary'], corner_radius=15)
        self.show = tkinter.IntVar(value=1)

        self.header = AnimatedButton(
            self,
            text=f"▼ {text}",
            command=self.toggle,
            fg_color="transparent",
            hover_color=COLORS['primary'],
            font=customtkinter.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        self.header.pack(fill="x", padx=10, pady=5)

        self.sub_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.sub_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def toggle(self):
        if self.show.get():
            self.sub_frame.pack_forget()
            self.header.configure(text=self.header.cget("text").replace("▼", "▶"))
            self.show.set(0)
        else:
            self.sub_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
            self.header.configure(text=self.header.cget("text").replace("▶", "▼"))
            self.show.set(1)


class StatCard(customtkinter.CTkFrame):
    def __init__(self, master, title, value, icon, color, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=color, corner_radius=15, height=80)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        text_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        text_frame.grid(row=0, column=0, sticky="ew", padx=(15, 5), pady=15)

        self.value_label = customtkinter.CTkLabel(
            text_frame,
            text=str(value),
            font=customtkinter.CTkFont(size=24, weight="bold"),
            text_color="white"
        )
        self.value_label.pack(anchor="w")

        self.title_label = customtkinter.CTkLabel(
            text_frame,
            text=title,
            font=customtkinter.CTkFont(size=12),
            text_color="white"
        )
        self.title_label.pack(anchor="w")

        self.icon_label = customtkinter.CTkLabel(
            self,
            text=icon,
            font=customtkinter.CTkFont(size=30)
        )
        self.icon_label.grid(row=0, column=1, padx=(5, 15), pady=15)

    def update_value(self, new_value):
        self.value_label.configure(text=str(new_value))


class App(customtkinter.CTk):
    def __init__(self, username, **kwargs):
        super().__init__(**kwargs)
        self.username = username
        self.data_file = f"seyahat_verileri_{username}.json"
        self.media_folder = f"media_{username}"  # Medya klasörü
        os.makedirs(self.media_folder, exist_ok=True)  # Klasör oluştur

        self.title(APP_TITLE)
        self.geometry(GEOMETRY)
        self.minsize(1000, 700)
        self.configure(fg_color=COLORS['surface'])
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.to_visit_markers = []
        self.visited_markers = []

        self.setup_ui()
        self.load_data()
        self.update_stats()

        self.lists_window = None
        self.search_entry.bind('<Return>', lambda event: self.search_location())

    def setup_ui(self):
        self.left_frame = GradientFrame(self, corner_radius=30)
        self.left_frame.grid(row=0, column=0, sticky="ns", padx=10, pady=15)
        self.left_frame.grid_rowconfigure(9, weight=10)

        header_frame = customtkinter.CTkFrame(self.left_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=150, pady=(20, 15))

        self.label_title = customtkinter.CTkLabel(
            header_frame,
            text="🎛️ Kontrol Merkezi",
            font=customtkinter.CTkFont(size=24, weight="bold"),
            text_color=COLORS['text']
        )
        self.label_title.pack()

        search_frame = customtkinter.CTkFrame(self.left_frame, fg_color=COLORS['secondary'], corner_radius=15)
        search_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=0)
        search_frame.grid_columnconfigure(0, weight=1)

        search_label = customtkinter.CTkLabel(
            search_frame,
            text="🔍 Yer Ara",
            font=customtkinter.CTkFont(size=16, weight="bold"),
            text_color=COLORS['text']
        )
        search_label.grid(row=0, column=0, columnspan=2, pady=(5, 10))

        self.search_entry = customtkinter.CTkEntry(
            search_frame,
            placeholder_text="Şehir, ülke veya mekan ara...",
            font=customtkinter.CTkFont(size=14),
            height=40,
            corner_radius=20
        )
        self.search_entry.grid(row=1, column=0, padx=(15, 5), pady=(0, 15), sticky="ew")

        self.search_button = AnimatedButton(
            search_frame,
            text="🔍",
            width=60,
            height=40,
            command=lambda: self.search_location(),
            fg_color=COLORS['accent'],
            corner_radius=20,
            font=customtkinter.CTkFont(size=16)
        )
        self.search_button.grid(row=1, column=1, padx=(0, 15), pady=(0, 15))

        stats_frame = customtkinter.CTkFrame(self.left_frame, fg_color="transparent")
        stats_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=20, pady=10)
        stats_frame.grid_columnconfigure((0, 1), weight=1)

        self.to_visit_card = StatCard(
            stats_frame,
            title="Gezmek İstediğim",
            value=0,
            icon="📍",
            color=COLORS['warning']
        )
        self.to_visit_card.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        self.visited_card = StatCard(
            stats_frame,
            title="Gezdiğim",
            value=0,
            icon="✅",
            color=COLORS['success']
        )
        self.visited_card.grid(row=0, column=1, padx=(5, 0), sticky="ew")

        # GELİŞTİRİLMİŞ İSTATİSTİK PANELİ
        advanced_stats_frame = customtkinter.CTkFrame(self.left_frame, fg_color="transparent")
        advanced_stats_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=20, pady=10)
        advanced_stats_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.total_countries_card = StatCard(
            advanced_stats_frame,
            title="Ülke Sayısı",
            value=0,
            icon="🌍",
            color='#8B5CF6'
        )
        self.total_countries_card.grid(row=0, column=0, padx=(0, 3), sticky="ew")

        self.monthly_visits_card = StatCard(
            advanced_stats_frame,
            title="Bu Ay",
            value=0,
            icon="📅",
            color='#06B6D4'
        )
        self.monthly_visits_card.grid(row=0, column=1, padx=3, sticky="ew")

        self.with_media_card = StatCard(
            advanced_stats_frame,
            title="Medyalı",
            value=0,
            icon="📸",
            color='#F59E0B'
        )
        self.with_media_card.grid(row=0, column=2, padx=(3, 0), sticky="ew")

        self.setup_map_controls()
        self.setup_quick_actions()
        self.setup_advanced_features()
        self.setup_main_buttons()
        self.setup_map_panel()

    def setup_map_controls(self):
        view_frame = customtkinter.CTkFrame(self.left_frame, fg_color=COLORS['secondary'], corner_radius=15)
        view_frame.grid(row=4, column=0, columnspan=2, sticky="ew", padx=20, pady=10)

        view_label = customtkinter.CTkLabel(
            view_frame,
            text="🗺️ Harita Görünümü",
            font=customtkinter.CTkFont(size=16, weight="bold"),
            text_color=COLORS['text']
        )
        view_label.pack(pady=(15, 10))

        self.map_type = customtkinter.CTkComboBox(
            view_frame,
            values=["OpenStreetMap", "Google Normal", "Google Satellite"],
            command=self.change_map_type,
            font=customtkinter.CTkFont(size=14),
            height=35,
            corner_radius=15
        )
        self.map_type.pack(pady=(0, 15), padx=15, fill="x")
        self.map_type.set("OpenStreetMap")

    def setup_quick_actions(self):
        actions_frame = customtkinter.CTkFrame(self.left_frame, fg_color=COLORS['secondary'], corner_radius=15)
        actions_frame.grid(row=5, column=0, columnspan=2, sticky="ew", padx=20, pady=10)

        actions_label = customtkinter.CTkLabel(
            actions_frame,
            text="⚡ Hızlı İşlemler",
            font=customtkinter.CTkFont(size=16, weight="bold"),
            text_color=COLORS['text']
        )
        actions_label.pack(pady=(0, 10))

        buttons = [

            ("🎯 Haritayı Ortala", self.center_map, COLORS['primary']),
            ("🗑️ Temizle", self.clear_all_markers, COLORS['danger'])
        ]

        for text, command, color in buttons:
            btn = AnimatedButton(
                actions_frame,
                text=text,
                command=command,
                fg_color=color,
                height=35,
                corner_radius=15,
                font=customtkinter.CTkFont(size=12, weight="bold")
            )
            btn.pack(fill="x", padx=15, pady=3)

        btn.pack_configure(pady=(3, 15))

    def setup_advanced_features(self):
        advanced_frame = customtkinter.CTkFrame(self.left_frame, fg_color=COLORS['secondary'], corner_radius=15)
        advanced_frame.grid(row=6, column=0, columnspan=2, sticky="ew", padx=20, pady=10)

        advanced_label = customtkinter.CTkLabel(
            advanced_frame,
            text="🛠️ Gelişmiş Özellikler",
            font=customtkinter.CTkFont(size=16, weight="bold"),
            text_color=COLORS['text']
        )
        advanced_label.pack(pady=(5, 10))

        advanced_buttons = [
            ("📤 Dışa Aktar", self.export_data, COLORS['accent']),
            ("📥 İçe Aktar", self.import_data, COLORS['accent']),
            ("💾 Yedek Oluştur", self.create_backup, COLORS['warning'])
        ]

        for text, command, color in advanced_buttons:
            btn = AnimatedButton(
                advanced_frame,
                text=text,
                command=command,
                fg_color=color,
                height=35,
                corner_radius=15,
                font=customtkinter.CTkFont(size=12, weight="bold")
            )
            btn.pack(fill="x", padx=15, pady=3)

        btn.pack_configure(pady=(3, 15))

    def setup_main_buttons(self):
        # İSTATİSTİK BUTONU
        self.stats_button = AnimatedButton(
            self.left_frame,
            text="📊 Detaylı İstatistikler",
            command=self.open_stats_window,
            height=30,
            font=customtkinter.CTkFont(size=14, weight="bold"),
            fg_color='#8B5CF6',
            hover_color='#7C3AED',
            corner_radius=20
        )
        self.stats_button.grid(row=7, column=0, columnspan=2, padx=20, pady=15, sticky="ew")

        self.show_lists_button = AnimatedButton(
            self.left_frame,
            text="📋 Listelerim",
            command=self.open_lists_window,
            height=30,
            font=customtkinter.CTkFont(size=14, weight="bold"),
            fg_color=COLORS['success'],
            hover_color="#059669",
            corner_radius=20
        )
        self.show_lists_button.grid(row=8, column=0, columnspan=2, padx=20, pady=15, sticky="ew")

    def setup_map_panel(self):
        self.right_frame = GradientFrame(self, corner_radius=20)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 20), pady=15)
        self.grid_columnconfigure(1, weight=1)

        map_header = customtkinter.CTkFrame(self.right_frame, fg_color="transparent", height=60)
        map_header.pack(fill="x", padx=15, pady=(15, 10))

        map_title = customtkinter.CTkLabel(
            map_header,
            text="🗺️ Keşif Haritası",
            font=customtkinter.CTkFont(size=20, weight="bold"),
            text_color=COLORS['text']
        )
        map_title.pack(side="left")

        map_container = customtkinter.CTkFrame(self.right_frame, corner_radius=15, fg_color=COLORS['secondary'])
        map_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self.map_widget = TkinterMapView(map_container, corner_radius=15)
        self.map_widget.pack(fill="both", expand=True, padx=3, pady=3)

        self.map_widget.add_right_click_menu_command(
            label="📍 Gezmek İstediğim Yerler'e Ekle",
            command=self.add_marker_event,
            pass_coords=True
        )
        self.map_widget.add_right_click_menu_command(
            label="✅ Gezdiğim Yerler'e Ekle",
            command=lambda coords: self.add_marker_event(coords, marker_type="visited"),
            pass_coords=True
        )

        self.map_widget.set_position(41.0082, 28.9784)
        self.map_widget.set_zoom(5)

    def change_map_type(self, value):
        if value == "Google Normal":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}")
        elif value == "Google Satellite":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}")
        else:
            self.map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")

    def search_location(self, event=None):
        address = self.search_entry.get().strip()
        if not address:
            messagebox.showwarning("⚠️ Uyarı", "Lütfen bir konum girin.")
            return

        original_text = self.search_button.cget("text")
        self.search_button.configure(text="⏳", state="disabled")
        self.update()

        def search_thread():
            try:
                coords = geocode_photon_multiple(address, self)
                if coords:
                    self.after(0, lambda: self.handle_search_result(coords, address))
                else:
                    self.after(0, lambda: self.search_button.configure(text=original_text, state="normal"))
            except Exception as e:
                self.after(0, lambda: [
                    messagebox.showerror("❌ Hata", f"Arama sırasında hata: {e}"),
                    self.search_button.configure(text=original_text, state="normal")
                ])

        threading.Thread(target=search_thread, daemon=True).start()

    def handle_search_result(self, coords, address):
        lat, lon = coords
        self.map_widget.set_position(lat, lon)
        self.map_widget.set_zoom(12)

        temp_marker = self.map_widget.set_marker(lat, lon, text=f"🔍 {address}")
        self.after(3000, lambda: temp_marker.delete() if temp_marker else None)

        self.search_button.configure(text="🔍", state="normal")
        self.search_entry.delete(0, tkinter.END)

    def save_media_files(self, files, location_name):
        if not files:
            return []

        media_paths = []
        safe_name = "".join(c for c in location_name if c.isalnum() or c in (' ', '-', '_')).rstrip()

        for i, file_path in enumerate(files):
            try:
                file_ext = os.path.splitext(file_path)[1]
                new_filename = f"{safe_name}_{i + 1}{file_ext}"
                new_path = os.path.join(self.media_folder, new_filename)

                shutil.copy2(file_path, new_path)
                media_paths.append(new_path)
            except Exception as e:
                messagebox.showerror("❌ Hata", f"Medya dosyası kaydedilemedi: {e}")

        return media_paths

    def show_media_preview(self, files):
        preview_window = customtkinter.CTkToplevel(self)
        preview_window.title("👁️ Medya Önizleme")
        preview_window.geometry("600x500")
        preview_window.configure(fg_color=COLORS['surface'])
        preview_window.attributes("-topmost", True)
        main_frame = GradientFrame(preview_window, corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        title_label = customtkinter.CTkLabel(
            main_frame,
            text="📷 Seçilen Medya Dosyaları",
            font=customtkinter.CTkFont(size=18, weight="bold"),
            text_color=COLORS['text']
        )
        title_label.pack(pady=(15, 20))

        scroll_frame = customtkinter.CTkScrollableFrame(main_frame)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        for i, file_path in enumerate(files):
            file_frame = customtkinter.CTkFrame(scroll_frame, fg_color=COLORS['secondary'], corner_radius=10)
            file_frame.pack(fill="x", pady=5, padx=5)

            filename = os.path.basename(file_path)
            file_label = customtkinter.CTkLabel(
                file_frame,
                text=f"📁 {filename}",
                font=customtkinter.CTkFont(size=12, weight="bold"),
                anchor="w"
            )
            file_label.pack(side="left", padx=10, pady=10)

            def open_file(path=file_path):
                try:
                    if platform.system() == 'Darwin':  # macOS
                        subprocess.call(('open', path))
                    elif platform.system() == 'Windows':  # Windows
                        os.startfile(path)
                    else:  # linux
                        subprocess.call(('xdg-open', path))
                except Exception as e:
                    messagebox.showerror("❌ Hata", f"Dosya açılamadı: {e}")

            open_btn = AnimatedButton(
                file_frame,
                text="🔍 Aç",
                command=open_file,
                fg_color=COLORS['accent'],
                width=60,
                height=30,
                corner_radius=10
            )
            open_btn.pack(side="right", padx=10, pady=10)

    def add_marker_event(self, coords, marker_type="to_visit"):
        lat, lon = coords

        def get_location_name():
            try:
                url = "https://photon.komoot.io/reverse"
                params = {"lat": lat, "lon": lon}
                response = requests.get(url, params=params, timeout=3)
                if response.status_code == 200:
                    data = response.json()
                    features = data.get("features", [])
                    if features:
                        props = features[0].get("properties", {})
                        name = props.get("name", "")
                        city = props.get("city", "")
                        country = props.get("country", "")
                        return f"{name}, {city}, {country}" if all(
                            [name, city, country]) else f"Lat: {lat:.4f}, Lon: {lon:.4f}"
                    return f"Lat: {lat:.4f}, Lon: {lon:.4f}"
            except:
                return f"Lat: {lat:.4f}, Lon: {lon:.4f}"

        location_name = get_location_name()

        dialog = customtkinter.CTkToplevel(self)
        dialog.title("📍 Yeni Yer Ekle")
        dialog.geometry("400x550")
        dialog.configure(fg_color=COLORS['surface'])
        dialog.grab_set()

        main_frame = GradientFrame(dialog, corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        title_label = customtkinter.CTkLabel(
            main_frame,
            text="🌟 Yeni Keşif Noktası",
            font=customtkinter.CTkFont(size=20, weight="bold"),
            text_color=COLORS['text']
        )
        title_label.pack(pady=(20, 15))

        name_label = customtkinter.CTkLabel(
            main_frame,
            text="📍 Yer Adı:",
            font=customtkinter.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text']
        )
        name_label.pack(pady=(10, 5))

        name_entry = customtkinter.CTkEntry(
            main_frame,
            font=customtkinter.CTkFont(size=14),
            height=35,
            corner_radius=15
        )
        name_entry.pack(fill="x", padx=20, pady=5)
        name_entry.insert(0, location_name)

        media_label = customtkinter.CTkLabel(
            main_frame,
            text="📷 Medya Ekle (İsteğe bağlı):",
            font=customtkinter.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text']
        )
        media_label.pack(pady=(10, 5))

        media_frame = customtkinter.CTkFrame(main_frame, fg_color=COLORS['secondary'], corner_radius=10)
        media_frame.pack(fill="x", padx=20, pady=5)

        selected_media = {"files": []}

        def select_media():
            files = filedialog.askopenfilenames(
                title="Foto/Video Seç",
                filetypes=[
                    ("Medya Dosyaları", "*.jpg *.jpeg *.png *.mp4 *.avi *.mov"),
                    ("Resim Dosyaları", "*.jpg *.jpeg *.png"),
                    ("Video Dosyaları", "*.mp4 *.avi *.mov"),
                    ("Tüm Dosyalar", "*.*")
                ]
            )
            if files:
                selected_media["files"] = list(files)
                media_info.configure(text=f"📁 {len(files)} dosya seçildi")
                preview_btn.configure(state="normal")

        def preview_media():
            if selected_media["files"]:
                self.show_media_preview(selected_media["files"])

        select_media_btn = AnimatedButton(
            media_frame,
            text="📂 Medya Seç",
            command=select_media,
            fg_color=COLORS['accent'],
            height=35,
            corner_radius=15,
            font=customtkinter.CTkFont(size=12)
        )
        select_media_btn.pack(side="left", padx=10, pady=10)

        preview_btn = AnimatedButton(
            media_frame,
            text="👁️ Önizle",
            command=preview_media,
            fg_color=COLORS['warning'],
            height=35,
            corner_radius=15,
            font=customtkinter.CTkFont(size=12),
            state="disabled"
        )
        preview_btn.pack(side="left", padx=5, pady=10)

        media_info = customtkinter.CTkLabel(
            media_frame,
            text="📷 Henüz medya seçilmedi",
            font=customtkinter.CTkFont(size=11),
            text_color=COLORS['text_secondary']
        )
        media_info.pack(side="right", padx=10, pady=10)

        note_label = customtkinter.CTkLabel(
            main_frame,
            text="📝 Notlar (İsteğe bağlı):",
            font=customtkinter.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text']
        )
        note_label.pack(pady=(10, 5))

        note_entry = customtkinter.CTkTextbox(
            main_frame,
            height=60,
            font=customtkinter.CTkFont(size=12),
            corner_radius=10
        )
        note_entry.pack(fill="x", padx=20, pady=5)

        button_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=20)
        button_frame.grid_columnconfigure((0, 1), weight=1)

        def add_to_visit():
            name = name_entry.get().strip()
            note = note_entry.get("1.0", tkinter.END).strip()
            if name:
                media_paths = self.save_media_files(selected_media["files"], name)
                self.add_location("to_visit", name, lat, lon, note, media_paths)
                dialog.destroy()

        def add_visited():
            name = name_entry.get().strip()
            note = note_entry.get("1.0", tkinter.END).strip()
            if name:
                media_paths = self.save_media_files(selected_media["files"], name)
                self.add_location("visited", name, lat, lon, note, media_paths)
                dialog.destroy()

        btn_to_visit = AnimatedButton(
            button_frame,
            text="📍 Gitmek İstiyorum",
            command=add_to_visit,
            fg_color=COLORS['warning'],
            height=40,
            corner_radius=20
        )
        btn_to_visit.grid(row=0, column=0, padx=(20, 10), sticky="ew")

        btn_visited = AnimatedButton(
            button_frame,
            text="✅ Gittim",
            command=add_visited,
            fg_color=COLORS['success'],
            height=40,
            corner_radius=20
        )
        btn_visited.grid(row=0, column=1, padx=(10, 20), sticky="ew")

    def add_location(self, list_type, name, lat, lon, note="", media_paths=None):
        if media_paths is None:
            media_paths = []

        if list_type == "to_visit":
            color = "orange"
            icon = "📍"
        else:
            color = "green"
            icon = "✅"

        marker = self.map_widget.set_marker(lat, lon, text=f"{icon} {name}", marker_color_circle=color,
                                            marker_color_outside=color)

        location_data = {
            "name": name,
            "lat": lat,
            "lon": lon,
            "note": note,
            "media_paths": media_paths,
            "date_added": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "marker": marker
        }

        if list_type == "to_visit":
            self.to_visit_markers.append(location_data)
        else:
            self.visited_markers.append(location_data)

        self.save_data()
        self.update_stats()

        if self.lists_window and self.lists_window.winfo_exists():
            self.lists_window.refresh_lists()

        messagebox.showinfo("🎉 Başarılı!",
                            f"'{name}' {('gezmek istediğin' if list_type == 'to_visit' else 'gezdiğin')} yerlere eklendi!")

    def center_map(self):
        self.map_widget.set_position(41.0082, 28.9784)
        self.map_widget.set_zoom(5)

    def clear_all_markers(self):
        result = messagebox.askyesno(
            "⚠️ Onay",
            "Tüm işaretleri silmek istediğinize emin misiniz?\nBu işlem geri alınamaz!"
        )
        if result:
            for location in self.to_visit_markers:
                if location.get("marker"):
                    location["marker"].delete()
            for location in self.visited_markers:
                if location.get("marker"):
                    location["marker"].delete()

            self.to_visit_markers.clear()
            self.visited_markers.clear()

            self.save_data()
            self.update_stats()

            if self.lists_window and self.lists_window.winfo_exists():
                self.lists_window.refresh_lists()

            messagebox.showinfo("🗑️ Temizlendi", "Tüm işaretler başarıyla silindi.")

    def update_stats(self):
        to_visit_count = len(self.to_visit_markers)
        visited_count = len(self.visited_markers)

        self.to_visit_card.update_value(to_visit_count)
        self.visited_card.update_value(visited_count)

        countries = set()
        for location in self.visited_markers + self.to_visit_markers:
            # Basit ülke çıkarımı (geocoding sonucundan gelebilir)
            name_parts = location['name'].split(',')
            if len(name_parts) > 1:
                countries.add(name_parts[-1].strip())
        self.total_countries_card.update_value(len(countries))
        current_month = datetime.now().strftime("%Y-%m")
        monthly_count = sum(1 for loc in self.visited_markers
                            if loc['date_added'].startswith(current_month))
        self.monthly_visits_card.update_value(monthly_count)
        media_count = sum(1 for loc in self.visited_markers + self.to_visit_markers
                          if loc.get('media_paths') and len(loc['media_paths']) > 0)
        self.with_media_card.update_value(media_count)

    def open_lists_window(self):
        if self.lists_window is None or not self.lists_window.winfo_exists():
            self.lists_window = ListsWindow(self)
        else:
            self.lists_window.lift()
            self.lists_window.focus()

    def open_stats_window(self):
        stats_window = customtkinter.CTkToplevel(self)
        stats_window.title("📊 Seyahat İstatistikleri")
        stats_window.geometry("1000x700")
        stats_window.configure(fg_color=COLORS['surface'])
        stats_window.attributes("-topmost", True)
        main_frame = GradientFrame(stats_window, corner_radius=20)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        title_label = customtkinter.CTkLabel(
            main_frame,
            text="📊 Detaylı Seyahat Analizi",
            font=customtkinter.CTkFont(size=24, weight="bold"),
            text_color=COLORS['text']
        )
        title_label.pack(pady=(15, 25))

        notebook = customtkinter.CTkTabview(main_frame)
        notebook.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        general_tab = notebook.add("📈 Genel")
        self.create_general_stats(general_tab)
        time_tab = notebook.add("📅 Zaman")
        self.create_time_analysis(time_tab)
    def create_general_stats(self, parent):
        scroll_frame = customtkinter.CTkScrollableFrame(parent)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        summary_frame = customtkinter.CTkFrame(scroll_frame, fg_color="transparent")
        summary_frame.pack(fill="x", pady=(0, 20))
        summary_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        total_locations = len(self.visited_markers) + len(self.to_visit_markers)
        completion_rate = (len(self.visited_markers) / total_locations * 100) if total_locations > 0 else 0

        cards_data = [
            ("Toplam Lokasyon", total_locations, "🎯", COLORS['accent']),
            ("Tamamlanma", f"{completion_rate:.1f}%", "✅", COLORS['success']),
            ("Medya Oranı", f"{self.calculate_media_percentage():.1f}%", "📷", '#8B5CF6')
        ]

        for i, (title, value, icon, color) in enumerate(cards_data):
            card = StatCard(summary_frame, title=title, value=value, icon=icon, color=color)
            card.grid(row=0, column=i, padx=5, sticky="ew")

        popular_frame = customtkinter.CTkFrame(scroll_frame, fg_color=COLORS['secondary'], corner_radius=15)
        popular_frame.pack(fill="x", pady=10)

        popular_title = customtkinter.CTkLabel(
            popular_frame,
            text="🏆 En Çok Ziyaret Edilen Bölgeler",
            font=customtkinter.CTkFont(size=16, weight="bold"),
            text_color=COLORS['text']
        )
        popular_title.pack(pady=(15, 10))

        regions = defaultdict(int)
        for loc in self.visited_markers:
            # Şehir/bölge çıkarımı
            parts = loc['name'].split(',')
            if len(parts) > 1:
                region = parts[-2].strip() if len(parts) > 2 else parts[-1].strip()
                regions[region] += 1

        sorted_regions = sorted(regions.items(), key=lambda x: x[1], reverse=True)[:5]

        for i, (region, count) in enumerate(sorted_regions):
            region_frame = customtkinter.CTkFrame(popular_frame, fg_color=COLORS['primary'], corner_radius=10)
            region_frame.pack(fill="x", padx=15, pady=3)

            region_label = customtkinter.CTkLabel(
                region_frame,
                text=f"{i + 1}. {region}",
                font=customtkinter.CTkFont(size=12, weight="bold"),
                anchor="w"
            )
            region_label.pack(side="left", padx=15, pady=8)

            count_label = customtkinter.CTkLabel(
                region_frame,
                text=f"{count} yer",
                font=customtkinter.CTkFont(size=11),
                text_color=COLORS['text_secondary']
            )
            count_label.pack(side="right", padx=15, pady=8)

        if not sorted_regions:
            no_data_label = customtkinter.CTkLabel(
                popular_frame,
                text="📊 Henüz yeterli veri yok",
                font=customtkinter.CTkFont(size=12),
                text_color=COLORS['text_secondary']
            )
            no_data_label.pack(pady=20)

        popular_frame.pack_configure(pady=(10, 15))

    def create_time_analysis(self, parent):
        scroll_frame = customtkinter.CTkScrollableFrame(parent)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        monthly_data = defaultdict(int)
        for loc in self.visited_markers:
            month = loc['date_added'][:7]  # YYYY-MM
            monthly_data[month] += 1

        if monthly_data:
            fig, ax1 = plt.subplots(1, 1, figsize=(10, 4))
            fig.patch.set_facecolor('#111827')

            months = sorted(monthly_data.keys())
            values = [monthly_data[month] for month in months]

            ax1.plot(months, values, marker='o', linewidth=2, markersize=6, color='#3B82F6')
            ax1.set_title('Aylık Ziyaret Trendi', color='white', fontsize=14, fontweight='bold')
            ax1.set_facecolor('#1F2937')
            ax1.tick_params(colors='white', rotation=45)
            ax1.grid(True, alpha=0.3)

            for spine in ax1.spines.values():
                spine.set_color('white')

            plt.tight_layout()

            canvas_frame = customtkinter.CTkFrame(scroll_frame, fg_color=COLORS['secondary'])
            canvas_frame.pack(fill="both", expand=True, pady=10)

            canvas = FigureCanvasTkAgg(fig, canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        else:
            no_data_label = customtkinter.CTkLabel(
                scroll_frame,
                text="📊 Henüz zaman analizi için yeterli veri yok",
                font=customtkinter.CTkFont(size=16),
                text_color=COLORS['text_secondary']
            )
            no_data_label.pack(pady=50)



    def calculate_avg_note_length(self):
        total_chars = 0
        count = 0

        for loc in self.visited_markers + self.to_visit_markers:
            note = loc.get('note', '')
            if note and note.strip():
                total_chars += len(note.strip())
                count += 1

        return f"{total_chars // count if count > 0 else 0} kar."

    def calculate_media_percentage(self):
        total = len(self.visited_markers) + len(self.to_visit_markers)
        if total == 0:
            return 0

        with_media = sum(1 for loc in self.visited_markers + self.to_visit_markers
                         if loc.get('media_paths') and len(loc['media_paths']) > 0)

        return (with_media / total) * 100

    def export_data(self):
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            if filename:
                export_data = {
                    "to_visit": [
                        {
                            "name": loc["name"],
                            "lat": loc["lat"],
                            "lon": loc["lon"],
                            "note": loc["note"],
                            "media_paths": loc.get("media_paths", []),
                            "date_added": loc["date_added"]
                        } for loc in self.to_visit_markers
                    ],
                    "visited": [
                        {
                            "name": loc["name"],
                            "lat": loc["lat"],
                            "lon": loc["lon"],
                            "note": loc["note"],
                            "media_paths": loc.get("media_paths", []),
                            "date_added": loc["date_added"]
                        } for loc in self.visited_markers
                    ]
                }

                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(export_data, f, indent=4, ensure_ascii=False)

                messagebox.showinfo("✅ Başarılı!", f"Veriler başarıyla dışa aktarıldı:\n{filename}")
        except Exception as e:
            messagebox.showerror("❌ Hata", f"Dışa aktarma sırasında hata:\n{e}")

    def import_data(self):
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            if filename:
                with open(filename, "r", encoding="utf-8") as f:
                    import_data = json.load(f)

                for location in self.to_visit_markers:
                    if location.get("marker"):
                        location["marker"].delete()
                for location in self.visited_markers:
                    if location.get("marker"):
                        location["marker"].delete()

                self.to_visit_markers.clear()
                self.visited_markers.clear()

                for item in import_data.get("to_visit", []):
                    marker = self.map_widget.set_marker(
                        item["lat"], item["lon"],
                        text=f"📍 {item['name']}",
                        marker_color_circle="orange",
                        marker_color_outside="orange"
                    )
                    item["marker"] = marker
                    if "media_paths" not in item:
                        item["media_paths"] = []
                    self.to_visit_markers.append(item)

                for item in import_data.get("visited", []):
                    marker = self.map_widget.set_marker(
                        item["lat"], item["lon"],
                        text=f"✅ {item['name']}",
                        marker_color_circle="green",
                        marker_color_outside="green"
                    )
                    item["marker"] = marker
                    if "media_paths" not in item:
                        item["media_paths"] = []
                    self.visited_markers.append(item)

                self.save_data()
                self.update_stats()

                if self.lists_window and self.lists_window.winfo_exists():
                    self.lists_window.refresh_lists()

                messagebox.showinfo("✅ Başarılı!", "Veriler başarıyla içe aktarıldı!")
        except Exception as e:
            messagebox.showerror("❌ Hata", f"İçe aktarma sırasında hata:\n{e}")

    def create_backup(self):
        try:
            backup_filename = f"seyahat_yedek_{self.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            export_data = {
                "to_visit": [
                    {
                        "name": loc["name"],
                        "lat": loc["lat"],
                        "lon": loc["lon"],
                        "note": loc["note"],
                        "media_paths": loc.get("media_paths", []),
                        "date_added": loc["date_added"]
                    } for loc in self.to_visit_markers
                ],
                "visited": [
                    {
                        "name": loc["name"],
                        "lat": loc["lat"],
                        "lon": loc["lon"],
                        "note": loc["note"],
                        "media_paths": loc.get("media_paths", []),
                        "date_added": loc["date_added"]
                    } for loc in self.visited_markers
                ]
            }

            with open(backup_filename, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=4, ensure_ascii=False)

            messagebox.showinfo("💾 Yedek Oluşturuldu!", f"Yedek dosyası oluşturuldu:\n{backup_filename}")
        except Exception as e:
            messagebox.showerror("❌ Hata", f"Yedekleme sırasında hata:\n{e}")

    def load_data(self):
        if not os.path.exists(self.data_file):
            return

        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, dict):
                messagebox.showwarning("⚠️ Uyarı",
                                       "Veri dosyası beklenen formatta değil (sözlük bekleniyor). Yeni bir oturum başlatılıyor.")
                return

            for item in data.get("to_visit", []):
                if not isinstance(item, dict) or not all(key in item for key in ["lat", "lon", "name"]):
                    messagebox.showwarning("⚠️ Uyarı",
                                           "Geçersiz veri formatı: 'to_visit' listesindeki bir öğe eksik veya hatalı.")
                    continue
                marker = self.map_widget.set_marker(
                    item["lat"], item["lon"],
                    text=f"📍 {item['name']}",
                    marker_color_circle="orange",
                    marker_color_outside="orange"
                )
                item["marker"] = marker
                if "media_paths" not in item:
                    item["media_paths"] = []
                self.to_visit_markers.append(item)

            for item in data.get("visited", []):
                if not isinstance(item, dict) or not all(key in item for key in ["lat", "lon", "name"]):
                    messagebox.showwarning("⚠️ Uyarı",
                                           "Geçersiz veri formatı: 'visited' listesindeki bir öğe eksik veya hatalı.")
                    continue
                marker = self.map_widget.set_marker(
                    item["lat"], item["lon"],
                    text=f"✅ {item['name']}",
                    marker_color_circle="green",
                    marker_color_outside="green"
                )
                item["marker"] = marker
                if "media_paths" not in item:
                    item["media_paths"] = []
                self.visited_markers.append(item)

        except (json.JSONDecodeError, FileNotFoundError):
            messagebox.showwarning("⚠️ Uyarı", "Veri dosyası okunurken hata oluştu. Yeni bir oturum başlatılıyor.")
        except Exception as e:
            messagebox.showerror("❌ Hata", f"Veri yüklenirken beklenmeyen hata: {e}")

    def save_data(self):
        data = {
            "to_visit": [
                {
                    "name": item["name"],
                    "lat": item["lat"],
                    "lon": item["lon"],
                    "note": item["note"],
                    "media_paths": item.get("media_paths", []),
                    "date_added": item["date_added"]
                } for item in self.to_visit_markers
            ],
            "visited": [
                {
                    "name": item["name"],
                    "lat": item["lat"],
                    "lon": item["lon"],
                    "note": item["note"],
                    "media_paths": item.get("media_paths", []),
                    "date_added": item["date_added"]
                } for item in self.visited_markers
            ]
        }

        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("❌ Hata", f"Veri kaydedilirken hata:\n{e}")

    def on_closing(self):
        self.after_cancel_all()
        self.save_data()
        self.destroy()

    def after_cancel_all(self):
        try:
            after_ids = self.tk.call('after', 'info')
            if after_ids:
                for after_id in after_ids.split():
                    try:
                        self.after_cancel(after_id)
                    except Exception:
                        pass
        except Exception:
            pass

class ListsWindow(customtkinter.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("📋 Keşif Listem")
        self.geometry("800x600")
        self.configure(fg_color=COLORS['surface'])
        self.attributes("-topmost", True)
        self.setup_ui()
        self.refresh_lists()

    def setup_ui(self):
        main_frame = GradientFrame(self, corner_radius=20)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        title_label = customtkinter.CTkLabel(
            main_frame,
            text="🗺️ Seyahat Listem",
            font=customtkinter.CTkFont(size=28, weight="bold"),
            text_color=COLORS['text']
        )
        title_label.pack(pady=(0, 30))

        self.notebook = customtkinter.CTkTabview(main_frame)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.to_visit_tab = self.notebook.add("📍 Gezmek İstediğim")
        self.visited_tab = self.notebook.add("✅ Gezdiğim")

        self.setup_to_visit_tab()
        self.setup_visited_tab()

    def setup_to_visit_tab(self):
        self.to_visit_scroll = customtkinter.CTkScrollableFrame(
            self.to_visit_tab,
            fg_color="transparent"
        )
        self.to_visit_scroll.pack(fill="both", expand=True, padx=10, pady=10)

    def setup_visited_tab(self):
        self.visited_scroll = customtkinter.CTkScrollableFrame(
            self.visited_tab,
            fg_color="transparent"
        )
        self.visited_scroll.pack(fill="both", expand=True, padx=10, pady=10)

    def refresh_lists(self):
        for widget in self.to_visit_scroll.winfo_children():
            widget.destroy()
        for widget in self.visited_scroll.winfo_children():
            widget.destroy()

        if not self.parent.to_visit_markers:
            no_data_label = customtkinter.CTkLabel(
                self.to_visit_scroll,
                text="🤔 Henüz hiç yer eklemedin!\nHaritaya sağ tıklayarak yeni yerler ekleyebilirsin.",
                font=customtkinter.CTkFont(size=16),
                text_color=COLORS['text_secondary']
            )
            no_data_label.pack(pady=50)
        else:
            for i, location in enumerate(self.parent.to_visit_markers):
                self.create_location_card(self.to_visit_scroll, location, "to_visit", i)

        if not self.parent.visited_markers:
            no_data_label = customtkinter.CTkLabel(
                self.visited_scroll,
                text="🌟 Henüz hiç yere gitmedin!\nGittiğin yerleri işaretleyerek anılarını koruyabilirsin.",
                font=customtkinter.CTkFont(size=16),
                text_color=COLORS['text_secondary']
            )
            no_data_label.pack(pady=50)
        else:
            for i, location in enumerate(self.parent.visited_markers):
                self.create_location_card(self.visited_scroll, location, "visited", i)

    def create_location_card(self, parent, location, list_type, index):
        card = customtkinter.CTkFrame(
            parent,
            fg_color=COLORS['secondary'],
            corner_radius=15,
            height=120
        )
        card.pack(fill="x", padx=10, pady=5)
        card.grid_propagate(False)

        card.grid_columnconfigure(1, weight=1)

        icon = "📍" if list_type == "to_visit" else "✅"
        icon_label = customtkinter.CTkLabel(
            card,
            text=icon,
            font=customtkinter.CTkFont(size=30)
        )
        icon_label.grid(row=0, column=0, rowspan=3, padx=15, pady=15, sticky="n")

        name_label = customtkinter.CTkLabel(
            card,
            text=location["name"],
            font=customtkinter.CTkFont(size=16, weight="bold"),
            text_color=COLORS['text'],
            anchor="w"
        )
        name_label.grid(row=0, column=1, sticky="ew", padx=10, pady=(15, 5))

        coords_text = f"📍 {location['lat']:.4f}, {location['lon']:.4f}"
        coords_label = customtkinter.CTkLabel(
            card,
            text=coords_text,
            font=customtkinter.CTkFont(size=12),
            text_color=COLORS['text_secondary'],
            anchor="w"
        )
        coords_label.grid(row=1, column=1, sticky="ew", padx=10)

        date_text = f"📅 {location['date_added']}"
        date_label = customtkinter.CTkLabel(
            card,
            text=date_text,
            font=customtkinter.CTkFont(size=11),
            text_color=COLORS['text_secondary'],
            anchor="w"
        )
        date_label.grid(row=2, column=1, sticky="ew", padx=10, pady=(0, 15))

        button_frame = customtkinter.CTkFrame(card, fg_color="transparent")
        button_frame.grid(row=0, column=2, rowspan=3, padx=15, pady=15, sticky="ns")

        show_btn = AnimatedButton(
            button_frame,
            text="🗺️",
            width=40,
            height=30,
            command=lambda: self.show_on_map(location),
            fg_color=COLORS['accent'],
            corner_radius=10,
            font=customtkinter.CTkFont(size=12)
        )
        show_btn.pack(pady=2)

        # Medya butonu ekle
        if location.get("media_paths") and len(location["media_paths"]) > 0:
            media_btn = AnimatedButton(
                button_frame,
                text=f"📷 {len(location['media_paths'])}",
                width=40,
                height=30,
                command=lambda: self.show_location_media(location),
                fg_color='#8B5CF6',  # Mor renk
                corner_radius=10,
                font=customtkinter.CTkFont(size=10)
            )
            media_btn.pack(pady=2)

        edit_btn = AnimatedButton(
            button_frame,
            text="✏️",
            width=40,
            height=30,
            command=lambda: self.edit_location(location, list_type, index),
            fg_color=COLORS['warning'],
            corner_radius=10,
            font=customtkinter.CTkFont(size=12)
        )
        edit_btn.pack(pady=2)

        delete_btn = AnimatedButton(
            button_frame,
            text="🗑️",
            width=40,
            height=30,
            command=lambda: self.delete_location(location, list_type, index),
            fg_color=COLORS['danger'],
            corner_radius=10,
            font=customtkinter.CTkFont(size=12)
        )
        delete_btn.pack(pady=2)

        if list_type == "to_visit":
            move_btn = AnimatedButton(
                button_frame,
                text="✅",
                width=40,
                height=30,
                command=lambda: self.move_to_visited(location, index),
                fg_color=COLORS['success'],
                corner_radius=10,
                font=customtkinter.CTkFont(size=12)
            )
            move_btn.pack(pady=2)

    def show_location_media(self, location):
        media_paths = location.get("media_paths", [])
        if not media_paths:
            messagebox.showinfo("ℹ️ Bilgi", "Bu lokasyon için medya dosyası yok.")
            return

        existing_files = [path for path in media_paths if os.path.exists(path)]

        if not existing_files:
            messagebox.showwarning("⚠️ Uyarı", "Medya dosyaları bulunamadı.")
            return

        self.parent.show_media_preview(existing_files)

    def show_on_map(self, location):
        self.parent.map_widget.set_position(location["lat"], location["lon"])
        self.parent.map_widget.set_zoom(12)
        self.parent.lift()
        self.parent.focus()

    def edit_location(self, location, list_type, index):
        dialog = customtkinter.CTkToplevel(self)
        dialog.title("✏️ Düzenle")
        dialog.geometry("400x450")
        dialog.configure(fg_color=COLORS['surface'])
        dialog.grab_set()
        dialog.attributes("-topmost", True)

        main_frame = GradientFrame(dialog, corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        title_label = customtkinter.CTkLabel(
            main_frame,
            text="✏️ Yer Bilgilerini Düzenle",
            font=customtkinter.CTkFont(size=18, weight="bold"),
            text_color=COLORS['text']
        )
        title_label.pack(pady=(20, 15))

        name_label = customtkinter.CTkLabel(
            main_frame,
            text="📍 Yer Adı:",
            font=customtkinter.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text']
        )
        name_label.pack(pady=(10, 5))

        name_entry = customtkinter.CTkEntry(
            main_frame,
            font=customtkinter.CTkFont(size=14),
            height=35
        )
        name_entry.pack(fill="x", padx=20, pady=5)
        name_entry.insert(0, location["name"])

        note_label = customtkinter.CTkLabel(
            main_frame,
            text="📝 Notlar:",
            font=customtkinter.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text']
        )
        note_label.pack(pady=(10, 5))

        note_entry = customtkinter.CTkTextbox(
            main_frame,
            height=80,
            font=customtkinter.CTkFont(size=12)
        )
        note_entry.pack(fill="x", padx=20, pady=5)
        note_entry.insert("1.0", location.get("note", ""))

        button_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=20)
        button_frame.grid_columnconfigure((0, 1), weight=1)

        def save_changes():
            new_name = name_entry.get().strip()
            new_note = note_entry.get("1.0", tkinter.END).strip()

            if not new_name:
                messagebox.showerror("❌ Hata", "Yer adı boş olamaz.", parent=dialog)
                return

            location["name"] = new_name
            location["note"] = new_note

            if location.get("marker"):
                location["marker"].delete()
                icon = "📍" if list_type == "to_visit" else "✅"
                color = "orange" if list_type == "to_visit" else "green"
                new_marker = self.parent.map_widget.set_marker(
                    location["lat"],
                    location["lon"],
                    text=f"{icon} {new_name}",
                    marker_color_circle=color,
                    marker_color_outside=color
                )
                location["marker"] = new_marker

            self.parent.save_data()
            self.refresh_lists()
            messagebox.showinfo("✅ Başarılı!", f"'{new_name}' bilgileri güncellendi!", parent=dialog)
            dialog.destroy()

        save_button = AnimatedButton(
            button_frame,
            text="💾 Kaydet",
            command=save_changes,
            fg_color=COLORS['success'],
            height=40,
            corner_radius=20
        )
        save_button.grid(row=0, column=0, padx=(20, 10), sticky="ew")

        cancel_button = AnimatedButton(
            button_frame,
            text="❌ İptal",
            command=dialog.destroy,
            fg_color=COLORS['danger'],
            height=40,
            corner_radius=20
        )
        cancel_button.grid(row=0, column=1, padx=(10, 20), sticky="ew")

    def delete_location(self, location, list_type, index):
        result = messagebox.askyesno(
            "⚠️ Onay",
            f"'{location['name']}' konumunu silmek istediğinize emin misiniz?",
            parent=self
        )
        if result:
            if location.get("marker"):
                location["marker"].delete()

            if list_type == "to_visit":
                self.parent.to_visit_markers.pop(index)
            else:
                self.parent.visited_markers.pop(index)

            self.parent.save_data()
            self.parent.update_stats()
            self.refresh_lists()
            messagebox.showinfo("🗑️ Silindi", f"'{location['name']}' silindi!", parent=self)

    def move_to_visited(self, location, index):
        result = messagebox.askyesno(
            "✅ Onay",
            f"'{location['name']}' konumunu gezdiğim yerlere taşımak istediğinize emin misiniz?",
            parent=self
        )
        if result:
            if location.get("marker"):
                location["marker"].delete()

            self.parent.to_visit_markers.pop(index)

            new_marker = self.parent.map_widget.set_marker(
                location["lat"],
                location["lon"],
                text=f"✅ {location['name']}",
                marker_color_circle="green",
                marker_color_outside="green"
            )
            location["marker"] = new_marker
            self.parent.visited_markers.append(location)

            self.parent.save_data()
            self.parent.update_stats()
            self.refresh_lists()
            messagebox.showinfo("✅ Taşındı", f"'{location['name']}' gezdiğim yerlere taşındı!", parent=self)


if __name__ == "__main__":
    app = LoginWindow()
    app.mainloop()
