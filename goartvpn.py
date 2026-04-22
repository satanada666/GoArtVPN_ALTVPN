import sys
import os
import json
import time
import socket
import threading
import subprocess
from pathlib import Path
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QSystemTrayIcon, QMenu, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QComboBox, QLineEdit,
    QTextEdit, QMessageBox
)
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QBrush, QAction, QTextCursor
from PyQt6.QtCore import Qt, QObject, pyqtSignal, QTimer

# ──────────────────────────────────────────────
#  ПУТИ
# ──────────────────────────────────────────────

if getattr(sys, 'frozen', False):
    APP_DIR = Path(sys.executable).parent
    BIN_DIR = APP_DIR / "_internal" / "bin"
else:
    APP_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
    BIN_DIR = APP_DIR / "bin"

CONFIG_FILE = APP_DIR / "config.json"
LOG_FILE    = APP_DIR / "vpn.log"
OPENCONNECT_EXE = BIN_DIR / "openconnect.exe"

# ──────────────────────────────────────────────
#  КОНФИГ
# ──────────────────────────────────────────────

DEFAULT_CONFIG = {
    "server":            "valletta-s1.goart.work",
    "port":              443,
    "user":              "KLUveAUHqQ",
    "password":          "satand@mail.ru",
    "interface":         "vpn0",
    "servercert":        "pin-sha256:NKP0RBSQJO8kBJxljfbAjr/yyKgRuy1wh76Mijdhpz0=",
    "no_dtls":           True,
    "disable_ipv6":      True,
    "reconnect_timeout": 300,
    "watchdog_interval": 10,
    "split_tunneling":   True,
    "custom_patterns":   [],
}

SERVERS = [
    ("Россия, Москва S9",             "moscow-s9"),
    ("Россия, Москва S14",            "moscow-s14"),
    ("Россия, Москва S4",             "moscow-s4"),
    ("Россия, Москва S5",             "moscow-s5"),
    ("Россия, Москва S8",             "moscow-s8"),
    ("Россия, Москва S10",            "moscow-s10"),
    ("Россия, Санкт-Петербург S1",    "saint-petersburg-s1"),
    ("Россия, Санкт-Петербург S4",    "saint-petersburg-s4"),
    ("Украина, Харьков S6",           "kharkov-s6"),
    ("Украина, Харьков S7",           "kharkov-s7"),
    ("Казахстан, Алматы S1",          "almaty-s1"),
    ("Казахстан, Алматы S2",          "almaty-s2"),
    ("Казахстан, Астана S2",          "astana-s2"),
    ("Германия, Франкфурт",           "frankfurt"),
    ("Германия, Франкфурт S2",        "frankfurt-s2"),
    ("Германия, Франкфурт S3",        "frankfurt-s3"),
    ("Германия, Франкфурт S4",        "frankfurt-s4"),
    ("Германия, Франкфурт S5",        "frankfurt-s5"),
    ("Нидерланды, Амстердам S1",      "amsterdam-s1"),
    ("Нидерланды, Амстердам S2",      "amsterdam-s2"),
    ("Нидерланды, Амстердам S3",      "amsterdam-s3"),
    ("Латвия, Рига S1",               "riga-s1"),
    ("Латвия, Рига S2",               "riga-s2"),
    ("Латвия, Рига S3",               "riga-s3"),
    ("Латвия, Рига S4",               "riga-s4"),
    ("Литва, Вильнюс S1",             "vilnius-s1"),
    ("Литва, Вильнюс S3",             "vilnius-s3"),
    ("Эстония, Таллин S1",            "tallinn-s1"),
    ("Эстония, Таллин S2",            "tallinn-s2"),
    ("Эстония, Таллин S3",            "tallinn-s3"),
    ("Финляндия, Хельсинки S2",       "helsinki-s2"),
    ("Финляндия, Хельсинки S3",       "helsinki-s3"),
    ("Швеция, Стокгольм S1",          "stockholm-s1"),
    ("Швеция, Стокгольм S2",          "stockholm-s2"),
    ("Швеция, Стокгольм S3",          "stockholm-s3"),
    ("Норвегия, Осло S1",             "oslo-s1"),
    ("Польша, Варшава S2",            "warsaw-s2"),
    ("Чехия, Прага S1",               "prague-s1"),
    ("Чехия, Прага S2",               "prague-s2"),
    ("Франция, Париж S2",             "paris-s2"),
    ("Франция, Лотербур S1",          "lauterbourg-s1"),
    ("Великобритания, Лондон S1",     "london-s1"),
    ("Великобритания, Лондон S4",     "london-s4"),
    ("Испания, Мадрид S2",            "madrid-s2"),
    ("Испания, Мадрид S3",            "madrid-s3"),
    ("Италия, Милан S1",              "milan-s1"),
    ("Бельгия, Брюссель S1",          "brussels-s1"),
    ("Бельгия, Брюссель S2",          "brussels-s2"),
    ("Болгария, София S1",            "sofia-s1"),
    ("Болгария, София S2",            "sofia-s2"),
    ("Португалия, Лиссабон S1",       "lisbon-s1"),
    ("Венгрия, Будапешт S2",          "budapesht-s2"),
    ("Хорватия, Загреб S1",           "zagreb-s1"),
    ("Ирландия, Дублин S2",           "dublin-s2"),
    ("Люксембург S1",                 "luxembourg-s1"),
    ("Швейцария, Цюрих S1",           "zurich-s1"),
    ("Кипр, Никосия S1",              "nicosia-s1"),
    ("Мальта, Валлетта S1",           "valletta-s1"),
    ("Турция, Стамбул S1",            "istanbul-s1"),
    ("Турция, Стамбул S3",            "istanbul-s3"),
    ("Грузия, Тбилиси S1",            "tbilisi-s1"),
    ("Грузия, Тбилиси S2",            "tbilisi-s2"),
    ("Армения, Ереван S1",            "yerevan-s1"),
    ("Азербайджан, Баку S1",          "baku-s1"),
    ("Беларусь, Минск S1",            "minsk-s1"),
    ("Молдова, Кишинев S3",           "kishinev-s3"),
    ("ОАЭ, Дубай S2",                 "dubai-s2"),
    ("Израиль, Тель-Авив S2",         "tel-aviv-s2"),
    ("Саудовская Аравия, Эр-Рияд S1", "riyadh-s1"),
    ("Индия, Нью Дели S1",            "new-delhi-s1"),
    ("Китай, Гонконг S1",             "hong-kong-s1"),
    ("Япония, Токио S2",              "tokyo-s2"),
    ("Сингапур S1",                   "singapore-s1"),
    ("Канада, Торонто S1",            "toronto-s1"),
    ("США, Ашберн S1",                "ashburn-s1"),
    ("США, Даллас S1",                "dallas-s1"),
    ("США, Лос-Анжелес",              "los-angeles"),
    ("США, Майами S1",                "miami-s1"),
    ("США, Нью-Йорк S1",              "new-york-s1"),
    ("США, Вашингтон S1",             "washington-s1"),
    ("Аргентина, Буэнос-Айрес S1",    "buenos-aires-s1"),
    ("Австралия, Сидней",             "sydney"),
]

DOMAIN = "goart.work"

# ──────────────────────────────────────────────
#  СТАТИЧЕСКИЕ ПОДСЕТИ ДЛЯ SPLIT TUNNELING
# ──────────────────────────────────────────────

# Telegram
TELEGRAM_SUBNETS = [
    "91.108.4.0/22", "91.108.8.0/22", "91.108.16.0/22", "91.108.56.0/22",
    "149.154.160.0/20", "91.105.192.0/23", "185.76.151.0/24",
    "91.108.20.0/22", "91.108.12.0/22",
]

# Google / YouTube (ASN 15169)
GOOGLE_SUBNETS = [
    "8.8.8.0/24", "8.8.4.0/24",
    "34.64.0.0/10", "34.128.0.0/10",
    "35.184.0.0/13", "35.192.0.0/14", "35.196.0.0/15",
    "35.198.0.0/16", "35.199.0.0/16", "35.200.0.0/13",
    "35.208.0.0/12", "35.224.0.0/12", "35.240.0.0/13",
    "64.233.160.0/19", "66.102.0.0/20", "66.249.64.0/19",
    "70.32.128.0/19", "72.14.192.0/18", "74.125.0.0/16",
    "104.132.0.0/10", "104.196.0.0/14",
    "108.177.8.0/21", "108.177.96.0/19",
    "142.250.0.0/15", "172.217.0.0/16", "172.253.0.0/16",
    "173.194.0.0/16", "209.85.128.0/17",
    "216.58.192.0/19", "216.239.32.0/19",
]

# Meta / Instagram / Facebook / WhatsApp
META_SUBNETS = [
    "31.13.24.0/21", "31.13.64.0/18", "45.64.40.0/22",
    "66.220.144.0/20", "69.63.176.0/20", "69.171.224.0/19",
    "74.119.76.0/22", "102.132.96.0/20", "103.4.96.0/22",
    "129.134.0.0/17", "157.240.0.0/17", "173.252.64.0/18",
    "179.60.192.0/22", "185.60.216.0/22", "204.15.20.0/22",
]

# Cloudflare (Claude/Anthropic) — полный список
CLAUDE_SUBNETS = [
    # Cloudflare IPv4 — все диапазоны
    "103.21.244.0/22", "103.22.200.0/22",
    "103.31.4.0/22", "104.16.0.0/13",
    "104.24.0.0/14", "108.162.192.0/18",
    "131.0.72.0/22", "141.101.64.0/18",
    "162.158.0.0/15", "172.64.0.0/13",
    "173.245.48.0/20", "188.114.96.0/20",
    "190.93.240.0/20", "197.234.240.0/22",
    "198.41.128.0/17",
    # Anthropic прямые IP
    "205.185.216.0/23",
    "160.79.104.0/21",
    "160.79.112.0/21",
    "160.79.120.0/21",
]

# Все подсети для split tunneling
ALL_SPLIT_SUBNETS = TELEGRAM_SUBNETS + GOOGLE_SUBNETS + META_SUBNETS + CLAUDE_SUBNETS


def load_config():
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            for k, v in DEFAULT_CONFIG.items():
                cfg.setdefault(k, v)
            return cfg
        except Exception:
            pass
    return DEFAULT_CONFIG.copy()


def save_config(cfg):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


# ──────────────────────────────────────────────
#  УТИЛИТЫ
# ──────────────────────────────────────────────

def log(msg):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")
    except Exception:
        pass


def run_cmd(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True,
                           encoding="cp1251", errors="replace", timeout=15)
        return r.returncode, r.stdout, r.stderr
    except Exception as e:
        return -1, "", str(e)


def get_default_gateway():
    _, out, _ = run_cmd("route print 0.0.0.0")
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 4 and parts[0] == "0.0.0.0" and parts[1] == "0.0.0.0":
            return parts[2], parts[3] if len(parts) > 3 else None
    return None, None


def get_active_interface_name(iface_ip):
    if not iface_ip:
        return None
    skip = ["loopback", "vpn0", "altvpn", "vmware", "virtualbox",
            "tap-windows", "bluetooth", "teredo", "isatap"]
    ps_cmd = f"powershell -Command \"Get-NetIPAddress -IPAddress '{iface_ip}' -ErrorAction SilentlyContinue | Select-Object -ExpandProperty InterfaceAlias\""
    _, out, _ = run_cmd(ps_cmd)
    name = out.strip()
    if name and not any(s in name.lower() for s in skip):
        return name
    _, out2, _ = run_cmd("netsh interface ipv4 show addresses")
    current = None
    for line in out2.splitlines():
        if '"' in line:
            parts = line.split('"')
            if len(parts) >= 2:
                current = parts[1]
        if iface_ip in line and current:
            if not any(s in current.lower() for s in skip):
                return current
    return None


DNS_LOCK_FILE = APP_DIR / ".dns_iface"


def _reset_dns(iface_name):
    if iface_name:
        run_cmd(f'netsh interface ipv4 set dnsservers name="{iface_name}" dhcp validate=no')
        run_cmd("ipconfig /flushdns")
        log(f"DNS сброшен на DHCP для {iface_name}")


def _save_dns_lock(iface_name):
    try:
        with open(DNS_LOCK_FILE, "w") as f:
            f.write(iface_name)
    except Exception:
        pass


def _clear_dns_lock():
    try:
        if DNS_LOCK_FILE.exists():
            DNS_LOCK_FILE.unlink()
    except Exception:
        pass


def _check_dns_lock():
    try:
        if DNS_LOCK_FILE.exists():
            iface_name = DNS_LOCK_FILE.read_text().strip()
            if iface_name:
                log(f"Найден незакрытый DNS lock — сбрасываем {iface_name}")
                _reset_dns(iface_name)
            _clear_dns_lock()
    except Exception:
        pass


# ──────────────────────────────────────────────
#  VPN ENGINE
# ──────────────────────────────────────────────

class VpnEngine(QObject):
    status_changed = pyqtSignal(str)
    log_signal     = pyqtSignal(str)
    cert_error     = pyqtSignal(str)

    def __init__(self, config):
        super().__init__()
        self.config = config
        self._process = None
        self._connected = False
        self._main_gw = None
        self._main_iface_ip = None
        self._vpn_gateway = None
        self._vpn_iface_idx = None
        self._watchdog_running = False
        self._cert_updated = False
        self._dns_iface = None
        self._sleep_monitor_running = False
        self._retrying = False

    def start_sleep_monitor(self):
        """Мониторим пробуждение из сна через WMI."""
        if self._sleep_monitor_running:
            return
        self._sleep_monitor_running = True
        threading.Thread(target=self._monitor_sleep, daemon=True).start()

    def _monitor_sleep(self):
        """Слушаем событие пробуждения Windows."""
        try:
            import win32api, win32con, win32gui, win32event
            import ctypes
            # Регистрируемся на события питания
            HWND_MESSAGE = -3
            WM_POWERBROADCAST = 0x0218
            PBT_APMRESUMEAUTOMATIC = 0x0012
            PBT_APMRESUMESUSPEND = 0x0007

            wc = win32gui.WNDCLASS()
            wc.lpfnWndProc = self._power_wnd_proc
            wc.lpszClassName = "GoArtVPN_PowerMonitor"
            try:
                win32gui.RegisterClass(wc)
            except Exception:
                pass
            hwnd = win32gui.CreateWindow(
                wc.lpszClassName, "", 0, 0, 0, 0, 0,
                HWND_MESSAGE, 0, 0, None
            )
            win32gui.PumpMessages()
        except Exception:
            # Если win32 недоступен — используем простой таймер
            self._monitor_sleep_simple()

    def _power_wnd_proc(self, hwnd, msg, wparam, lparam):
        WM_POWERBROADCAST = 0x0218
        PBT_APMRESUMEAUTOMATIC = 0x0012
        if msg == WM_POWERBROADCAST and wparam == PBT_APMRESUMEAUTOMATIC:
            self.emit_log("💤 Пробуждение из сна — перезапуск VPN...")
            self.stop()
            time.sleep(3)
            self.start()
        return 0

    def _monitor_sleep_simple(self):
        """Простой мониторинг через проверку процесса каждые 30 сек."""
        last_check = time.monotonic()
        while self._sleep_monitor_running:
            time.sleep(10)
            now = time.monotonic()
            # Если прошло больше 60 сек между проверками — был сон
            if now - last_check > 60 and self._connected:
                self.emit_log("💤 Обнаружено пробуждение из сна — перезапуск VPN...")
                self.stop()
                time.sleep(3)
                self.start()
            last_check = now

    def emit_log(self, msg):
        log(msg)
        self.log_signal.emit(msg)

    def start(self):
        if self._connected or self._process:
            return
        self.status_changed.emit("connecting")
        self.emit_log(">>> Запуск подключения...")
        threading.Thread(target=self._run, daemon=True).start()

    def stop(self):
        self._watchdog_running = False
        self._teardown()
        if self._process:
            try:
                self._process.terminate()
                time.sleep(2)
                if self._process.poll() is None:
                    self._process.kill()
            except Exception:
                pass
            self._process = None
        self._connected = False
        self._vpn_iface_idx = None
        self.status_changed.emit("disconnected")

    def _run(self):
        cfg = self.config
        iface = cfg.get("interface", "vpn0")

        run_cmd("taskkill /F /IM openconnect.exe 2>nul")
        run_cmd(f'netsh interface delete "{iface}" 2>nul')
        time.sleep(1)

        self._main_gw, self._main_iface_ip = get_default_gateway()

        server = cfg["server"]
        if not server.endswith(".goart.work"):
            server = f"{server}.goart.work"

        cert = cfg.get("servercert", "")
        cmd = [
            str(OPENCONNECT_EXE),
            f"{server}:{cfg.get('port', 443)}",
            f"--user={cfg['user']}",
            "--passwd-on-stdin",
            f"--interface={iface}",
            "--non-inter",
            "--no-proxy",
            f"--reconnect-timeout={cfg.get('reconnect_timeout', 300)}",
        ]
        if cfg.get("no_dtls"):
            cmd.append("--no-dtls")
        if cfg.get("disable_ipv6"):
            cmd.append("--disable-ipv6")
        cmd.append("--no-http-keepalive")
        cmd.append("--force-dpd=10")
        cmd.append(f"--servercert={cert}" if cert else "--no-certificate-check")

        env = os.environ.copy()
        env["PATH"] = str(BIN_DIR) + ";C:\\Windows\\System32;" + env.get("PATH", "")

        try:
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = 0
            self._process = subprocess.Popen(
                cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, text=False, bufsize=0,
                env=env, cwd=str(BIN_DIR), startupinfo=si,
                creationflags=0x08000000,
            )
            self._process.stdin.write((cfg["password"] + "\n").encode("utf-8"))
            self._process.stdin.flush()

            buf = b""
            while True:
                chunk = self._process.stdout.read(1)
                if not chunk:
                    break
                buf += chunk
                if chunk == b"\n":
                    line = buf.decode("cp1251", errors="replace").rstrip()
                    buf = b""
                    if line:
                        self._on_line(line)
                if self._process.poll() is not None:
                    break
        except Exception as e:
            self.emit_log(f"Ошибка запуска: {e}")

        was_connected = self._connected
        self._connected = False
        self._teardown()

        if self._cert_updated:
            self._cert_updated = False
            self.status_changed.emit("connecting")
            time.sleep(2)
            threading.Thread(target=self._run, daemon=True).start()
            return

        if was_connected and self._watchdog_running:
            self.emit_log("⚠ Соединение упало — авто-перезапуск...")
            self.status_changed.emit("connecting")
            if not self._retrying:
                self._retrying = True
                threading.Thread(target=self._retry_connect, daemon=True).start()
            return

        self.status_changed.emit("disconnected")

    def _retry_connect(self):
        """Повторяем подключение пока не получится."""
        attempt = 0
        while self._watchdog_running:
            attempt += 1
            wait = min(15 * attempt, 60)
            self.emit_log(f"Попытка {attempt}, ожидание {wait} сек...")
            time.sleep(wait)
            if not self._watchdog_running:
                self._retrying = False
                break
            # Проверяем и IP и DNS
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(5)
                s.connect(("8.8.8.8", 53))
                s.close()
            except Exception:
                self.emit_log(f"Интернет недоступен, ждём...")
                continue
            try:
                server = self.config.get("server", "")
                if not server.endswith(".goart.work"):
                    server = f"{server}.goart.work"
                socket.getaddrinfo(server, 443)
                self.emit_log(f"Интернет и DNS есть — подключаемся (попытка {attempt})...")
                self._retrying = False
                threading.Thread(target=self._run, daemon=True).start()
                return
            except Exception:
                self.emit_log(f"DNS ещё не работает, ждём...")
                continue

    def _on_line(self, line):
        self.emit_log(line)
        ll = line.lower()

        if not self._connected and any(kw in ll for kw in [
            "cstp connected", "tunnel connected", "established", "session established"
        ]):
            self._connected = True
            self.status_changed.emit("connected")
            threading.Thread(target=self._on_connected, daemon=True).start()

        if ("using tap-windows device" in ll or "using wintun device" in ll) and ", index " in ll:
            try:
                self._vpn_iface_idx = int(line.split(", index ")[-1].strip())
            except Exception:
                pass

        if "public vpn gateway address:" in ll:
            try:
                self._vpn_gateway = line.split(":")[-1].strip()
            except Exception:
                pass

        if "None of the" in line and "pin-sha256:" in line:
            try:
                pin = "pin-sha256:" + line.split("pin-sha256:")[-1].strip()
                if pin != self.config.get("servercert"):
                    self.config["servercert"] = pin
                    save_config(self.config)
                    self.emit_log(f"✓ Сертификат обновлён: {pin}")
                    self._cert_updated = True
                    self.cert_error.emit(pin)
            except Exception:
                pass

    def _on_connected(self):
        import ipaddress

        # Ждём индекс интерфейса
        for _ in range(20):
            if self._vpn_iface_idx:
                break
            time.sleep(0.5)

        time.sleep(1)

        split = self.config.get("split_tunneling", True)

        if split:
            # ── SPLIT TUNNELING: удаляем дефолтный маршрут VPN ──
            _, out, _ = run_cmd("route print 0.0.0.0")
            for line in out.splitlines():
                parts = line.split()
                if len(parts) >= 3 and parts[0] == "0.0.0.0" and parts[1] == "0.0.0.0":
                    gw = parts[2]
                    if self._main_gw and gw != self._main_gw:
                        run_cmd(f"route delete 0.0.0.0 mask 0.0.0.0 {gw}")
                        self.emit_log(f"Удалён дефолтный маршрут VPN через {gw}")

            # Маршрут к VPN серверу через основной шлюз
            if self._main_gw:
                try:
                    ip = socket.gethostbyname(self.config["server"])
                    run_cmd(f"route add {ip} mask 255.255.255.255 {self._main_gw}")
                except Exception:
                    pass

            # Прописываем ВСЕ статические подсети через VPN одной командой
            if self._vpn_iface_idx:
                # Собираем все маршруты в один батч-файл и запускаем
                import tempfile
                lines = ["@echo off"]
                count = 0
                for subnet in ALL_SPLIT_SUBNETS:
                    net_obj = ipaddress.IPv4Network(subnet, strict=False)
                    lines.append(
                        f"route add {net_obj.network_address} "
                        f"mask {net_obj.netmask} "
                        f"0.0.0.0 if {self._vpn_iface_idx}"
                    )
                    count += 1
                bat_path = APP_DIR / "_routes.bat"
                with open(bat_path, "w") as f:
                    f.write("\n".join(lines))
                run_cmd(f'cmd /c "{bat_path}"')
                try:
                    bat_path.unlink()
                except Exception:
                    pass
                self.emit_log(f"✓ Split tunneling: {count} подсетей прописано через VPN")

            # DNS — ставим Google DNS напрямую (без прокси)
            active_iface = get_active_interface_name(self._main_iface_ip)
            if active_iface:
                run_cmd(f'netsh interface ipv4 set dnsservers name="{active_iface}" static 8.8.8.8 primary validate=no')
                run_cmd(f'netsh interface ipv4 add dnsservers name="{active_iface}" address=1.1.1.1 index=2 validate=no')
                run_cmd("ipconfig /flushdns")
                self._dns_iface = active_iface
                _save_dns_lock(active_iface)
                self.emit_log(f"DNS: 8.8.8.8 / 1.1.1.1 → {active_iface}")

        else:
            # ── ВЕСЬ ТРАФИК ЧЕРЕЗ VPN ──
            self.emit_log("🌐 Режим: весь трафик через VPN")
            if self._vpn_iface_idx:
                count = 0
                for subnet in ALL_SPLIT_SUBNETS:
                    net_obj = ipaddress.IPv4Network(subnet, strict=False)
                    run_cmd(
                        f"route add {net_obj.network_address} "
                        f"mask {net_obj.netmask} "
                        f"0.0.0.0 if {self._vpn_iface_idx}"
                    )
                    count += 1

        self._watchdog_running = True
        threading.Thread(target=self._watchdog, daemon=True).start()

    def _watchdog(self):
        interval = self.config.get("watchdog_interval", 10)
        while self._watchdog_running and self._connected:
            time.sleep(interval)
            if not self._watchdog_running:
                break
            if self._process and self._process.poll() is not None:
                self.emit_log("⚠ Watchdog: процесс упал — перезапуск через 5 сек...")
                self._teardown()
                self._connected = False
                self._process = None
                self._vpn_iface_idx = None
                if self._watchdog_running and not self._retrying:
                    self._retrying = True
                    threading.Thread(target=self._retry_connect, daemon=True).start()
                break

    def _teardown(self):
        if self._dns_iface:
            _reset_dns(self._dns_iface)
            self._dns_iface = None
        _clear_dns_lock()


# ──────────────────────────────────────────────
#  ИКОНКИ
# ──────────────────────────────────────────────

def make_icon(color):
    px = QPixmap(64, 64)
    px.fill(Qt.GlobalColor.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setBrush(QBrush(QColor(color)))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(4, 4, 56, 56)
    p.end()
    return QIcon(px)


ICON_GREEN = ICON_RED = ICON_YELLOW = None

STYLE = """
QWidget { background-color: #1e1e1e; color: #d4d4d4;
          font-family: 'Segoe UI', sans-serif; font-size: 13px; }
QLabel { color: #d4d4d4; }
QLineEdit, QComboBox {
    background: #2d2d2d; border: 1px solid #3e3e3e;
    border-radius: 4px; padding: 6px 8px; color: #d4d4d4; }
QLineEdit:focus, QComboBox:focus { border-color: #007acc; }
QComboBox::drop-down { border: none; width: 20px; }
QTextEdit {
    background: #0d0d0d; border: 1px solid #3e3e3e;
    border-radius: 4px; color: #00ff00;
    font-family: 'Consolas', 'Courier New', monospace; font-size: 12px; }
QPushButton {
    border-radius: 4px; padding: 8px 20px;
    font-size: 13px; font-weight: bold; color: white; border: none; }
QPushButton#btn_start { background: #0e639c; }
QPushButton#btn_start:hover { background: #1177bb; }
QPushButton#btn_start:disabled { background: #3e3e3e; color: #666; }
QPushButton#btn_stop { background: #6b1a1a; }
QPushButton#btn_stop:hover { background: #8b2020; }
QPushButton#btn_stop:disabled { background: #3e3e3e; color: #666; }
"""


class MainWindow(QWidget):
    def __init__(self, config, engine, tray_icon):
        super().__init__()
        self.config = config
        self.engine = engine
        self.tray_icon = tray_icon
        self.engine.status_changed.connect(self._on_status)
        self.engine.log_signal.connect(self._append_log)
        self.engine.cert_error.connect(self._on_cert_error)

        # Таймер постоянного обновления иконки трея
        self._tray_timer = QTimer()
        self._tray_timer.timeout.connect(self._update_tray)
        self._tray_timer.start(3000)

        self.setWindowTitle("GoArt VPN Control")
        self.setMinimumSize(480, 540)
        self.resize(480, 580)
        self.setStyleSheet(STYLE)
        self._build_ui()
        self._on_status("disconnected")

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(8)

        root.addWidget(QLabel("Сервер:"))
        self.combo_server = QComboBox()
        self.combo_server.setEditable(True)
        self.combo_server.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        current = self.config.get("server", "")
        idx = 0
        for i, (label, slug) in enumerate(SERVERS):
            host = f"{slug}.{DOMAIN}"
            self.combo_server.addItem(host, host)
            if host == current or slug == current:
                idx = i
        self.combo_server.setCurrentIndex(idx)
        root.addWidget(self.combo_server)

        root.addWidget(QLabel("Пользователь:"))
        self.edit_user = QLineEdit(self.config.get("user", ""))
        root.addWidget(self.edit_user)

        root.addWidget(QLabel("Пароль:"))
        self.edit_pass = QLineEdit(self.config.get("password", ""))
        self.edit_pass.setEchoMode(QLineEdit.EchoMode.Password)
        root.addWidget(self.edit_pass)

        # Кнопки подключения
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        self.btn_start = QPushButton("ПОДКЛЮЧИТЬ")
        self.btn_start.setObjectName("btn_start")
        self.btn_start.clicked.connect(self._do_start)
        self.btn_stop = QPushButton("СТОП")
        self.btn_stop.setObjectName("btn_stop")
        self.btn_stop.clicked.connect(self._do_stop)
        btn_row.addWidget(self.btn_start)
        btn_row.addWidget(self.btn_stop)
        root.addLayout(btn_row)

        # Кнопки утилит
        util_row = QHBoxLayout()
        util_row.setSpacing(6)

        self.btn_scan = QPushButton("🔍 Лучший сервер")
        self.btn_scan.setStyleSheet("background:#2d5016;border-radius:4px;padding:6px 10px;color:white;border:none;font-size:12px;")
        self.btn_scan.clicked.connect(self._do_scan)

        self.btn_cert = QPushButton("🔐 Сертификат")
        self.btn_cert.setStyleSheet("background:#4a3000;border-radius:4px;padding:6px 10px;color:white;border:none;font-size:12px;")
        self.btn_cert.clicked.connect(self._do_update_cert)
        self.btn_cert.setVisible(False)

        self.btn_all_vpn = QPushButton("🌐 Весь → VPN")
        self.btn_all_vpn.setStyleSheet("background:#1a3a5c;border-radius:4px;padding:6px 10px;color:white;border:none;font-size:12px;")
        self.btn_all_vpn.setCheckable(True)
        self.btn_all_vpn.setChecked(not self.config.get("split_tunneling", True))
        self.btn_all_vpn.clicked.connect(self._toggle_all_vpn)

        util_row.addWidget(self.btn_scan)
        util_row.addWidget(self.btn_cert)
        util_row.addWidget(self.btn_all_vpn)
        root.addLayout(util_row)

        # Кастомные домены (информационное поле)
        row_custom = QHBoxLayout()
        row_custom.addWidget(QLabel("Свои подсети (CIDR через запятую):"))
        root.addLayout(row_custom)
        self.edit_custom = QLineEdit()
        self.edit_custom.setPlaceholderText("192.168.100.0/24, 10.0.0.0/8")
        custom_list = self.config.get("custom_patterns", [])
        self.edit_custom.setText(", ".join(custom_list))
        self.edit_custom.editingFinished.connect(self._save_custom)
        root.addWidget(self.edit_custom)

        root.addWidget(QLabel("Лог событий:"))
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        root.addWidget(self.log_text)

    def _do_start(self):
        if self.engine._connected or self.engine._process:
            return
        if not OPENCONNECT_EXE.exists():
            QMessageBox.critical(self, "Ошибка", f"openconnect.exe не найден!\n{BIN_DIR}")
            return
        server = self.combo_server.currentData() or self.combo_server.currentText().strip()
        if server and not server.endswith(".goart.work"):
            server = f"{server}.{DOMAIN}"
        self.config["server"] = server
        self.config["user"] = self.edit_user.text().strip()
        self.config["password"] = self.edit_pass.text()
        text = self.edit_custom.text().strip()
        self.config["custom_patterns"] = [p.strip() for p in text.split(",") if p.strip()]
        save_config(self.config)
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(False)
        QTimer.singleShot(30000, lambda: self._on_status(
            "connected" if self.engine._connected else "disconnected"))
        self.engine.start()

    def _do_stop(self):
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(False)
        self.engine.stop()
        QTimer.singleShot(5000, lambda: self._on_status("disconnected"))

    def _update_tray(self):
        """Постоянно обновляем иконку трея по реальному состоянию."""
        if self.engine._connected:
            self._on_status("connected")
        elif self.engine._process:
            self._on_status("connecting")

    def _on_status(self, status):
        connected = status == "connected"
        connecting = status == "connecting"
        self.btn_start.setEnabled(not connected and not connecting)
        self.btn_stop.setEnabled(connected)
        if self.tray_icon:
            if status == "connected":
                self.tray_icon.setIcon(ICON_GREEN)
                self.tray_icon.setToolTip("GoArt VPN — Подключено ✓")
            elif status == "connecting":
                self.tray_icon.setIcon(ICON_YELLOW)
                self.tray_icon.setToolTip("GoArt VPN — Подключение...")
            else:
                self.tray_icon.setIcon(ICON_RED)
                self.tray_icon.setToolTip("GoArt VPN — Отключено")

    def _on_cert_error(self, pin):
        self.btn_cert.setVisible(True)
        self._append_log('<span style="color:#ff8c00;">⚠ Новый сертификат — нажмите "Сертификат"</span>')

    def _do_update_cert(self):
        self.btn_cert.setVisible(False)
        self.engine.stop()
        time.sleep(2)
        self.engine.start()

    def _toggle_all_vpn(self, checked):
        if checked:
            self.btn_all_vpn.setText("✓ Весь → VPN")
            self.btn_all_vpn.setStyleSheet("background:#5c1a1a;border-radius:4px;padding:6px 10px;color:white;border:none;font-size:12px;")
            self.config["split_tunneling"] = False
            save_config(self.config)
            self._append_log('<span style="color:#ed8936;">🌐 Режим: ВЕСЬ трафик через VPN</span>')
        else:
            self.btn_all_vpn.setText("🌐 Весь → VPN")
            self.btn_all_vpn.setStyleSheet("background:#1a3a5c;border-radius:4px;padding:6px 10px;color:white;border:none;font-size:12px;")
            self.config["split_tunneling"] = True
            save_config(self.config)
            self._append_log('<span style="color:#48bb78;">✓ Режим: Split tunneling (статические подсети)</span>')
        if self.engine._connected:
            self.engine.stop()
            QTimer.singleShot(3000, self.engine.start)

    def _do_scan(self):
        if self.engine._connected:
            QMessageBox.information(self, "Инфо", "Сначала отключитесь от VPN")
            return
        self.btn_scan.setEnabled(False)
        self.btn_scan.setText("⏳ Проверка...")
        self._append_log(">>> Поиск лучшего сервера...")
        threading.Thread(target=self._scan_servers, daemon=True).start()

    def _scan_servers(self):
        import socket as sock
        import urllib.request

        CHECK_URLS = [
            ("YouTube",   "https://www.youtube.com/generate_204", "www.youtube.com"),
            ("Instagram", "https://www.instagram.com/",           "www.instagram.com"),
            ("Claude",    "https://claude.ai/",                   "claude.ai"),
        ]

        ping_results = []
        for label, slug in SERVERS:
            host = f"{slug}.{DOMAIN}"
            try:
                t = time.time()
                s = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
                s.settimeout(3)
                s.connect((host, 443))
                s.close()
                ms = int((time.time() - t) * 1000)
                ping_results.append((ms, label, slug, host))
            except Exception:
                pass

        ping_results.sort()
        top = ping_results[:10]
        self.engine.log_signal.emit(f"    Доступно: {len(ping_results)}, проверяем топ-10...")

        best_score = -1
        best_label = None
        best_host  = None

        for ms, label, slug, host in top:
            self.engine.log_signal.emit(f"  → {label} ({ms}ms)...")
            self.config["server"] = host
            save_config(self.config)

            connected_event = threading.Event()
            orig = self.engine._on_connected
            def patched():
                orig()
                connected_event.set()
            self.engine._on_connected = patched
            self.engine._connected = False
            self.engine._process = None
            self.engine._vpn_iface_idx = None
            self.engine._watchdog_running = True
            threading.Thread(target=self.engine._run, daemon=True).start()
            ok = connected_event.wait(35)
            self.engine._on_connected = orig

            if not ok:
                self.engine.log_signal.emit(f"  ✗ {label}: не подключился")
                self.engine.stop()
                time.sleep(3)
                continue

            time.sleep(8)

            score = 0
            for site_name, url, _ in CHECK_URLS:
                try:
                    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                    resp = urllib.request.urlopen(req, timeout=10)
                    if resp.status in (200, 204):
                        score += 1
                        self.engine.log_signal.emit(f"    ✓ {site_name}")
                    else:
                        self.engine.log_signal.emit(f"    ~ {site_name}: {resp.status}")
                        score += 0.5
                except Exception as e:
                    self.engine.log_signal.emit(f"    ✗ {site_name}: {str(e)[:40]}")

            self.engine.log_signal.emit(f"    Счёт: {score}/{len(CHECK_URLS)}")
            if score > best_score:
                best_score = score
                best_label = label
                best_host  = host

            self.engine.stop()
            time.sleep(3)
            if best_score == len(CHECK_URLS):
                break

        if best_host:
            self.engine.log_signal.emit(f">>> 🏆 Лучший: {best_label} ({best_score}/{len(CHECK_URLS)})")
            self.config["server"] = best_host
            save_config(self.config)
            for i in range(self.combo_server.count()):
                if self.combo_server.itemData(i) == best_host:
                    self.combo_server.setCurrentIndex(i)
                    break
        else:
            self.engine.log_signal.emit(">>> Ни один сервер не прошёл проверку")
            save_config(self.config)

        self.btn_scan.setEnabled(True)
        self.btn_scan.setText("🔍 Лучший сервер")

    def _save_custom(self):
        text = self.edit_custom.text().strip()
        patterns = [p.strip() for p in text.split(",") if p.strip()]
        self.config["custom_patterns"] = patterns
        save_config(self.config)

    def _append_log(self, msg):
        self.log_text.append(f'<span style="color:#00ff00;">{msg}</span>')
        self.log_text.moveCursor(QTextCursor.MoveOperation.End)

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        if self.tray_icon:
            self.tray_icon.showMessage("GoArt VPN", "Работает в трее",
                                       QSystemTrayIcon.MessageIcon.Information, 2000)


class TrayApp(QObject):
    def __init__(self, config, engine, window):
        super().__init__()
        self.window = window
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(ICON_RED)
        self.tray.setToolTip("GoArt VPN — Отключено")
        self.tray.activated.connect(self._on_click)
        menu = QMenu()
        act_show = QAction("Открыть", menu)
        act_show.triggered.connect(self._show)
        menu.addAction(act_show)
        menu.addSeparator()
        act_quit = QAction("✕  Выход", menu)
        act_quit.triggered.connect(self._quit)
        menu.addAction(act_quit)
        self.tray.setContextMenu(menu)
        self.tray.show()
        self._engine = engine

    def _on_click(self, reason):
        if reason in (QSystemTrayIcon.ActivationReason.Trigger,
                      QSystemTrayIcon.ActivationReason.DoubleClick):
            self._show()

    def _show(self):
        self.window.show()
        self.window.raise_()
        self.window.activateWindow()

    def _quit(self):
        self._engine.stop()
        QApplication.quit()


def main():
    if sys.platform == "win32":
        import ctypes

        if not ctypes.windll.shell32.IsUserAnAdmin():
            args = " ".join(f'"{a}"' for a in sys.argv)
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, args, None, 1)
            sys.exit(0)

        # Защита от второго запуска (после получения прав админа)
        mutex = ctypes.windll.kernel32.CreateMutexW(None, True, "GoArtVPN_SingleInstance_Admin")
        if ctypes.windll.kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
            ctypes.windll.user32.MessageBoxW(0, "GoArt VPN уже запущен!", "GoArt VPN", 0x40)
            sys.exit(0)

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    global ICON_GREEN, ICON_RED, ICON_YELLOW
    ICON_GREEN  = make_icon("#48bb78")
    ICON_RED    = make_icon("#fc8181")
    ICON_YELLOW = make_icon("#ed8936")

    _check_dns_lock()
    config = load_config()
    save_config(config)

    engine = VpnEngine(config)
    engine.start_sleep_monitor()

    window = MainWindow(config, engine, None)
    tray_app = TrayApp(config, engine, window)  # noqa
    window.tray_icon = tray_app.tray  # используем иконку из TrayApp

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()