import datetime
import os
import sqlite3
import http.server
import socketserver
import threading
import time
import asyncio
import websockets
import json
import sys
import re
import shutil
import uuid
from urllib.parse import quote

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_GUI_HTML_PATH = os.path.join(BASE_DIR, "templates", "log_viewer_gui.html")
LOGS_BASE_DIR = os.path.join(BASE_DIR, "logs")

class Colors:
    RESET = "\033[0m"
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

LOG_LEVEL_COLORS = {
    "DEBUG": Colors.BRIGHT_BLACK,
    "INFO": Colors.CYAN,
    "WARNING": Colors.YELLOW,
    "ERROR": Colors.RED,
    "CRITICAL": Colors.BRIGHT_RED + "\033[1m",
}

LOG_LEVELS = {
    "DEBUG": 10,
    "INFO": 20,
    "WARNING": 30,
    "ERROR": 40,
    "CRITICAL": 50
}

CONNECTED_WEBSOCKETS = set()
log_queue = asyncio.Queue()
_websocket_event_loop = None

UNIQUE_LOG_ID = datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + str(uuid.uuid4())[:8]

WEB_GUI_HTML_PATH = os.path.join(BASE_DIR, "log_viewer_gui.html")
WEB_SERVER_PORT = 8000
WEBSOCKET_PORT = 8001

_http_server_instance = None
_websocket_thread = None
_gui_initialized = False

web_server_logger = None
main_app_logger_instance = None

class Formatter:
    def __init__(self, fmt: str = "[%(timestamp)s] - %(level)s - %(name)s - %(message)s"):
        self.fmt = fmt

    def format(self, level: str, name: str, message: str) -> str:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        formatted_message = self.fmt.replace('%(timestamp)s', timestamp)
        formatted_message = formatted_message.replace('%(level)s', level)
        formatted_message = formatted_message.replace('%(name)s', name)
        formatted_message = formatted_message.replace('%(message)s', message)
        return formatted_message

class Handler:
    def __init__(self, level: str = "INFO", formatter: Formatter = None):
        if level not in LOG_LEVELS:
            raise ValueError(f"Geçersiz log seviyesi: {level}. Geçerli seviyeler: {list(LOG_LEVELS.keys())}")
        self.level = LOG_LEVELS.get(level)
        self.formatter = formatter if formatter else Formatter()

    def emit(self, level: str, name: str, message: str):
        raise NotImplementedError("Bu metod alt sınıflar tarafından uygulanmalıdır.")

    def should_log(self, level: str) -> bool:
        return LOG_LEVELS.get(level, LOG_LEVELS["INFO"]) >= self.level

    def close(self):
        pass

    def clear(self):
        raise NotImplementedError("Bu metod alt sınıflar tarafından uygulanmalıdır.")

class ConsoleHandler(Handler):
    def emit(self, level: str, name: str, message: str):
        if self.should_log(level):
            formatted_msg = self.formatter.format(level, name, message)
            color_code = LOG_LEVEL_COLORS.get(level, Colors.RESET)
            print(f"{color_code}{formatted_msg}{Colors.RESET}")

    def clear(self):
        if web_server_logger:
            web_server_logger.warning("ConsoleHandler'ı temizlemek doğrudan konsolu temizlemez.")

class FileHandler(Handler):
    def __init__(self, base_filename: str, level: str = "INFO", formatter: Formatter = None, encoding: str = "utf-8"):
        super().__init__(level, formatter)
        self.base_filename = base_filename
        self.filename = self._get_log_file_path()
        self.encoding = encoding
        self._ensure_dir_exists()
        self.file = open(self.filename, 'a', encoding=self.encoding)

    def _get_log_file_path(self):
        log_dir = os.path.join(LOGS_BASE_DIR, "log")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        return os.path.join(log_dir, f"{self.base_filename}_{UNIQUE_LOG_ID}.log")

    def _ensure_dir_exists(self):
        dir_name = os.path.dirname(self.filename)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name)

    def emit(self, level: str, name: str, message: str):
        if self.should_log(level):
            formatted_msg = self.formatter.format(level, name, message)
            self.file.write(formatted_msg + '\n')
            self.file.flush()

    def clear(self):
        if self.file and not self.file.closed:
            self.file.close()
        try:
            self.file = open(self.filename, 'w', encoding=self.encoding)
            self.file.flush()
            if web_server_logger:
                web_server_logger.info(f"Dosya logları temizlendi: {self.filename}")
        except Exception as e:
            if web_server_logger:
                web_server_logger.error(f"Dosya logları temizlenirken hata: {e}")
            self.file = open(self.filename, 'a', encoding=self.encoding)

    def close(self):
        if self.file and not self.file.closed:
            self.file.close()
        super().close()

class DatabaseHandler(Handler):
    def __init__(self, base_filename: str, level: str = "INFO", formatter: Formatter = None):
        super().__init__(level, formatter)
        self.base_filename = base_filename
        self.db_path = self._get_db_file_path()
        self.conn = None
        self.cursor = None
        self._connect_db()
        self._ensure_dir_exists()

    def _get_db_file_path(self):
        db_dir = os.path.join(LOGS_BASE_DIR, "db")
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
        return os.path.join(db_dir, f"{self.base_filename}_{UNIQUE_LOG_ID}.db")

    def _ensure_dir_exists(self):
        dir_name = os.path.dirname(self.db_path)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name)

    def _connect_db(self):
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS custom_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    level TEXT,
                    name TEXT,
                    message TEXT
                )
            ''')
            self.conn.commit()
        except sqlite3.Error as e:
            if web_server_logger:
                web_server_logger.error(f"Veritabanı bağlantı hatası: {e}")
            else:
                print(f"Veritabanı bağlantı hatası: {e}")
            self.conn = None
            self.cursor = None

    def emit(self, level: str, name: str, message: str):
        if not self.conn or not self.cursor:
            if web_server_logger:
                web_server_logger.warning("Veritabanı bağlantısı yok veya başarısız oldu, log kaydedilemedi.")
            else:
                print("Veritabanı bağlantısı yok veya başarısız oldu, log kaydedilemedi.")
            return

        if self.should_log(level):
            formatted_data = self.formatter.format(level, name, message)
            parts = formatted_data.split(' - ', 3)

            if len(parts) >= 3:
                timestamp_str = parts.pop(0).strip('[]')
                level_str = parts.pop(0).strip()
                log_name = parts.pop(0).strip()
                log_message = parts.pop(0).strip() if parts else ""

                try:
                    self.cursor.execute(
                        "INSERT INTO custom_logs (timestamp, level, name, message) VALUES (?, ?, ?, ?)",
                        (timestamp_str, level_str, log_name, log_message)
                    )
                    self.conn.commit()
                except sqlite3.Error as e:
                    if web_server_logger:
                        web_server_logger.error(f"Veritabanına log kaydederken hata oluştu: {e}")
                    else:
                        print(f"Veritabanına log kaydederken hata oluştu: {e}")
            else:
                if web_server_logger:
                    web_server_logger.error(f"Biçimlendirme hatası: Log mesajı beklendiği gibi ayrılamadı. Mesaj: {formatted_data}")
                else:
                    print(f"Biçimlendirme hatası: Log mesajı beklendiği gibi ayrılamadı. Mesaj: {formatted_data}")

    def clear(self):
        if self.conn and self.cursor:
            try:
                self.cursor.execute("DELETE FROM custom_logs")
                self.conn.commit()
                if web_server_logger:
                    web_server_logger.info(f"Veritabanı logları temizlendi: {self.db_path}")
            except sqlite3.Error as e:
                if web_server_logger:
                    web_server_logger.error(f"Veritabanı logları temizlenirken hata: {e}")

    def close(self):
        if self.conn:
            self.conn.close()
        super().close()

class Logger:
    _instances = {}

    def __new__(cls, name: str, level: str = "INFO", gui: bool = False):
        if name not in cls._instances:
            instance = super().__new__(cls)
            cls._instances.setdefault(name, instance)
            instance._initialized = False
        return cls._instances.get(name)

    def __init__(self, name: str, level: str = "INFO", gui: bool = False):
        if self._initialized:
            if LOG_LEVELS.get(level, LOG_LEVELS["INFO"]) > self.level:
                self.level = LOG_LEVELS.get(level)
            return

        if level not in LOG_LEVELS:
            raise ValueError(f"Geçersiz log seviyesi: {level}. Geçerli seviyeler: {list(LOG_LEVELS.keys())}")

        self.name = name
        self.level = LOG_LEVELS.get(level)
        self.handlers = []
        self._initialized = True
        self.gui_enabled = gui

        global _gui_initialized, web_server_logger, main_app_logger_instance
        if self.gui_enabled and not _gui_initialized:
            if web_server_logger is None:
                web_server_logger = Logger(name="WebServerInit", level="INFO")
                if not os.path.exists(LOGS_BASE_DIR):
                    os.makedirs(LOGS_BASE_DIR)
                web_server_logger.add_handler(FileHandler("web_server", level="INFO"))
                web_server_logger.info("Web server init logger başlatıldı.")

            _start_logger_gui_servers_internal(self)
            _gui_initialized = True
        else:
            if web_server_logger:
                 web_server_logger.debug("GUI sunucuları zaten başlatılmış veya GUI modu etkin değil.")
        
        if self.gui_enabled:
            main_app_logger_instance = self


    def add_handler(self, handler: Handler):
        if handler not in self.handlers:
            self.handlers.append(handler)

    def remove_handler(self, handler: Handler):
        if handler in self.handlers:
            self.handlers.remove(handler)
            handler.close()

    def _log(self, level: str, message: str):
        if LOG_LEVELS.get(level, LOG_LEVELS["INFO"]) >= self.level:
            formatted_message = self.handlers and self.handlers[-1].formatter.format(level, self.name, message) \
                                or f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] - {level} - {self.name} - {message}"

            log_entry_data = {
                "timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "level": level,
                "name": self.name,
                "message": message,
                "formatted_message": formatted_message
            }
        
            global _websocket_event_loop
            if self.gui_enabled and _websocket_event_loop and _websocket_event_loop.is_running():
                try:
                    _websocket_event_loop.call_soon_threadsafe(log_queue.put_nowait, log_entry_data)
                except Exception as e:
                    if web_server_logger:
                        web_server_logger.error(f"Log kuyruğuna eklenirken hata: {e}")
                    else:
                        print(f"Log kuyruğuna eklenirken hata: {e}")

            for handler in self.handlers:
                try:
                    handler.emit(level, self.name, message)
                except Exception as e:
                    if web_server_logger:
                        web_server_logger.error(f"Loglama hatası: İşleyici '{handler.__class__.__name__}' log kaydederken sorun yaşadı: {e}")
                    else:
                        print(f"Loglama hatası: İşleyici '{handler.__class__.__name__}' log kaydederken sorun yaşadı: {e}")

    def debug(self, message: str):
        self._log("DEBUG", message)
    def info(self, message: str):
        self._log("INFO", message)
    def warning(self, message: str):
        self._log("WARNING", message)
    def error(self, message: str):
        self._log("ERROR", message)
    def critical(self, message: str):
        self._log("CRITICAL", message)

    def close(self):
        for handler in self.handlers:
            handler.close()
        self.handlers = []
        if self.name in Logger._instances:
            del Logger._instances[self.name]


    def clear_handlers(self, target: str):
        global main_app_logger_instance
        if web_server_logger:
            web_server_logger.info(f"Temizleme isteği alındı: {target}")

        for handler in self.handlers:
            handler_name = handler.__class__.__name__
            if target == "console" and handler_name == "ConsoleHandler":
                handler.clear()
            elif target == "file" and handler_name == "FileHandler":
                handler.clear()
            elif target == "database" and handler_name == "DatabaseHandler":
                handler.clear()
            elif target == "all":
                handler.clear()
        
        if self.gui_enabled:
            pass


async def websocket_server_start_handler(websocket, path=None):
    CONNECTED_WEBSOCKETS.add(websocket)
    web_server_logger.info(f"Yeni web soketi bağlantısı: {websocket.remote_address}. Toplam bağlantı: {len(CONNECTED_WEBSOCKETS)}")
    try:
        all_logs = []
        for subdir, _, files in os.walk(LOGS_BASE_DIR):
            for file in files:
                if file.endswith('.log'):
                    filepath = os.path.join(subdir, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            for line in f:
                                log_pattern = re.compile(r"^\[(.*?)\] - (DEBUG|INFO|WARNING|ERROR|CRITICAL) - (.*?) - (.*)$")
                                match = log_pattern.match(line.strip())
                                if match:
                                    timestamp, level, name, message = match.groups()
                                    all_logs.append({"timestamp": timestamp, "level": level, "name": name, "message": message, "formatted_message": line.strip()})
                                else:
                                    all_logs.append({"timestamp": "N/A", "level": "UNKNOWN", "name": file, "message": line.strip(), "formatted_message": line.strip()})
                    except FileNotFoundError:
                        web_server_logger.warning(f"Başlangıç logları için '{filepath}' dosyası bulunamadı.")
                    except Exception as e:
                        web_server_logger.error(f"Başlangıç logları okunurken hata: {e}")

        for log_entry in all_logs[-200:]:
            await websocket.send(json.dumps(log_entry))

        await websocket.wait_closed()
    finally:
        CONNECTED_WEBSOCKETS.remove(websocket)
        web_server_logger.info(f"Web soketi bağlantısı kesildi. Kalan bağlantı: {len(CONNECTED_WEBSOCKETS)}")

async def broadcast_logs_to_clients():
    while True:
        try:
            log_entry = await log_queue.get()
            message = json.dumps(log_entry)
            for websocket in list(CONNECTED_WEBSOCKETS):
                try:
                    await websocket.send(message)
                except websockets.exceptions.ConnectionClosed:
                    pass
                except Exception as e:
                    web_server_logger.error(f"Log gönderirken hata: {e}")
        except asyncio.CancelledError:
            web_server_logger.info("Broadcast görevi iptal edildi.")
            break
        except Exception as e:
            web_server_logger.error(f"Broadcast görevi beklenmedik hata: {e}")


async def _start_websocket_server_async_coroutine():
    web_server_logger.info(f"Web Soketi Sunucusu ws://localhost:{WEBSOCKET_PORT} adresinde başlatılıyor...")
    
    asyncio.create_task(broadcast_logs_to_clients())
    
    try:
        server = await websockets.serve(websocket_server_start_handler, "localhost", WEBSOCKET_PORT)
        web_server_logger.info(f"WebSockets sunucusu ws://localhost:{WEBSOCKET_PORT} adresinde çalışıyor.")
        await server.wait_closed()
    except asyncio.CancelledError:
        web_server_logger.info("WebSocket sunucusu başlatma görevi iptal edildi.")
    except Exception as e:
        web_server_logger.critical(f"WebSocket sunucusu başlatılırken kritik hata: {e}")
    finally:
        pass


def _run_websocket_server_in_thread(loop):
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(_start_websocket_server_async_coroutine())
    except Exception as e:
        web_server_logger.critical(f"WebSocket iş parçacığı hatası: {e}")
    finally:
        for task in asyncio.all_tasks(loop=loop):
            task.cancel()
        
        loop.run_until_complete(asyncio.sleep(0.1))

        if not loop.is_closed():
            loop.close()
        web_server_logger.info("WebSocket olay döngüsü kapatıldı.")

class SuppressLogRequests(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

class LogViewerHTTPRequestHandler(SuppressLogRequests):
    def do_GET(self):
        if self.path == '/get_log_files':
            self.list_log_files()
        elif self.path.startswith('/download/'):
            parts = self.path.split('/')
            if len(parts) >= 4:
                subdir = parts[2]
                filename = '/'.join(parts[3:])
                self.download_file(subdir, filename)
            else:
                self.send_error(400, "Geçersiz indirme yolu formatı.")
        elif self.path == '/':
            self.send_gui_html()
        else:
            super().do_GET()

    def do_POST(self):
        global main_app_logger_instance
        if self.path == '/clear_logs':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                clear_target = data.get('target', 'all')

                if main_app_logger_instance:
                    main_app_logger_instance.clear_handlers(clear_target)
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'status': 'success', 'message': f'Loglar {clear_target} hedeften temizlendi.'}).encode('utf-8'))
                else:
                    self.send_error(500, "Ana loglayıcı örneği mevcut değil.")
                    web_server_logger.error("Ana loglayıcı örneği mevcut değil, temizleme işlemi yapılamadı.")

            except json.JSONDecodeError:
                self.send_error(400, "Geçersiz JSON verisi.")
                web_server_logger.error("Log temizleme isteği için geçersiz JSON verisi.")
            except Exception as e:
                self.send_error(500, f"Logları temizlerken hata oluştu: {e}")
                web_server_logger.error(f"Logları temizlerken hata oluştu: {e}")
        elif self.path == '/delete_logs_by_ext':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                extension = data.get('extension')
                
                if extension == 'all_files':
                    deleted_count = self.delete_all_log_files()
                    message = f"{deleted_count} adet tüm uzantılı log dosyası silindi."
                elif extension:
                    deleted_count = self.delete_logs_by_extension(extension)
                    message = f"{deleted_count} adet .{extension} uzantılı dosya silindi."
                else:
                    self.send_error(400, "Geçersiz istek: Uzantı belirtilmedi.")
                    web_server_logger.error("Geçersiz istek: Silinecek uzantı belirtilmedi.")
                    return

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'success', 'message': message}).encode('utf-8'))
            except json.JSONDecodeError:
                self.send_error(400, "Geçersiz JSON verisi.")
                web_server_logger.error("Log silme isteği için geçersiz JSON verisi.")
            except Exception as e:
                self.send_error(500, f"Logları silerken hata oluştu: {e}")
                web_server_logger.error(f"Logları silerken hata oluştu: {e}")
        else:
            self.send_error(404, "Desteklenmeyen POST isteği.")

    def list_log_files(self):
        log_files = []
        for subdir, _, files in os.walk(LOGS_BASE_DIR):
            relative_subdir = os.path.relpath(subdir, LOGS_BASE_DIR)
            prefix = "" if relative_subdir == "." else f"{relative_subdir}/"
            for file in files:
                log_files.append(f"{prefix}{file}")
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(log_files).encode('utf-8'))
        web_server_logger.info(f"Log dosyaları listelendi. İstemci: {self.client_address}")

    def download_file(self, subdir, filename):
        file_path = os.path.join(LOGS_BASE_DIR, quote(subdir, safe=''), quote(filename, safe=''))
        
        try:
            if not os.path.exists(file_path):
                self.send_error(404, f"Dosya bulunamadı: {file_path}")
                web_server_logger.error(f"İndirme isteği için dosya bulunamadı: {file_path}")
                return

            self.send_response(200)
            content_type = 'application/octet-stream'
            if filename.endswith('.txt') or filename.endswith('.log'):
                content_type = 'text/plain'
            elif filename.endswith('.db'):
                content_type = 'application/x-sqlite3'
            elif filename.endswith('.zip'):
                content_type = 'application/zip'
            self.send_header("Content-type", content_type)
            self.send_header("Content-Disposition", f"attachment; filename=\"{os.path.basename(filename)}\"")
            self.end_headers()
            with open(file_path, 'rb') as f:
                self.wfile.write(f.read())
            web_server_logger.info(f"'{os.path.basename(filename)}' dosyası indirildi. İstemci: {self.client_address}")
        except Exception as e:
            self.send_error(500, f"Dosya indirme hatası: {e}")
            web_server_logger.error(f"Dosya indirilirken hata oluştu: {e}")

    def delete_logs_by_extension(self, extension):
        deleted_count = 0
        for subdir, _, files in os.walk(LOGS_BASE_DIR):
            for file in files:
                if file.endswith(f".{extension}"):
                    file_path = os.path.join(subdir, file)
                    try:
                        os.remove(file_path)
                        deleted_count += 1
                        if web_server_logger:
                            web_server_logger.info(f"Silinen dosya: {file_path}")
                    except Exception as e:
                        if web_server_logger:
                            web_server_logger.error(f"Dosya silinirken hata: {file_path} - {e}")
                        print(f"Hata: {file_path} silinirken bir sorun oluştu: {e}")
        return deleted_count

    def delete_all_log_files(self):
        deleted_count = 0
        for subdir, _, files in os.walk(LOGS_BASE_DIR):
            for file in files:
                file_path = os.path.join(subdir, file)
                try:
                    os.remove(file_path)
                    deleted_count += 1
                    if web_server_logger:
                        web_server_logger.info(f"Silinen dosya (tümü): {file_path}")
                except Exception as e:
                    if web_server_logger:
                        web_server_logger.error(f"Dosya silinirken hata (tümü): {file_path} - {e}")
                    print(f"Hata: {file_path} silinirken bir sorun oluştu: {e}")
        return deleted_count

    def send_gui_html(self):
        try:
            with open(WEB_GUI_HTML_PATH, 'r', encoding='utf-8') as f:
                html_content = f.read()
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html_content.encode('utf-8'))
            web_server_logger.info(f"Kök dizin isteği işlendi. '{WEB_GUI_HTML_PATH}' gönderildi. İstemci: {self.client_address}")
        except FileNotFoundError:
            self.send_error(404, f"Web GUI dosyası bulunamadı: {WEB_GUI_HTML_PATH}")
            web_server_logger.critical(f"Web GUI dosyası bulunamadı: {WEB_GUI_HTML_PATH}. Lütfen bu dosyanın '{BASE_DIR}' dizininde olduğundan emin olun.")
        except Exception as e:
            self.send_error(500, f"Web GUI dosyasını okurken hata oluştu: {e}")
            web_server_logger.error(f"Web GUI dosyası okunurken hata oluştu: {e}")

def _start_http_server_internal():
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("", WEB_SERVER_PORT), LogViewerHTTPRequestHandler)
    
    web_server_logger.info(f"HTTP Sunucusu http://localhost:{WEB_SERVER_PORT} adresinde çalışıyor...")
    
    http_server_thread = threading.Thread(target=httpd.serve_forever)
    http_server_thread.daemon = True
    http_server_thread.start()
    return httpd

def stop_logger_gui_servers():
    global _http_server_instance, _websocket_thread, _websocket_event_loop, _gui_initialized, web_server_logger

    if not _gui_initialized:
        return

    if _http_server_instance:
        print("HTTP sunucusu kapatılıyor...")
        _http_server_instance.shutdown()
        if web_server_logger:
            web_server_logger.info("HTTP sunucusu kapatıldı.")
        _http_server_instance = None
    
    if _websocket_event_loop:
        print("Web Soketi sunucusu kapatılıyor...")
        for task in asyncio.all_tasks(loop=_websocket_event_loop):
            task.cancel()
        
        if _websocket_event_loop.is_running():
            try:
                _websocket_event_loop.run_until_complete(
                    asyncio.gather(*asyncio.all_tasks(loop=_websocket_event_loop), return_exceptions=True)
                )
            except Exception as e:
                if web_server_logger:
                    web_server_logger.error(f"Kapanışta görevleri beklerken hata: {e}")
            
            if _websocket_event_loop.is_running():
                _websocket_event_loop.stop()
            
            if _websocket_thread and _websocket_thread.is_alive():
                _websocket_thread.join(timeout=5)
                if _websocket_thread.is_alive():
                    if web_server_logger:
                        web_server_logger.warning("Uyarı: WebSocket iş parçacığı zaman aşımına uğradı, zorla sonlandırılıyor.")
            
            if web_server_logger:
                web_server_logger.info("Web Soketi sunucusu kapatıldı.")
            
            if _websocket_event_loop and not _websocket_event_loop.is_closed():
                _websocket_event_loop.close()
            _websocket_event_loop = None
            _websocket_thread = None
    
    _gui_initialized = False

def _start_logger_gui_servers_internal(logger_instance_for_gui):
    global _http_server_instance, _websocket_thread, _websocket_event_loop, _gui_initialized, web_server_logger, main_app_logger_instance

    if not _gui_initialized and logger_instance_for_gui.gui_enabled:
        main_app_logger_instance = logger_instance_for_gui

        _websocket_event_loop = asyncio.new_event_loop()
        
        _http_server_instance = _start_http_server_internal()
        
        _websocket_thread = threading.Thread(target=_run_websocket_server_in_thread, args=(_websocket_event_loop,), daemon=True)
        _websocket_thread.start()
        
        time.sleep(1)
        print(f"Web GUI'ye erişmek için tarayıcınızda http://localhost:{WEB_SERVER_PORT} adresini açın.")
        print(f"Gerçek zamanlı loglar için web soketi ws://localhost:{WEBSOCKET_PORT} adresinde çalışıyor.")
        _gui_initialized = True
    else:
        if web_server_logger:
             web_server_logger.debug("GUI sunucuları zaten başlatılmış veya GUI modu etkin değil.")


async def _start_websocket_server_async_coroutine():
    web_server_logger.info(f"Web Soketi Sunucusu ws://localhost:{WEBSOCKET_PORT} adresinde başlatılıyor...")
    
    asyncio.create_task(broadcast_logs_to_clients())
    
    try:
        server = await websockets.serve(websocket_server_start_handler, "localhost", WEBSOCKET_PORT)
        web_server_logger.info(f"WebSockets sunucusu ws://localhost:{WEBSOCKET_PORT} adresinde çalışıyor.")
        await server.wait_closed()
    except asyncio.CancelledError:
        web_server_logger.info("WebSocket sunucusu başlatma görevi iptal edildi.")
    except Exception as e:
        web_server_logger.critical(f"WebSocket sunucusu başlatılırken kritik hata: {e}")
    finally:
        pass

def run_application_logic():
    global main_app_logger_instance

    main_app_logger_instance = Logger(name="MainApp", level="DEBUG", gui=True)
    main_app_logger_instance.add_handler(ConsoleHandler(level="DEBUG"))
    main_app_logger_instance.add_handler(FileHandler("application", level="DEBUG"))
    main_app_logger_instance.add_handler(DatabaseHandler("my_app_logs", level="DEBUG", formatter=Formatter("[%(timestamp)s][%(name)s] - %(level)s - %(message)s")))

    main_app_logger_instance.info("Uygulama başlatılıyor.")
    if main_app_logger_instance.gui_enabled:
        main_app_logger_instance.info("Web GUI ve gerçek zamanlı log akışı etkin.")
    else:
        main_app_logger_instance.info("Web GUI devre dışı. Sadece konsol ve dosya loglaması.")

    for i in range(10):
        main_app_logger_instance.debug(f"Döngü adımı: {i+1} - Rastgele veri: {os.urandom(4).hex()}")
        if i % 3 == 0:
            main_app_logger_instance.info(f"İşlem {i+1} başarıyla tamamlandı.")
        elif i % 5 == 0:
            main_app_logger_instance.warning(f"Sistem kaynağı kullanımı kritik seviyeye yaklaşıyor.")
        elif i == 7:
            try:
                result = 10 / 0
                main_app_logger_instance.info(f"Hesaplama sonucu: {result}")
            except ZeroDivisionError:
                main_app_logger_instance.error("Hata: Sıfıra bölme işlemi tespit edildi!")
        time.sleep(0.5)

    main_app_logger_instance.critical("Uygulama temel işlevlerini tamamladı. Kapatılıyor.")
    if web_server_logger:
        web_server_logger.info("Uygulama mantığı tamamlandı.")


if __name__ == "__main__":
    if web_server_logger is None:
        web_server_logger = Logger(name="WebServerInitGlobal", level="INFO")
        if not os.path.exists(LOGS_BASE_DIR):
            os.makedirs(LOGS_BASE_DIR)
        web_server_logger.add_handler(FileHandler("web_server_global", level="INFO"))
        web_server_logger.info("Global WebServerInitGlobal logger başlatıldı.")

    run_application_logic()

    try:
        print("Web GUI açık. Kapatmak için Ctrl+C'ye basabilirsiniz.")
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nUygulama kullanıcı tarafından sonlandırıldı.")
    except Exception as e:
        if web_server_logger:
            web_server_logger.critical(f"Uygulamada beklenmeyen hata oluştu: {e}")
        print(f"Uygulamada beklenmeyen hata oluştu: {e}")
    finally:
        if main_app_logger_instance:
            main_app_logger_instance.close()
        stop_logger_gui_servers()
        if web_server_logger:
            web_server_logger.close()
        print("Tüm kaynaklar temizlendi. Çıkılıyor.")