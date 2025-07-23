import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
from datetime import datetime


class ModernGorevYoneticisiGUI:
    def __init__(self):
        self.dosya_adi = "gorevler.json"
        self.gorevler = []
        self.root = tk.Tk()
        self.root.title("✨ Görev Yöneticisi")
        self.root.geometry("1000x700")
        self.root.minsize(900, 600)
        self.setup_modern_theme()
        self.create_modern_widgets()
        self.gorevleri_yukle()
        self.gorevleri_guncelle()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.start_animations()

    def setup_modern_theme(self):
        self.root.configure(bg='#1a1a2e')
        self.colors = {
            'primary': '#6c5ce7',  # Mor
            'secondary': '#fd79a8',  # Pembe
            'success': '#00b894',  # Yeşil
            'warning': '#fdcb6e',  # Sarı
            'danger': '#e17055',  # Turuncu-kırmızı
            'info': '#74b9ff',  # Mavi
            'dark': '#1a1a2e',  # Koyu mavi
            'light': '#ffffff',  # Beyaz
            'card': '#16213e',  # Kart arka planı
            'text': '#dfe6e9',  # Metin rengi
            'border': '#2d3748',  # Kenar rengi
            'hover': '#a29bfe'  # Hover efekti
        }
        self.setup_custom_styles()

    def setup_custom_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Card.TFrame',
                        background=self.colors['card'],
                        relief='flat',
                        borderwidth=1)
        style.configure('ModernTitle.TLabel',
                        font=('Segoe UI', 24, 'bold'),
                        background=self.colors['dark'],
                        foreground=self.colors['primary'])
        style.configure('Subtitle.TLabel',
                        font=('Segoe UI', 12),
                        background=self.colors['card'],
                        foreground=self.colors['text'])
        style.configure('Modern.TButton',
                        font=('Segoe UI', 10, 'bold'),
                        relief='flat',
                        padding=(15, 8))
        style.configure('Primary.TButton',
                        font=('Segoe UI', 10, 'bold'),
                        relief='flat',
                        padding=(15, 8),
                        background=self.colors['primary'])
        style.configure('Success.TButton',
                        font=('Segoe UI', 10, 'bold'),
                        relief='flat',
                        padding=(12, 6),
                        background=self.colors['success'])
        style.configure('Danger.TButton',
                        font=('Segoe UI', 10, 'bold'),
                        relief='flat',
                        padding=(12, 6),
                        background=self.colors['danger'])
        style.configure('Modern.TEntry',
                        font=('Segoe UI', 11),
                        fieldbackground=self.colors['light'],
                        relief='flat',
                        borderwidth=2)
        style.configure('Modern.Treeview',
                        background=self.colors['light'],
                        foreground='#2d3748',
                        font=('Segoe UI', 10),
                        rowheight=35,
                        fieldbackground=self.colors['light'])
        style.configure('Modern.Treeview.Heading',
                        font=('Segoe UI', 11, 'bold'),
                        background=self.colors['primary'],
                        foreground='white',
                        relief='flat')
        style.configure('Modern.Horizontal.TProgressbar',
                        background=self.colors['success'],
                        troughcolor=self.colors['border'],
                        borderwidth=0,
                        relief='flat')

    def create_modern_widgets(self):
        main_container = tk.Frame(self.root, bg=self.colors['dark'])
        main_container.pack(fill='both', expand=True, padx=20, pady=0)
        self.create_header(main_container)
        content_frame = tk.Frame(main_container, bg=self.colors['dark'])
        content_frame.pack(fill='both', expand=True, pady=(20, 0))
        self.create_modern_task_list(content_frame)
        self.create_modern_controls(content_frame)
        self.create_modern_statistics(main_container)

    def create_header(self, parent):
        header_frame = tk.Frame(parent, bg=self.colors['dark'], height=80)
        header_frame.pack(fill='x', pady=(0, 10))
        header_frame.pack_propagate(False)

        title_frame = tk.Frame(header_frame, bg=self.colors['dark'])
        title_frame.pack(expand=True)

        title_text = "✨ Modern Görev Yönetici"
        self.title_label = tk.Label(title_frame, text=title_text,
                                    font=('Segoe UI', 28, 'bold'),
                                    bg=self.colors['dark'],
                                    fg=self.colors['primary'])
        self.title_label.pack(pady=20)

        subtitle = "Görevlerinizi modern ve şık bir arayüzle yönetin"
        tk.Label(header_frame, text=subtitle,
                 font=('Segoe UI', 12),
                 bg=self.colors['dark'],
                 fg=self.colors['text']).pack()

    def create_modern_task_list(self, parent):
        left_panel = tk.Frame(parent, bg=self.colors['dark'])
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 15))
        card_frame = tk.Frame(left_panel, bg=self.colors['card'],
                              relief='solid', bd=1)
        card_frame.pack(fill='both', expand=True, padx=5, pady=5)
        card_header = tk.Frame(card_frame, bg=self.colors['primary'], height=50)
        card_header.pack(fill='x')
        card_header.pack_propagate(False)

        tk.Label(card_header, text="📋 Görev Listesi",
                 font=('Segoe UI', 14, 'bold'),
                 bg=self.colors['primary'],
                 fg='white').pack(pady=15)

        tree_container = tk.Frame(card_frame, bg=self.colors['card'])
        tree_container.pack(fill='both', expand=True, padx=15, pady=15)
        columns = ('🎯', 'Görev', '📅')
        self.tree = ttk.Treeview(tree_container, columns=columns,
                                 show='headings', height=18,
                                 style='Modern.Treeview')

        self.tree.heading('🎯', text='Durum')
        self.tree.heading('Görev', text='Görev Açıklaması')
        self.tree.heading('📅', text='Oluşturma Tarihi')
        self.tree.column('🎯', width=80, anchor='center')
        self.tree.column('Görev', width=350)
        self.tree.column('📅', width=150, anchor='center')
        scrollbar = ttk.Scrollbar(tree_container, orient="vertical",
                                  command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        self.tree.bind('<Double-1>', self.on_task_double_click)
        self.tree.bind('<Button-3>', self.on_task_right_click)

    def create_modern_controls(self, parent):
        right_panel = tk.Frame(parent, bg=self.colors['dark'], width=300)
        right_panel.pack(side='right', fill='y')
        right_panel.pack_propagate(False)
        self.create_add_task_card(right_panel)
        tk.Frame(right_panel, bg=self.colors['dark'], height=20).pack()
        self.create_action_buttons_card(right_panel)
        tk.Frame(right_panel, bg=self.colors['dark'], height=20).pack()
        self.create_search_card(right_panel)

    def create_add_task_card(self, parent):
        card = tk.Frame(parent, bg=self.colors['card'], relief='solid', bd=1)
        card.pack(fill='x', padx=5)
        header = tk.Frame(card, bg=self.colors['secondary'], height=40)
        header.pack(fill='x')
        header.pack_propagate(False)

        tk.Label(header, text="➕ Yeni Görev Ekle",
                 font=('Segoe UI', 12, 'bold'),
                 bg=self.colors['secondary'],
                 fg='white').pack(pady=10)

        content = tk.Frame(card, bg=self.colors['card'])
        content.pack(fill='x', padx=20, pady=20)
        tk.Label(content, text="Görev açıklaması:",
                 font=('Segoe UI', 10),
                 bg=self.colors['card'],
                 fg=self.colors['text']).pack(anchor='w', pady=(0, 5))

        self.task_entry = ttk.Entry(content, style='Modern.TEntry', width=30)
        self.task_entry.pack(fill='x', pady=(0, 15))
        self.task_entry.bind('<Return>', lambda e: self.gorev_ekle())
        add_btn = tk.Button(content, text="🚀 Görevi Ekle",
                            font=('Segoe UI', 11, 'bold'),
                            bg=self.colors['primary'],
                            fg='white',
                            relief='flat',
                            cursor='hand2',
                            command=self.gorev_ekle)
        add_btn.pack(fill='x', pady=5)
        add_btn.bind('<Enter>', lambda e: add_btn.configure(bg=self.colors['hover']))
        add_btn.bind('<Leave>', lambda e: add_btn.configure(bg=self.colors['primary']))

    def create_action_buttons_card(self, parent):
        card = tk.Frame(parent, bg=self.colors['card'], relief='solid', bd=1)
        card.pack(fill='x', padx=5)

        header = tk.Frame(card, bg=self.colors['info'], height=40)
        header.pack(fill='x')
        header.pack_propagate(False)
        tk.Label(header, text="🛠️ Görev İşlemleri",
                 font=('Segoe UI', 12, 'bold'),
                 bg=self.colors['info'],
                 fg='white').pack(pady=10)
        content = tk.Frame(card, bg=self.colors['card'])
        content.pack(fill='x', padx=20, pady=20)

        buttons = [
            ("✏️", "Düzenle", self.gorev_duzenle, self.colors['warning']),
            ("✅", "Tamamla/Geri Al", self.gorev_durumu_degistir, self.colors['success']),
            ("🗑️", "Sil", self.gorev_sil, self.colors['danger']),
            ("🔄", "Yenile", self.gorevleri_guncelle, self.colors['info']),
            ("📊", "İstatistikler", self.istatistik_goster, self.colors['secondary']),
            ("💾", "Kaydet", self.gorevleri_kaydet, self.colors['primary'])
        ]

        for icon, text, command, color in buttons:
            btn_frame = tk.Frame(content, bg=self.colors['card'])
            btn_frame.pack(fill='x', pady=2)

            btn = tk.Button(btn_frame, text=f"{icon} {text}",
                            font=('Segoe UI', 10, 'bold'),
                            bg=color,
                            fg='white',
                            relief='flat',
                            cursor='hand2',
                            command=command)
            btn.pack(fill='x', pady=1)
            original_color = color
            btn.bind('<Enter>', lambda e, b=btn, c=color: b.configure(bg=self.lighten_color(c)))
            btn.bind('<Leave>', lambda e, b=btn, c=original_color: b.configure(bg=c))

    def create_search_card(self, parent):
        card = tk.Frame(parent, bg=self.colors['card'], relief='solid', bd=1)
        card.pack(fill='x', padx=5)

        header = tk.Frame(card, bg=self.colors['success'], height=40)
        header.pack(fill='x')
        header.pack_propagate(False)

        tk.Label(header, text="🔍 Görev Ara",
                 font=('Segoe UI', 12, 'bold'),
                 bg=self.colors['success'],
                 fg='white').pack(pady=10)
        content = tk.Frame(card, bg=self.colors['card'])
        content.pack(fill='x', padx=20, pady=20)
        tk.Label(content, text="Arama terimi:",
                 font=('Segoe UI', 10),
                 bg=self.colors['card'],
                 fg=self.colors['text']).pack(anchor='w', pady=(0, 5))

        self.search_entry = ttk.Entry(content, style='Modern.TEntry', width=30)
        self.search_entry.pack(fill='x')
        self.search_entry.bind('<KeyRelease>', self.gorev_ara)

    def create_modern_statistics(self, parent):
        stats_container = tk.Frame(parent, bg=self.colors['dark'], height=120)
        stats_container.pack(fill='x', pady=(20, 0))
        stats_container.pack_propagate(False)
        cards_frame = tk.Frame(stats_container, bg=self.colors['dark'])
        cards_frame.pack(fill='both', expand=True, pady=10)
        self.create_stat_cards(cards_frame)
        progress_frame = tk.Frame(stats_container, bg=self.colors['dark'])
        progress_frame.pack(fill='x', pady=(10, 0))
        tk.Label(progress_frame, text="📊 Tamamlanma İlerlemesi",
                 font=('Segoe UI', 11, 'bold'),
                 bg=self.colors['dark'],
                 fg=self.colors['text']).pack()
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame,
                                            variable=self.progress_var,
                                            maximum=100,
                                            length=400,
                                            style='Modern.Horizontal.TProgressbar')
        self.progress_bar.pack(pady=10)
        self.progress_label = tk.Label(progress_frame, text="0%",
                                       font=('Segoe UI', 10, 'bold'),
                                       bg=self.colors['dark'],
                                       fg=self.colors['success'])
        self.progress_label.pack()

    def create_stat_cards(self, parent):
        stats = [
            ("Toplam", "📈", 'info'),
            ("Tamamlanan", "✅", 'success'),
            ("Bekleyen", "⏳", 'warning'),
            ("Oran", "📊", 'secondary')
        ]

        self.stat_labels = {}
        for i, (title, icon, color_key) in enumerate(stats):
            card = tk.Frame(parent, bg=self.colors[color_key],
                            relief='solid', bd=1, width=200, height=120)
            card.pack(side='left', fill='y', padx=5, expand=True)
            card.pack_propagate(False)
            tk.Label(card, text=icon, font=('Segoe UI', 20),
                     bg=self.colors[color_key], fg='white').pack(pady=(0, 0))
            tk.Label(card, text=title, font=('Segoe UI', 10, 'bold'),
                     bg=self.colors[color_key], fg='white').pack()
            value_label = tk.Label(card, text="0",
                                   font=('Segoe UI', 16, 'bold'),
                                   bg=self.colors[color_key], fg='white')
            value_label.pack(pady=(5, 10))

            self.stat_labels[title.lower()] = value_label

    def lighten_color(self, color):
        color_map = {
            self.colors['primary']: self.colors['hover'],
            self.colors['success']: '#55efc4',
            self.colors['danger']: '#fab1a0',
            self.colors['warning']: '#ffeaa7',
            self.colors['info']: '#81ecec',
            self.colors['secondary']: '#fd79a8'
        }
        return color_map.get(color, color)

    def start_animations(self):
        self.animate_title()

    def animate_title(self):
        colors = [self.colors['primary'], self.colors['secondary'],
                  self.colors['success'], self.colors['info']]

        def change_color(index=0):
            if hasattr(self, 'title_label'):
                self.title_label.configure(fg=colors[index % len(colors)])
                self.root.after(3000, lambda: change_color(index + 1))

        change_color()

    def gorevleri_yukle(self):
        try:
            if os.path.exists(self.dosya_adi):
                with open(self.dosya_adi, 'r', encoding='utf-8') as dosya:
                    self.gorevler = json.load(dosya)
                self.show_status_message(f"✓ {len(self.gorevler)} görev yüklendi")
            else:
                self.gorevler = []
                self.show_status_message("● Yeni görev listesi oluşturuldu")
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya okuma hatası: {str(e)}")
            self.gorevler = []

    def gorevleri_kaydet(self):
        try:
            with open(self.dosya_adi, 'w', encoding='utf-8') as dosya:
                json.dump(self.gorevler, dosya, ensure_ascii=False, indent=2)
            self.show_status_message("✓ Görevler kaydedildi")
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya kaydetme hatası: {str(e)}")

    def gorevleri_guncelle(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for i, gorev in enumerate(self.gorevler):
            durum = "✅" if gorev.get("durum") == "tamamlandi" else "⏳"
            tarih = gorev.get('olusturma_tarihi', '').split()[0]
            item = self.tree.insert('', 'end', values=(durum, gorev['metin'], tarih))
            if gorev.get("durum") == "tamamlandi":
                self.tree.item(item, tags=('completed',))
        self.tree.tag_configure('completed', background='#d5f4e6',
                                foreground='#00695c')
        self.istatistikleri_guncelle()

    def istatistikleri_guncelle(self):
        toplam = len(self.gorevler)
        tamamlanan = sum(1 for g in self.gorevler if g.get("durum") == "tamamlandi")
        bekleyen = toplam - tamamlanan
        oran = (tamamlanan / toplam * 100) if toplam > 0 else 0

        self.stat_labels["toplam"].config(text=str(toplam))
        self.stat_labels["tamamlanan"].config(text=str(tamamlanan))
        self.stat_labels["bekleyen"].config(text=str(bekleyen))
        self.stat_labels["oran"].config(text=f"{oran:.1f}%")
        self.progress_var.set(oran)
        self.progress_label.config(text=f"{oran:.1f}%")

    def gorev_ekle(self):
        gorev_metni = self.task_entry.get().strip()

        if not gorev_metni:
            messagebox.showwarning("Uyarı", "Boş görev eklenemez!")
            return

        yeni_gorev = {
            "id": len(self.gorevler) + 1,
            "metin": gorev_metni,
            "olusturma_tarihi": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "durum": "bekliyor"
        }

        self.gorevler.append(yeni_gorev)
        self.task_entry.delete(0, tk.END)
        self.gorevleri_guncelle()
        self.gorevleri_kaydet()
        self.show_status_message(f"✓ Görev eklendi: {gorev_metni}")

    def gorev_duzenle(self):
        secili = self.tree.selection()
        if not secili:
            messagebox.showwarning("Uyarı", "Lütfen düzenlenecek görevi seçin!")
            return

        index = self.tree.index(secili[0])
        gorev = self.gorevler[index]

        yeni_metin = simpledialog.askstring("Görev Düzenle",
                                            f"Görev metnini düzenleyin:",
                                            initialvalue=gorev['metin'])

        if yeni_metin and yeni_metin.strip():
            gorev['metin'] = yeni_metin.strip()
            gorev['guncelleme_tarihi'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.gorevleri_guncelle()
            self.gorevleri_kaydet()
            self.show_status_message(f"✓ Görev güncellendi: {yeni_metin}")

    def gorev_sil(self):
        secili = self.tree.selection()
        if not secili:
            messagebox.showwarning("Uyarı", "Lütfen silinecek görevi seçin!")
            return

        index = self.tree.index(secili[0])
        gorev = self.gorevler[index]

        if messagebox.askyesno("Görev Sil", f"'{gorev['metin']}' görevi silinsin mi?"):
            self.gorevler.pop(index)

            for i, g in enumerate(self.gorevler):
                g["id"] = i + 1

            self.gorevleri_guncelle()
            self.gorevleri_kaydet()
            self.show_status_message(f"✓ Görev silindi: {gorev['metin']}")

    def gorev_durumu_degistir(self):
        secili = self.tree.selection()
        if not secili:
            messagebox.showwarning("Uyarı", "Lütfen görev seçin!")
            return

        index = self.tree.index(secili[0])
        gorev = self.gorevler[index]

        if gorev.get("durum") == "bekliyor":
            gorev["durum"] = "tamamlandi"
            gorev["tamamlanma_tarihi"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            mesaj = f"✅ Görev tamamlandı: {gorev['metin']}"
        else:
            gorev["durum"] = "bekliyor"
            if "tamamlanma_tarihi" in gorev:
                del gorev["tamamlanma_tarihi"]
            mesaj = f"⏳ Görev bekliyor: {gorev['metin']}"

        self.gorevleri_guncelle()
        self.gorevleri_kaydet()
        self.show_status_message(mesaj)

    def gorev_ara(self, event=None):
        arama_terimi = self.search_entry.get().lower()

        for item in self.tree.get_children():
            self.tree.delete(item)

        for gorev in self.gorevler:
            if arama_terimi in gorev['metin'].lower():
                durum = "✅" if gorev.get("durum") == "tamamlandi" else "⏳"
                tarih = gorev.get('olusturma_tarihi', '').split()[0]

                item = self.tree.insert('', 'end', values=(durum, gorev['metin'], tarih))

                if gorev.get("durum") == "tamamlandi":
                    self.tree.item(item, tags=('completed',))

    def istatistik_goster(self):
        if not self.gorevler:
            messagebox.showinfo("İstatistik", "Henüz hiç görev eklenmemiş.")
            return

        toplam = len(self.gorevler)
        tamamlanan = sum(1 for g in self.gorevler if g.get("durum") == "tamamlandi")
        bekleyen = toplam - tamamlanan
        oran = (tamamlanan / toplam * 100) if toplam > 0 else 0
        son_gorevler = sorted(self.gorevler, key=lambda x: x.get('olusturma_tarihi', ''), reverse=True)[:5]
        son_liste = "\n".join([f"• {g['metin']}" for g in son_gorevler])
        mesaj = f"""🎯 DETAYLI İSTATİSTİKLER

📊 Genel Durum:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 Toplam Görev: {toplam}
✅ Tamamlanan: {tamamlanan}
⏳ Bekleyen: {bekleyen}
📊 Başarı Oranı: %{oran:.1f}

🕐 En Son Eklenen Görevler:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{son_liste}

🎉 {'Harika gidiyorsun! 🚀' if oran > 70 else 'Devam et! 💪' if oran > 30 else 'Başlangıç güzel! ⭐'}
"""

        messagebox.showinfo("📊 Detaylı İstatistikler", mesaj)

    def on_task_double_click(self, event):
        self.gorev_duzenle()

    def on_task_right_click(self, event):
        """Görev sağ tıklandığında menü göster"""
        # Gelecekte context menu eklenebilir
        pass

    def show_status_message(self, mesaj):
        original_title = "✨ Modern Görev Yönetici"
        self.root.title(f"✨ {mesaj}")
        self.root.after(3000, lambda: self.root.title(original_title))
        self.flash_status_animation()

    def flash_status_animation(self):
        original_bg = self.root.cget('bg')
        flash_color = self.colors['success']

        def flash(count=0):
            if count < 6:
                current_bg = flash_color if count % 2 == 0 else original_bg
                self.root.configure(bg=current_bg)
                self.root.after(150, lambda: flash(count + 1))
            else:
                self.root.configure(bg=original_bg)
        flash()

    def on_closing(self):
        self.gorevleri_kaydet()
        def fade_out(alpha=1.0):
            if alpha > 0:
                self.root.attributes('-alpha', alpha)
                self.root.after(50, lambda: fade_out(alpha - 0.1))
            else:
                self.root.destroy()

        try:
            fade_out()
        except:
            self.root.destroy()

    def calistir(self):

        def fade_in(alpha=0.0):
            if alpha < 1.0:
                self.root.attributes('-alpha', alpha)
                self.root.after(50, lambda: fade_in(alpha + 0.1))
            else:
                self.root.attributes('-alpha', 1.0)

        try:
            self.root.attributes('-alpha', 0.0)
            fade_in()
        except:
            pass
        self.center_window()
        self.root.mainloop()

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def create_tooltip(self, widget, text):

        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.configure(bg='black')
            label = tk.Label(tooltip, text=text, bg='black', fg='white')
            label.pack()

            x = widget.winfo_rootx() + 25
            y = widget.winfo_rooty() + 25
            tooltip.geometry(f"+{x}+{y}")

            widget.tooltip = tooltip

        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip

        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)


def main():
    try:
        app = ModernGorevYoneticisiGUI()
        app.calistir()
    except Exception as e:
        messagebox.showerror("Kritik Hata",
                             f"Uygulama başlatılamadı:\n{str(e)}\n\nLütfen tekrar deneyin.")

if __name__ == "__main__":
    main()
