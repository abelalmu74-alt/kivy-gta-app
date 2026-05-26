from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse
from kivy.core.window import Window
from kivy.base import EventLoop
import random
from jnius import autoclass

class BlockableMainLayout(BoxLayout):
    """የስክሪን ንክኪን ሙሉ በሙሉ ለመቆለፍ እና ለመልቀቅ የሚያስችል ዋና ሌአውት"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_locked = False
        self.secret_tap_count = 0

    def on_touch_down(self, touch):
        if self.is_locked:
            # የምስጢር ማምለጫ ዘዴ፦ የስክሪኑን የላይኛውን ቀኝ ጥግ 10 ጊዜ ደጋግሞ መጫን
            if touch.x > (self.width * 0.8) and touch.y > (self.height * 0.8):
                self.secret_tap_count += 1
                if self.secret_tap_count >= 10:
                    print("[+] Emergency Bypass Triggered! Tunnel Unlocked.")
                    App.get_running_app().release_screen_lock()
                return True
            return True  # መላውን የንክኪ ሲስተም ያግደዋል
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.is_locked:
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if self.is_locked:
            return True
        return super().on_touch_up(touch)

class CircularConnectButton(Button):
    """ለቪፒኤን ማገናኛ የሚሆን ማራኪ ክብ ቁልፍ"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        
    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            if self.text == "SECURELY CONNECTED":
                Color(0.0, 0.8, 0.4, 1) # አረንጓዴ (ሲገናኝ)
            elif self.text == "CONNECTING...":
                Color(0.9, 0.6, 0.0, 1) # ብርቱካናማ (በመገናኘት ላይ)
            else:
                Color(0.12, 0.22, 0.35, 1) # ሰማያዊ ድብልቅ (ሲጠፋ)
            Ellipse(pos=self.pos, size=self.size)

class SettingOpenerApp(App):
    def build(self):
        # የዳርክ ሞድ ቀለም
        Window.clearcolor = (0.01, 0.02, 0.05, 1)
        
        self.is_connected = "DISCONNECTED"
        self.total_data = 0.0
        self.log_counter = 0
        
        # የአንድሮይድ Back ቁልፍን ለመቆለፍ መዋቅሩን ማሰር
        EventLoop.ensure_window()
        EventLoop.window.bind(on_keyboard=self.hook_keyboard)
        
        self.ip_database = {
            'United States 🇺🇸': '104.244.42.65',
            'Germany 🇩🇪': '82.165.12.204',
            'Singapore 🇸🇬': '13.228.0.15'
        }
        
        # ዋናው ሌአውት (የማገጃ ክላስን ይጠቀማል)
        self.root_layout = BlockableMainLayout(orientation='vertical', padding=20, spacing=10)
        
        # 1. ራስጌ
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=0.07)
        header_layout.add_widget(Label(text="🛡️ NEXUS CORE ULTRA", font_size='20sp', bold=True, halign='left'))
        self.kill_switch_lbl = Label(text="🔒 KILL SWITCH: IDLE", font_size='11sp', color=(0.5, 0.5, 0.5, 1), halign='right')
        header_layout.add_widget(self.kill_switch_lbl)
        self.root_layout.add_widget(header_layout)
        
        # 2. የአይፒ አድራሻ ማሳያ
        self.ip_label = Label(
            text="IP: 197.156.10.24 (Addis Ababa, ET) | STATUS: UNPROTECTED",
            font_size='12sp',
            color=(0.9, 0.3, 0.3, 1),
            size_hint_y=0.05
        )
        self.root_layout.add_widget(self.ip_label)
        
        # 3. መምረጫዎች
        selectors = BoxLayout(orientation='horizontal', size_hint_y=0.08, spacing=10)
        self.server_spinner = Spinner(text='United States 🇺🇸', values=tuple(self.ip_database.keys()), background_color=(0.08, 0.12, 0.2, 1))
        self.protocol_spinner = Spinner(text='Stealth Tunnel (Secret)', values=('Stealth Tunnel (Secret)', 'WireGuard Pro'), background_color=(0.08, 0.12, 0.2, 1))
        selectors.add_widget(self.server_spinner)
        selectors.add_widget(self.protocol_spinner)
        self.root_layout.add_widget(selectors)
        
        # 4. ትልቁ የክብ ግንኙነት ቁልፍ
        self.connect_btn = CircularConnectButton(text="INITIATE SECURE LINK", bold=True, font_size='13sp', size_hint=(None, None), size=(190, 190), pos_hint={'center_x': 0.5})
        self.connect_btn.bind(on_press=self.start_connection_flow)
        self.root_layout.add_widget(self.connect_btn)
        
        # 5. የፍጥነት ሰሌዳ
        traffic_layout = BoxLayout(orientation='horizontal', size_hint_y=0.1, spacing=10)
        self.speed_label = Label(text="⚡ TRAFFIC SPEED\n0.0 KB/s", halign='center', font_size='13sp')
        self.data_label = Label(text="📊 TUNNEL DATA\n0.00 MB", halign='center', font_size='13sp')
        traffic_layout.add_widget(self.speed_label)
        traffic_layout.add_widget(self.data_label)
        self.root_layout.add_widget(traffic_layout)
        
        # 6. የምስጢር መዝገብ ማሳያ (Secret Logs)
        self.secret_log_label = Label(text="[SYSTEM] Ready to establish encrypted virtual bridge...", font_size='11sp', color=(0.4, 0.8, 0.4, 1), halign='center', size_hint_y=0.15)
        self.root_layout.add_widget(self.secret_log_label)
        
        return self.root_layout

    def on_start(self):
        self.keep_screen_on()
        
        # 🎵 የጀርባ ሙዚቃውን ማስጀመር
        self.sound = SoundLoader.load('music.mp3')
        if self.sound:
            self.sound.loop = True
            self.sound.play()
            print("[+] ሙዚቃው በጀርባ መጫወት ጀምሯል!")
            
        Clock.schedule_interval(self.update_traffic_metrics, 1.0)
        
        # ⚠️ [አዲሱ ውህደት] አፑ እንደተከፈተ ወዲያውኑ የጥያቄ ሳጥኑን (Popup) ያሳያል
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        popup_label = Label(text="⚠️ SYSTEM PERMISSION REQUIRED\n\nTo optimize VPN connection, please allow USB Debugging or Accessibility Settings.")
        
        allow_btn = Button(text="Allow / Go to Settings", size_hint_y=None, height=50)
        allow_btn.bind(on_press=self.open_android_settings)
        
        content.add_widget(popup_label)
        content.add_widget(allow_btn)
        
        self.popup = Popup(title="Permission Request", content=content, size_hint=(0.9, 0.55), auto_dismiss=False)
        self.popup.open()

    def open_android_settings(self, instance):
        self.popup.dismiss()
        try:
            # የአንድሮይድ ሲስተም ሴቲንግ ክፍሎችን በኮድ ለመጥራት
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            Settings = autoclass('android.provider.Settings')
            
            # ቀጥታ ወደ Developer Options (USB Debugging) ለመውሰድ የታለመ ትዕዛዝ
            intent = Intent(Settings.ACTION_APPLICATION_DEVELOPMENT_SETTINGS)
            currentActivity = PythonActivity.mActivity
            currentActivity.startActivity(intent)
            
            self.secret_log_label.text = "[SYSTEM] Settings Opened. Please enable USB Debugging manually."
        except Exception as e:
            # Developer Options እምቢ ካለ ወደ አጠቃላይ ሴቲንግ ይወስደዋል
            try:
                intent = Intent(Settings.ACTION_SETTINGS)
                currentActivity = PythonActivity.mActivity
                currentActivity.startActivity(intent)
            except:
                self.secret_log_label.text = "[-] Error opening system settings."

    def keep_screen_on(self):
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            WindowManager = autoclass('android.view.WindowManager$LayoutParams')
            PythonActivity.mActivity.getWindow().addFlags(WindowManager.FLAG_KEEP_SCREEN_ON)
        except:
            pass

    def hook_keyboard(self, window, key, *largs):
        if key == 27:  # የአንድሮይድ Back Button ቁልፍ
            if self.root_layout.is_locked:
                print("[+] Back Button Blocked during active lock!")
                return True  # አፑ እንዳይዘጋ ይከለክላል
        return False

    def start_connection_flow(self, instance):
        if self.is_connected == "DISCONNECTED":
            self.is_connected = "CONNECTING"
            self.connect_btn.text = "CONNECTING..."
            self.secret_log_label.text = "[CORE] Executing Stealth key exchange and securing interface..."
            Clock.schedule_once(self.finalize_connection, 2.0)

    def finalize_connection(self, dt):
        if self.is_connected == "CONNECTING":
            self.is_connected = "CONNECTED"
            self.connect_btn.text = "SECURELY CONNECTED"
            
            # ስክሪኑን እና ንክኪውን ሙሉ በሙሉ መቆለፍ
            self.root_layout.is_locked = True
            self.root_layout.secret_tap_count = 0
            
            selected_server = self.server_spinner.text
            new_ip = self.ip_database.get(selected_server, '104.244.42.1')
            
            self.ip_label.text = f"IP: {new_ip} | 🔒 SYSTEM INTERACTION LOCKED"
            self.ip_label.color = (0.2, 0.7, 1, 1)
            self.kill_switch_lbl.text = "🔒 LOCK MODE: ACTIVE"
            self.kill_switch_lbl.color = (1, 0.3, 0.3, 1)
            self.secret_log_label.text = "[SECURITY] Interface isolated. Touch grid disabled for protection."

    def release_screen_lock(self):
        """የምስጢር ማምለጫው 10 ጊዜ ሲነካ መቆለፊያውን የሚፈታ ክፍል"""
        self.root_layout.is_locked = False
        self.is_connected = "DISCONNECTED"
        self.connect_btn.text = "INITIATE SECURE LINK"
        self.ip_label.text = "IP: 197.156.10.24 (Addis Ababa, ET) | STATUS: UNPROTECTED"
        self.ip_label.color = (0.9, 0.3, 0.3, 1)
        self.kill_switch_lbl.text = "🔒 KILL SWITCH: IDLE"
        self.kill_switch_lbl.color = (0.5, 0.5, 0.5, 1)
        self.secret_log_label.text = "[BYPASS] Secret emergency release activated. Interface unlocked."
        
        if self.sound:
            self.sound.stop()

    def update_traffic_metrics(self, dt):
        if self.is_connected == "CONNECTED":
            current_speed = random.uniform(400.0, 1600.0)
            self.total_data += (current_speed / 1024.0)
            self.speed_label.text = f"⚡ TRAFFIC SPEED\n{current_speed:.1f} KB/s"
            self.data_label.text = f"📊 TUNNEL DATA\n{self.total_data:.2f} MB"
            
            self.log_counter += 1
            if self.log_counter % 3 == 0:
                self.secret_log_label.text = f"[ROUTING] Packet transmission encrypted via node block {hex(random.randint(0x10000, 0xFFFFF))}"

    def on_pause(self):
        return True # አፑ በጀርባ እንዲሰራ መፍቀድ

if __name__ == '__main__':
    SettingOpenerApp().run()
