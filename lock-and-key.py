################################################################################
# Lock&Key Password Manager                                                    #
################################################################################
# Version: 1.0                                                                 #
# Open-source, self-managed, and self-hosted                                   #
#                                                                              #
# Created by - Ludvik Kristoffersen                                            #
#                                                                              #
# Copyright 2024 Ludvik Kristoffersen                                          #
################################################################################

################################################################################
#                                                                              #
#                               Importing modules                              #
#                                                                              #
################################################################################

# 1. Fernet used for encrypting and decrypting passwords before storage.
# 2. Pillow used for importing and handling images in the application.
# 3. MySQL connector used for connecting and interacting with the MySQL database.
# 4. Customtkinter used for creating the application interface.
# 5. Platform used for OS type detection.
# 6. Argon2 used for creating a secure key for encryption and decryption.
# 7. Random used for randomly selecting characters for password generating.
# 8. String used for easily getting lowercase, uppercase, and digit characters.
# 9. Socket used for testing the connection of the user supplied IP address.
# 10. Base64 used for encoding the Argon2 generated key into base64.
# 11. Time used for creating small time delays between some actions.
# 12. OS used for mainly checking for if files exist or not.
# 13. RE used for creating regex to be used to check user input.
from cryptography.fernet import Fernet
from PIL import Image
import mysql.connector
import customtkinter
import platform
import argon2
import random
import string
import socket
import base64
import time
import sys
import os
import re

################################################################################
#                                                                              #
#                                  OS detection                                #
#                                                                              #
################################################################################

# Getting the OS type the user is currently on, used to determine various decisions.
os_name = platform.system()

# Based on the OS used, Python determines the absolute paths for the installation
# folder, this is how we are able to locate not only the executable but also the
# images, and the other files used in the script.
if os_name == "Windows":
    def resource_path(relative_path):
        try:
            base_path = sys._MEIPASS2
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
elif os_name == "Linux":
    def resource_path(relative_path):
        try:
            base_path = sys._MEIPASS2
        except Exception:
            base_path = os.path.abspath("/opt")
        if relative_path.endswith((".json", ".txt")):
            return os.path.join(base_path, "lock-and-key", relative_path)
        elif relative_path.endswith(".png"):
            return os.path.join(base_path, "lock-and-key", ".images", relative_path)


# Based on the OS type we are importing images from the ".images" folder,
# and saving these images as variables to be used later in the script.
if os_name == "Windows":
    logo_image_dark = customtkinter.CTkImage(dark_image=Image.open(resource_path(".images\\lock-and-key-darkmode.png")), size=(165,39))
    logo_image_light = customtkinter.CTkImage(light_image=Image.open(resource_path(".images\\lock-and-key-lightmode.png")), size=(165,39))
    information_image_light = customtkinter.CTkImage(light_image=Image.open(resource_path(".images\\info-button-lightmode.png")), size=(24,24))
    information_image_dark = customtkinter.CTkImage(dark_image=Image.open(resource_path(".images\\info-button-darkmode.png")), size=(24,24))
    dark_mode_image = customtkinter.CTkImage(light_image=Image.open(resource_path(".images\\light-mode.png")), size=(24,24))
    light_mode_image = customtkinter.CTkImage(dark_image=Image.open(resource_path(".images\\dark-mode.png")), size=(24,24))
    exit_image_light = customtkinter.CTkImage(light_image=Image.open(resource_path(".images\\exit-button-lightmode.png")), size=(24,24))
    exit_image_dark = customtkinter.CTkImage(dark_image=Image.open(resource_path(".images\\exit-button-darkmode.png")), size=(24,24))
    title_bar_logo_dark = customtkinter.CTkImage(dark_image=Image.open(resource_path(".images\\lock-and-key-titlebar-white.png")), size=(20,20))
    title_bar_logo_light = customtkinter.CTkImage(dark_image=Image.open(resource_path(".images\\lock-and-key-titlebar-dark.png")), size=(20,20))
elif os_name == "Linux":
    logo_image_dark = customtkinter.CTkImage(dark_image=Image.open(resource_path("lock-and-key-darkmode.png")), size=(165,39))
    logo_image_light = customtkinter.CTkImage(light_image=Image.open(resource_path("lock-and-key-lightmode.png")), size=(165,39))
    information_image_light = customtkinter.CTkImage(light_image=Image.open(resource_path("info-button-lightmode.png")), size=(24,24))
    information_image_dark = customtkinter.CTkImage(dark_image=Image.open(resource_path("info-button-darkmode.png")), size=(24,24))
    dark_mode_image = customtkinter.CTkImage(light_image=Image.open(resource_path("light-mode.png")), size=(24,24))
    light_mode_image = customtkinter.CTkImage(dark_image=Image.open(resource_path("dark-mode.png")), size=(24,24))
    exit_image_light = customtkinter.CTkImage(light_image=Image.open(resource_path("exit-button-lightmode.png")), size=(24,24))
    exit_image_dark = customtkinter.CTkImage(dark_image=Image.open(resource_path("exit-button-darkmode.png")), size=(24,24))
    title_bar_logo_dark = customtkinter.CTkImage(dark_image=Image.open(resource_path("lock-and-key-titlebar-white.png")), size=(20,20))
    title_bar_logo_light = customtkinter.CTkImage(dark_image=Image.open(resource_path("lock-and-key-titlebar-dark.png")), size=(20,20))

################################################################################
#                                                                              #
#                           Application color control                          #
#                                                                              #
################################################################################

# Setting the default appearance mode of the application to the custom JSON
# theme, and setting the default appearance mode to being dark. Also setting
# the error message color, and succeed message color.
customtkinter.set_default_color_theme(resource_path(".app-theme.json"))
error_color = "#E63946"
succeed_color = "#3A3DFD"
appearance_mode = "dark"

# A function for getting the saved appearance mode on application startup,
# and then configuring the color for the title bar based on the appearance mode.
def get_color():
    global appearance_mode
    if os.path.isfile(resource_path(".appearance-mode.txt")):
        with open(resource_path(".appearance-mode.txt"), "r") as file:
            appearance_mode = file.readline().strip()
            file.close()
        if appearance_mode == "dark":
            customtkinter.set_appearance_mode("light")
            title_bar.configure(fg_color="#eaeaff", bg_color="#eaeaff")
            title_bar_close_button.configure(fg_color="#b5b3de", bg_color="#b5b3de", text_color="#0B0B12", hover_color="#a3a0e2")
            title_bar_logo_label.configure(image=title_bar_logo_light)
            appearance_mode = "dark"
        elif appearance_mode == "light":
            customtkinter.set_appearance_mode("dark")
            title_bar.configure(fg_color="#2c2c46", bg_color="#2c2c46")
            title_bar_close_button.configure(fg_color="#0B0B12", bg_color="#0B0B12", text_color="#DAD9FC", hover_color="#19192d")
            title_bar_logo_label.configure(image=title_bar_logo_dark)
            appearance_mode = "light"
        else:
            customtkinter.set_appearance_mode("dark")
            title_bar.configure(fg_color="#2c2c46", bg_color="#2c2c46")
            title_bar_close_button.configure(fg_color="#0B0B12", bg_color="#0B0B12", text_color="#DAD9FC", hover_color="#19192d")
            title_bar_logo_label.configure(image=title_bar_logo_dark)
            appearance_mode = "light"
            with open(resource_path(".appearance-mode.txt"), "w") as file:
                file.write("light")
                file.close()
    else:
        with open(resource_path(".appearance-mode.txt"), "x") as file:
            file.close()
        with open(resource_path(".appearance-mode.txt"), "w") as file:
            file.write("light")
            file.close()
        with open(resource_path(".appearance-mode.txt"), "r") as file:
            appearance_mode = file.readline()
            file.close()
        if appearance_mode == "light":
            customtkinter.set_appearance_mode("dark")
            title_bar.configure(fg_color="#2c2c46", bg_color="#2c2c46")
            title_bar_close_button.configure(fg_color="#0B0B12", bg_color="#0B0B12", text_color="#DAD9FC", hover_color="#19192d")
            appearance_mode = "light"
        else:
            customtkinter.set_appearance_mode("dark")
            title_bar.configure(fg_color="#2c2c46", bg_color="#2c2c46")
            title_bar_close_button.configure(fg_color="#0B0B12", bg_color="#0B0B12", text_color="#DAD9FC", hover_color="#19192d")
            appearance_mode = "light"

# This function is for triggering the a UI change once the user changes
# the appearance mode within the application, it is also changing the
# colors of objects that might have changed during application usage.
def ui_change():
    if appearance_mode == "dark":
        button_change_appearance.configure(image=light_mode_image)
        button_home.configure(image=information_image_light)
        button_exit_application.configure(image=exit_image_light)
        logo_label.configure(image=logo_image_light)
        right_frame.configure(fg_color="#DAD9FC", bg_color="#DAD9FC")
        title_bar.configure(fg_color="#eaeaff", bg_color="#eaeaff")
        title_bar_close_button.configure(fg_color="#b5b3de", bg_color="#b5b3de", text_color="#0B0B12", hover_color="#a3a0e2")
        title_bar_logo_label.configure(image=title_bar_logo_light)
        try:
            password_strength_slider.configure(progress_color="#DAD9FC", button_color="#DAD9FC", button_hover_color="#DAD9FC")
            password_strength_updater(None)
        except:
            pass
        customtkinter.set_appearance_mode("light")
    elif appearance_mode == "light":
        button_change_appearance.configure(image=dark_mode_image)
        button_home.configure(image=information_image_dark)
        button_exit_application.configure(image=exit_image_dark)
        logo_label.configure(image=logo_image_dark)
        right_frame.configure(fg_color="#11111C", bg_color="#11111C")
        title_bar.configure(fg_color="#2c2c46", bg_color="#2c2c46")
        title_bar_close_button.configure(fg_color="#0B0B12", bg_color="#0B0B12", text_color="#DAD9FC", hover_color="#19192d")
        title_bar_logo_label.configure(image=title_bar_logo_dark)
        try:
            password_strength_slider.configure(progress_color="#11111C", button_color="#11111C", button_hover_color="#11111C")
            password_strength_updater(None)
        except:
            pass
        customtkinter.set_appearance_mode("dark")
    else:
        button_change_appearance.configure(image=dark_mode_image)
        button_home.configure(image=information_image_dark)
        button_exit_application.configure(image=exit_image_dark)
        logo_label.configure(image=logo_image_dark)
        right_frame.configure(fg_color="#11111C", bg_color="#11111C")
        title_bar.configure(fg_color="#2c2c46", bg_color="#2c2c46")
        title_bar_close_button.configure(fg_color="#0B0B12", bg_color="#0B0B12", text_color="#DAD9FC", hover_color="#19192d")
        title_bar_logo_label.configure(image=title_bar_logo_dark)
        try:
            password_strength_slider.configure(progress_color="#11111C", button_color="#11111C", button_hover_color="#11111C")
            password_strength_updater(None)
        except:
            pass
        customtkinter.set_appearance_mode("dark")

# This is the function that changes the appearance mode based on user interaction
# during runtime.
def change_appearance_mode():
    global appearance_mode
    if appearance_mode == "dark":
        appearance_mode = "light"
        with open(resource_path(".appearance-mode.txt"), "w") as file:
            file.write("light")
            file.close()
        ui_change()
    else:
        appearance_mode = "dark"
        with open(resource_path(".appearance-mode.txt"), "w") as file:
            file.write("dark")
            file.close()
        ui_change()

################################################################################
#                                                                              #
#                               Minor functions                                #
#                                                                              #
################################################################################

# Creating some regex's that determine what the user is allowed to type
# in the various input fields, checks if the user has used characters that 
# is not allowed.
username_regex = r"^[A-Za-z0-9_.@\-]+$"
password_regex = r"^[A-Za-z0-9!@#$%^&*]+$"
folder_regex = r"^[A-Za-z0-9]+$"

# Function for removing the objects in the right frame, used to reset the
# right frame by removing the contents that is in place, used at the start in
# every main function.
def remove_right_objects():
    for widget in right_frame.winfo_children():
        widget.destroy()

# Function for removing the objects in the sidebar frame, used to reset the
# sidebar frame by removing the contents that is in place.
def remove_sidebar_objects():
    for widget in login_frame.winfo_children():
        widget.destroy()

# Functions for letting the user click and drag on the custom title bar to
# move it around on the screen. 
def get_position(event):
    global x_pos, y_pos
    x_pos = event.x
    y_pos = event.y
    
def move_application(event):
    x = event.x_root - x_pos
    y = event.y_root - y_pos
    root.geometry(f"+{x}+{y}")

# This function is used to exit the application, it closes the current
# database connection and the database cursor and then safely exists 
# the application.
def exit_application():
    try:
        if cursor and connection:
            cursor.close()
            connection.close()
            time.sleep(1)
            root.quit()
            sys.exit()
        else:
            root.quit()
            sys.exit()
    except:
        time.sleep(1)
        root.quit()
        sys.exit()

################################################################################
#                                                                              #
#                          Password strength check                             #
#                                                                              #
################################################################################

# This function calculates the score based on if the user meets the requirements
# listed below, these requirements follow the guidelines found on this website
# https://www.cmu.edu/iso/governance/guidelines/password-management.html
# but has been modified to make the requirements stronger.
def password_score_calculation(password):
    password_score = 0

    if len(password) >= 20:
        password_score += 1
    if re.search(r"[a-z]", password):
        password_score += 1
    if re.search(r"(?:[A-Z].*?){1,}", password):
        password_score += 1
    if re.search(r"(?:[0-9].*?){3,}", password):
        password_score += 1
    if re.search(r"(?:[!@#$%^&*].*?){3,}", password):
        password_score += 1
    return password_score

# This function updates the password strength checker based on teh score
# calculated in the previous function. This let's the user see exactly
# how weak or strong the password entered is.
def password_strength_updater(event):
    entered_password = password_entry.get()
    overall_score = password_score_calculation(entered_password)
    if overall_score == 0:
        password_strength_label.configure(text="")
        if appearance_mode == "light":
            password_strength_slider.configure(progress_color="#11111C", button_color="#11111C", button_hover_color="#11111C")
        elif appearance_mode == "dark":
            password_strength_slider.configure(progress_color="#DAD9FC", button_color="#DAD9FC", button_hover_color="#DAD9FC")
        else:
            password_strength_slider.configure(progress_color="#11111C", button_color="#11111C", button_hover_color="#11111C")
    elif overall_score <= 2:
        password_strength_label.configure(text="Weak")
        password_strength_slider.configure(progress_color="#E63946", button_color="#E63946", button_hover_color="#E63946")
    elif overall_score <= 4:
        password_strength_label.configure(text="Good")
        password_strength_slider.configure(progress_color="#ffa100", button_color="#ffa100", button_hover_color="#ffa100")
    elif overall_score <= 6:
        password_strength_label.configure(text="Strong")
        password_strength_slider.configure(progress_color="#3A3DFD", button_color="#3A3DFD", button_hover_color="#3A3DFD")
    else:
        password_strength_label.configure(text="")
    password_strength_slider.set(overall_score)

################################################################################
#                                                                              #
#                                Home screen                                   #
#                                                                              #
################################################################################

# This function creates the home screen, this is the first screen the user sees
# once they have authenticated themselves. The home screen provides a short
# description of the password manager, and also lists the functionality provided
# by this password manager.
def home_screen():
    remove_right_objects()
    description_title_label = customtkinter.CTkLabel(right_frame, text="Description", font=customtkinter.CTkFont(size=20, weight="bold"))
    description_title_label.grid(row=0, column=0, padx=20, pady=(20,5), sticky="w")

    description_text = customtkinter.CTkTextbox(right_frame, width=550, height=50, font=customtkinter.CTkFont(size=13), wrap="word")
    description_text.grid(row=1, column=0, padx=20, sticky="w")
    description_text.insert("end", "Lock&Key is a self-hosted, self-managed, open-source password manager. It provides everything you need for storing and managing your accounts securely!")
    description_text.configure(state="disabled")

    functionalities_label = customtkinter.CTkLabel(right_frame, text="Provided Functionalities", font=customtkinter.CTkFont(size=20, weight="bold"))
    functionalities_label.grid(row=2, column=0, padx=20, pady=(5,5), sticky="w")

    functionalities_text = customtkinter.CTkTextbox(right_frame, width=550, height=200, font=customtkinter.CTkFont(size=13), wrap="word")
    functionalities_text.grid(row=3, column=0, padx=20, sticky="w")
    functionalities_text.insert("end", """• Adding account entries: Create new or add existing account entries.\n
• Updating account entries: Modify account entries with new information.\n
• Deleting account entries: Remove unwanted account entries.\n
• Listing account entries: Display a list of all or specified account entries.\n
• Password generation: Generate random, complex passwords.\n
• Encryption: Data securely stored with encryption.""")
    functionalities_text.configure(state="disabled")

################################################################################
#                                                                              #
#                                Adding entry                                  #
#                                                                              #
################################################################################

# This is one of the main functionalities provided by the password manager, this
# function lets the user add a new password entry into the database. 
def adding_entry():
    # Calls the function to remove what is currently in the right frame.
    remove_right_objects()

    global username_entry, folder_entry, folder_menu, password_entry, password_strength_label, password_strength_slider

    add_entry_label = customtkinter.CTkLabel(right_frame, text="Add Entry", font=customtkinter.CTkFont(size=15, weight="bold"))
    add_entry_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")

    username_label = customtkinter.CTkLabel(right_frame, text="Username:")
    username_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
    username_entry = customtkinter.CTkEntry(right_frame)
    username_entry.grid(row=1, column=0, padx=100, pady=10, sticky="w")
    
    # Function for showing the entered password.
    def toggle_password_show():
        if password_show.get():
            password_entry.configure(show="")
        else:
            password_entry.configure(show="*")
    
    password_label = customtkinter.CTkLabel(right_frame, text="Password:")
    password_label.grid(row=2, column=0, padx=20, pady=(10,0), sticky="w")
    password_entry = customtkinter.CTkEntry(right_frame, show="*")
    password_entry.grid(row=2, column=0, padx=100, pady=(10,0), sticky="w")
    # Bind that triggers the password strength checker on key release.
    password_entry.bind("<KeyRelease>", password_strength_updater)
    password_strength_slider = customtkinter.CTkSlider(right_frame, from_=0, to=6, number_of_steps=6, width=115, height=5)
    password_strength_slider.grid(row=3, column=0, padx=(100,0), pady=0, sticky="w")

    if appearance_mode == "light":
        password_strength_slider.configure(progress_color="#11111C")
    elif appearance_mode == "dark":
        password_strength_slider.configure(progress_color="#DAD9FC")
    else:
        password_strength_slider.configure(progress_color="#11111C")

    password_strength_slider.configure(state="disabled")
    password_strength_slider.set(0)
    password_strength_label = customtkinter.CTkLabel(right_frame, text="", font=customtkinter.CTkFont(size=11))
    password_strength_label.grid(row=3, column=0, padx=(205,0), pady=0, sticky="w")

    password_show = customtkinter.CTkCheckBox(right_frame, text="Show password", command=toggle_password_show)
    password_show.grid(row=2, column=1, pady=(10,0), sticky="w")

    # MySQL query that retrieves all the folders from the vault.
    cursor.execute("SELECT folder FROM vault ORDER BY folder")
    rows = cursor.fetchall()
    folder_list = [row[0] for row in rows]
    unique_set = set(folder_list)
    unique_list = list(unique_set)
    if "None" in unique_list:
        unique_list.remove("None")
    else:
        pass

    folder_label = customtkinter.CTkLabel(right_frame, text="Folder:")
    folder_label.grid(row=4, column=0, padx=20, pady=(0,10), sticky="w")
    folder_entry = customtkinter.CTkEntry(right_frame)
    folder_entry.grid(row=4, column=0, padx=100, pady=(0,10), sticky="w")
    folder_menu = customtkinter.CTkOptionMenu(right_frame, values=["None"]+unique_list)
    folder_menu.grid(row=4, column=1, pady=(0,10), sticky="w")
    
    # Function for adding the new entry into the database, it checks if the username,
    # password, and folder matches their respective regex patterns. Passwords are
    # encrypted, and that encrypted value is stored in the database.
    def add_database_entry():
        try:
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            folder = folder_entry.get().strip()
            folder_select = folder_menu.get()
            
            if len(username) > 0 and len(password) > 0:
                message_label.configure(text="")
                if re.match(username_regex,username):
                    message_label.configure(text="")
                    if re.match(password_regex,password):
                        message_label.configure(text="")
                        encode_password = password.encode()
                        encrypt_password = cipher_instance.encrypt(encode_password)
                        decoded_encrypted_password = encrypt_password.decode()
                        if len(folder) > 0:
                            message_label.configure(text="")
                            if re.match(folder_regex,folder):
                                cursor.execute(f'INSERT INTO vault (username, password, folder) VALUES ("{username}","{decoded_encrypted_password}","{folder}");')
                                connection.commit()
                                message_label.configure(text="New entry added.", text_color=succeed_color)
                                username_entry.delete(0, 'end')
                                password_entry.delete(0, 'end')
                                folder_entry.delete(0, 'end')
                                password_strength_updater(None)
                            else:
                                message_label.configure(text="Folder invalid.", text_color=error_color)
                        else:
                            message_label.configure(text="")
                            cursor.execute(f'INSERT INTO vault (username, password, folder) VALUES ("{username}","{decoded_encrypted_password}","{folder_select}");')
                            connection.commit()
                            message_label.configure(text="New entry added.", text_color=succeed_color)
                            username_entry.delete(0, 'end')
                            password_entry.delete(0, 'end')
                            folder_entry.delete(0, 'end')
                            password_strength_updater(None)
                    else:
                        message_label.configure(text="Password invalid.", text_color=error_color)
                else:
                    message_label.configure(text="Username invalid.", text_color=error_color)
            else:
                message_label.configure(text="Username or password cannot be empty.", text_color=error_color)
        except mysql.connector.Error:
            message_label.configure(text="Failed to add new entry.", text_color=error_color)

    add_button = customtkinter.CTkButton(right_frame, text="Add Entry", command=add_database_entry)
    add_button.grid(row=5, column=0, padx=20, pady=10, sticky="w")
    
    # This function provides the user with the possibility to generate a random strong password
    # that must be in the 25-255 character limit. The randomly generated password must create
    # a strong password each time, meaning if must match the requirements for the password
    # strength checker.
    def generate_random_password():
        try:
            password_length = int(password_char_length.get())
            if password_length < 25:
                message_label.configure(text="Password character length to short.", text_color=error_color)
            elif password_length > 255:
                message_label.configure(text="Password character length to long.", text_color=error_color)
            else:
                message_label.configure(text="")
                password_entry.delete(0, "end")
                lowercase = string.ascii_lowercase
                uppercase = string.ascii_uppercase
                numbers = string.digits
                special_char = "!@#$%^&*"
                combined_char_list = lowercase+uppercase+numbers+special_char
                random_password = "".join(random.choices(combined_char_list, k=password_length))
                if any(char in lowercase for char in random_password) and any(char in uppercase for char in random_password) \
                    and sum(char in numbers for char in random_password) >= 3 and sum(char in special_char for char in random_password) >= 3: 
                    password_entry.insert(0, random_password)
                else:
                    generate_random_password()
                password_strength_updater(None)
        except:
            message_label.configure(text="Password character length not valid.", text_color=error_color)
    
    password_char_length = customtkinter.CTkEntry(right_frame, placeholder_text="25-255", width=60, justify="center")
    password_char_length.grid(row=5, column=2, padx=10, pady=10, sticky="w")
    password_char_length.insert(0, "50")

    generate_password_button = customtkinter.CTkButton(right_frame, text="Generate Password", command=generate_random_password)
    generate_password_button.grid(row=5, column=1, pady=10, sticky="w")

    message_label = customtkinter.CTkLabel(right_frame, text="")
    message_label.grid(row=6, column=0, padx=20, pady=10, sticky="w")

################################################################################
#                                                                              #
#                               Updating entry                                 #
#                                                                              #
################################################################################

# This is one of the main functionalities provided by the password manager, this
# function lets the user update any entries that are already stored in the
# password manager.
def updating_entry():
    # Calls the function to remove what is currently in the right frame.
    remove_right_objects()

    global updating_list
    update_entry_label = customtkinter.CTkLabel(right_frame, text="Update Entry", font=customtkinter.CTkFont(size=15, weight="bold"))
    update_entry_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")

    # MySQL query that retrieves all the folders from the vault which is used
    # for displaying all entries or only specified entries.
    cursor.execute("SELECT folder FROM vault ORDER BY folder")
    rows = cursor.fetchall()
    folder_list = [row[0] for row in rows]
    unique_set = set(folder_list)
    unique_list = list(unique_set)

    folder_menu = customtkinter.CTkOptionMenu(right_frame, values=["All"]+unique_list)
    folder_menu.grid(row=1, column=0, padx=20, pady=0, sticky="w")

    scrollable_frame = customtkinter.CTkScrollableFrame(right_frame, width=550, height=235, corner_radius=6)
    scrollable_frame.grid(row=3, column=0, padx=(20, 0), pady=(10, 0), sticky="nsew")
    scrollable_frame.grid_columnconfigure(0, weight=1)

    # Function that retrieves all entries currently stored in the password manager,
    # but it does not retrieve the password.
    def updating_list():
        if folder_menu.get() == "All":
            cursor.execute("SELECT id, username, folder FROM vault ORDER BY folder;")
        else:
            cursor.execute(f"SELECT id, username, folder FROM vault WHERE folder='{folder_menu.get()}' ORDER BY folder;")
        entries = cursor.fetchall()

        for widget in scrollable_frame.winfo_children():
            widget.destroy()

        entry_id = 3
        for entry in entries:
            title_username_label = customtkinter.CTkLabel(scrollable_frame, text="Username", font=customtkinter.CTkFont(size=13, weight="bold"))
            title_username_label.grid(row=2, column=0, padx=0, pady=5, sticky="w")
            title_folder_label = customtkinter.CTkLabel(scrollable_frame, text="Folder", font=customtkinter.CTkFont(size=13, weight="bold"))
            title_folder_label.grid(row=2, column=1, padx=(5,40), pady=5, sticky="w")

            username_label = customtkinter.CTkLabel(scrollable_frame, text=f"{entry[1]}")
            username_label.grid(row=entry_id, column=0, padx=0, pady=5, sticky="w")

            folder_label = customtkinter.CTkLabel(scrollable_frame, text=f"{entry[2]}")
            folder_label.grid(row=entry_id, column=1, padx=(5,40), pady=5, sticky="w")

            row_id = entry[0]
            username = entry[1]
            folder = entry[2]

            select_entry_button = customtkinter.CTkButton(scrollable_frame, text="Select")
            select_entry_button.grid(row=entry_id, column=2, padx=(5,0), pady=5, sticky="w")
            select_entry_button.configure(command=lambda r=row_id, u=username, f=folder: updating_entry_button(r,u,f))
            entry_id += 1

    # When a user selects a entry they want to edit or update in any way, they get
    # brought to the same screen used to create a new entry, but the username
    # and folder is already filled in, indicating that the user is updating a 
    # entry. The password does not show, if the password is not changed then the
    # currently stored password will not change, but if it is changed then the 
    # password will update.         
    def updating_entry_button(row_id, username, folder):
        global password_entry, password_strength_label, password_strength_slider
        remove_right_objects()
    
        update_entry_label = customtkinter.CTkLabel(right_frame, text="Update Entry", font=customtkinter.CTkFont(size=15, weight="bold"))
        update_entry_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")
    
        username_label = customtkinter.CTkLabel(right_frame, text="Username:")
        username_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        username_entry = customtkinter.CTkEntry(right_frame)
        username_entry.grid(row=1, column=0, padx=100, pady=10, sticky="w")
        username_entry.insert(0, username)
        
        # Function for showing the entered password.
        def toggle_password_show():
            if password_show.get():
                password_entry.configure(show="")
            else:
                password_entry.configure(show="*")
    
        password_label = customtkinter.CTkLabel(right_frame, text="Password:")
        password_label.grid(row=2, column=0, padx=20, pady=(10,0), sticky="w")
        password_entry = customtkinter.CTkEntry(right_frame, show="*")
        password_entry.grid(row=2, column=0, padx=100, pady=(10,0), sticky="w")
        # Bind that triggers the password strength checker on key release.
        password_entry.bind("<KeyRelease>", password_strength_updater)
        password_strength_slider = customtkinter.CTkSlider(right_frame, from_=0, to=6, number_of_steps=6, width=115, height=5)
        password_strength_slider.grid(row=3, column=0, padx=(100,0), pady=0, sticky="w")

        if appearance_mode == "light":
            password_strength_slider.configure(progress_color="#11111C")
        elif appearance_mode == "dark":
            password_strength_slider.configure(progress_color="#DAD9FC")
        else:
            password_strength_slider.configure(progress_color="#11111C")

        password_strength_slider.configure(state="disabled")
        password_strength_slider.set(0)
        password_strength_label = customtkinter.CTkLabel(right_frame, text="", font=customtkinter.CTkFont(size=11))
        password_strength_label.grid(row=3, column=0, padx=(205,0), pady=0, sticky="w")

        password_show = customtkinter.CTkCheckBox(right_frame, text="Show password", command=toggle_password_show)
        password_show.grid(row=2, column=1, pady=(10,0), sticky="w")
        
        # MySQL query that retrieves all the folders from the vault.
        cursor.execute("SELECT folder FROM vault ORDER BY folder")
        rows = cursor.fetchall()
        folder_list = [row[0] for row in rows]
        unique_set = set(folder_list)
        unique_list = list(unique_set)
        if "None" in unique_list:
            unique_list.remove("None")
        else:
            pass
        
        folder_label = customtkinter.CTkLabel(right_frame, text="Folder:")
        folder_label.grid(row=4, column=0, padx=20, pady=(0,10), sticky="w")
        folder_entry = customtkinter.CTkEntry(right_frame)
        folder_entry.grid(row=4, column=0, padx=100, pady=(0,10), sticky="w")
        folder_entry.insert(0, folder)
        folder_menu = customtkinter.CTkOptionMenu(right_frame, values=["None"]+unique_list)
        folder_menu.grid(row=4, column=1, padx=0, pady=(0,10))

        # Function that updates the selected entry. It checks if anything has been changed
        # if not then nothing will be updated, all inputs are also being run through the
        # regex specified earlier to hinder the user from entering characters that might
        # break the back end query made. The user can choose to update one or multiple
        # things, new passwords are also encrypted before being stored in the database.
        def confirm_update():
            new_username = username_entry.get().strip()
            password = password_entry.get().strip()
            folder_length = folder_entry.get().strip()
            new_folder = folder_entry.get().strip()

            if len(new_username) > 0:
                message_label.configure(text="")
                if re.match(username_regex,new_username):
                    message_label.configure(text="")
                    if len(password) == 0 or re.match(password_regex,password):
                        message_label.configure(text="")
                        if len(new_folder) == 0 or re.match(folder_regex,new_folder):
                            message_label.configure(text="")
                            if len(password) != 0:
                                encode_password = password.encode()
                                encrypt_password = cipher_instance.encrypt(encode_password)
                                decoded_encrypted_password = encrypt_password.decode()

                            if new_username != username and len(password) != 0 and new_folder != folder:
                                if len(folder_length) == 0:
                                    cursor.execute(f"UPDATE vault SET username='{new_username}', password='{decoded_encrypted_password}', folder='{folder_menu.get()}' WHERE id={int(row_id)}")
                                    connection.commit()
                                    password_strength_updater(None)
                                    updating_entry()
                                else:
                                    cursor.execute(f"UPDATE vault SET username='{new_username}', password='{decoded_encrypted_password}', folder='{new_folder}' WHERE id={int(row_id)}")
                                    connection.commit()
                                    password_strength_updater(None)
                                    updating_entry()
                            elif new_username != username and len(password) != 0:
                                cursor.execute(f"UPDATE vault SET username='{new_username}', password='{decoded_encrypted_password}' WHERE id={int(row_id)}")
                                connection.commit()
                                password_strength_updater(None)
                                updating_entry()
                            elif new_username != username and new_folder != folder:
                                if len(folder_length) == 0:
                                    cursor.execute(f"UPDATE vault SET username='{new_username}', folder='{folder_menu.get()}' WHERE id={int(row_id)}")
                                    connection.commit()
                                    password_strength_updater(None)
                                    updating_entry()
                                else:
                                    cursor.execute(f"UPDATE vault SET username='{new_username}', folder='{new_folder}' WHERE id={int(row_id)}")
                                    connection.commit()
                                    password_strength_updater(None)
                                    updating_entry()
                            elif len(password) != 0 and new_folder != folder:
                                if len(folder_length) == 0:
                                    cursor.execute(f"UPDATE vault SET password='{decoded_encrypted_password}', folder='{folder_menu.get()}' WHERE id={int(row_id)}")
                                    connection.commit()
                                    password_strength_updater(None)
                                    updating_entry()
                                else:
                                    cursor.execute(f"UPDATE vault SET username='{decoded_encrypted_password}', folder='{new_folder}' WHERE id={int(row_id)}")
                                    connection.commit()
                                    password_strength_updater(None)
                                    updating_entry()
                            elif new_username != username:
                                cursor.execute(f"UPDATE vault SET username='{new_username}' WHERE id={int(row_id)}")
                                connection.commit()
                                password_strength_updater(None)
                                updating_entry()
                            elif len(password) != 0:
                                cursor.execute(f"UPDATE vault SET password='{decoded_encrypted_password}' WHERE id={int(row_id)}")
                                connection.commit()
                                password_strength_updater(None)
                                updating_entry()
                            elif new_folder != folder:
                                if len(folder_length) == 0:
                                    cursor.execute(f"UPDATE vault SET folder='{folder_menu.get()}' WHERE id={int(row_id)}")
                                    connection.commit()
                                    password_strength_updater(None)
                                    updating_entry()
                                else:
                                    cursor.execute(f"UPDATE vault SET folder='{new_folder}' WHERE id={int(row_id)}")
                                    connection.commit()
                                    password_strength_updater(None)
                                    updating_entry()
                            else:
                                message_label.configure(text="Nothing has been changed!", text_color=error_color)
                        else:
                            message_label.configure(text="Folder invalid.", text_color=error_color) 
                    else:
                        message_label.configure(text="Password invalid.", text_color=error_color)
                else:
                    message_label.configure(text="Username invalid.", text_color=error_color)
            else:
                message_label.configure(text="Username cannot be empty.", text_color=error_color)
        
        # Function for letting the user cancel the current update, brings the user
        # back to the selection screen.
        def cancel_update():
            password_strength_updater(None)
            remove_right_objects()
            updating_entry()

        confirm_update_button = customtkinter.CTkButton(right_frame, text="Update", command=confirm_update, width=60)
        confirm_update_button.grid(row=5, column=0, padx=20, pady=10, sticky="w")
        cancel_update_button = customtkinter.CTkButton(right_frame, text="Cancel", command=cancel_update, width=60)
        cancel_update_button.grid(row=5, column=0, padx=90, pady=10, sticky="w")

        # This function provides the user with the possibility to generate a random strong password
        # that must be in the 25-255 character limit. The randomly generated password must create
        # a strong password each time, meaning if must match the requirements for the password
        # strength checker.
        def generate_random_password():
            try:
                password_length = int(password_char_length.get())
                if password_length < 25:
                    message_label.configure(text="Password character length to short.", text_color=error_color)
                elif password_length > 255:
                    message_label.configure(text="Password character length to long.", text_color=error_color)
                else:
                    message_label.configure(text="")
                    password_entry.delete(0, "end")
                    lowercase = string.ascii_lowercase
                    uppercase = string.ascii_uppercase
                    numbers = string.digits
                    special_char = "!@#$%^&*"
                    combined_char_list = lowercase+uppercase+numbers+special_char
                    random_password = "".join(random.choices(combined_char_list, k=password_length))
                    if any(char in lowercase for char in random_password) and any(char in uppercase for char in random_password) \
                        and sum(char in numbers for char in random_password) >= 3 and sum(char in special_char for char in random_password) >= 3: 
                        password_entry.insert(0, random_password)
                    else:
                        generate_random_password()
                    password_strength_updater(None)
            except:
                message_label.configure(text="Password character length not valid.", text_color=error_color)
    
        password_char_length = customtkinter.CTkEntry(right_frame, placeholder_text="25-255", width=60, justify="center")
        password_char_length.grid(row=5, column=2, padx=10, pady=10, sticky="w")
        password_char_length.insert(0, "50")

        generate_password_button = customtkinter.CTkButton(right_frame, text="Generate Password", command=generate_random_password)
        generate_password_button.grid(row=5, column=1, pady=10, sticky="w")

        message_label = customtkinter.CTkLabel(right_frame, text="")
        message_label.grid(row=6, column=0, padx=20, pady=10, sticky="w")
    
    # Calls the updating list function immediately to update the current list of entries.
    updating_list()

    update_entries_button = customtkinter.CTkButton(right_frame, text="Search", command=updating_list, width=60)
    update_entries_button.grid(row=1, column=0, padx=180, pady=0, sticky="w")

################################################################################
#                                                                              #
#                               Deleting entry                                 #
#                                                                              #
################################################################################

# This is one of the main functionalities provided by the password manager, this
# function lets the user delete entries in the password manager.
def deleting_entry():
    # Calls the function to remove what is currently in the right frame.
    remove_right_objects()

    delete_entry_label = customtkinter.CTkLabel(right_frame, text="Delete Entry", font=customtkinter.CTkFont(size=15, weight="bold"))
    delete_entry_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")

    # MySQL query that retrieves all the folders from the vault which is used
    # for displaying all entries or only specified entries.
    cursor.execute("SELECT folder FROM vault ORDER BY folder")
    rows = cursor.fetchall()
    folder_list = [row[0] for row in rows]
    unique_set = set(folder_list)
    unique_list = list(unique_set)

    folder_menu = customtkinter.CTkOptionMenu(right_frame, values=["All"]+unique_list)
    folder_menu.grid(row=1, column=0, padx=20, pady=0, sticky="w")

    scrollable_frame = customtkinter.CTkScrollableFrame(right_frame, width=550, height=235, corner_radius=6)
    scrollable_frame.grid(row=3, column=0, padx=(20, 0), pady=(10, 0), sticky="nsew")
    scrollable_frame.grid_columnconfigure(0, weight=1)

    # Clicking the delete button on one of the entries in the list
    # will bring up a confirmation screen where the user can confirm
    # the deletion or decline the deletion.
    def delete_entry_button(row_id):
        remove_right_objects()
        delete_entry_label = customtkinter.CTkLabel(right_frame, text="Delete Entry", font=customtkinter.CTkFont(size=15, weight="bold"))
        delete_entry_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")
        warning_label = customtkinter.CTkLabel(right_frame, text="Deletion of entries are final, are you sure?")
        warning_label.grid(row=1, column=0, padx=20, pady=5, sticky="w")
        
        # This function is run when the user confirms the deletion, this will
        # delete the entry from the database.
        def confirm_deletion():
            cursor.execute(f"DELETE FROM vault WHERE id={int(row_id)}")
            connection.commit()
            deleting_entry()
        confirm_deletion_button = customtkinter.CTkButton(right_frame, text="Yes", command=confirm_deletion, width=50, fg_color=error_color, hover_color="#CC323F", text_color="#0B0B12")
        confirm_deletion_button.grid(row=2, column=0, padx=20, pady=5, sticky="w")
        regret_deletion_button = customtkinter.CTkButton(right_frame, text="No", command=deleting_entry, width=50)
        regret_deletion_button.grid(row=2, column=0, padx=90, pady=5, sticky="w")

    # Function that retrieves all entries currently stored in the password manager,
    # but it does not retrieve the password.
    def updating_list():
        if folder_menu.get() == "All":
            cursor.execute("SELECT id, username, folder FROM vault ORDER BY folder;")
        else:
            cursor.execute(f"SELECT id, username, folder FROM vault WHERE folder='{folder_menu.get()}' ORDER BY folder;")
        entries = cursor.fetchall()

        for widget in scrollable_frame.winfo_children():
            widget.destroy()

        entry_id = 3
        for entry in entries:
            title_username_label = customtkinter.CTkLabel(scrollable_frame, text="Username", font=customtkinter.CTkFont(size=13, weight="bold"))
            title_username_label.grid(row=2, column=0, padx=0, pady=5, sticky="w")
            title_folder_label = customtkinter.CTkLabel(scrollable_frame, text="Folder", font=customtkinter.CTkFont(size=13, weight="bold"))
            title_folder_label.grid(row=2, column=1, padx=(5,40), pady=5, sticky="w")

            username_label = customtkinter.CTkLabel(scrollable_frame, text=f"{entry[1]}")
            username_label.grid(row=entry_id, column=0, padx=0, pady=5, sticky="w")

            folder_label = customtkinter.CTkLabel(scrollable_frame, text=f"{entry[2]}")
            folder_label.grid(row=entry_id, column=1, padx=(5,40), pady=5, sticky="w")

            row_id = entry[0]

            remove_button = customtkinter.CTkButton(scrollable_frame, text="Delete", fg_color=error_color, hover_color="#CC323F", text_color="#0B0B12")
            remove_button.grid(row=entry_id, column=2, padx=(5,0), pady=5, sticky="w")
            remove_button.configure(command=lambda r=row_id: delete_entry_button(r))
            entry_id += 1

    # Calls the updating list function immediately to update the current list of entries.
    updating_list()

    update_entries_button = customtkinter.CTkButton(right_frame, text="Search", command=updating_list, width=60)
    update_entries_button.grid(row=1, column=0, padx=180, pady=0, sticky="w")

################################################################################
#                                                                              #
#                               Listing entries                                #
#                                                                              #
################################################################################

# This is one of the main functionalities provided by the password manager, this
# function lets the user list all or specified entries and let's the user copy
# password for any stored entry in the database.
def listing_entries():
    # Calls the function to remove what is currently in the right frame.
    remove_right_objects()

    global scrollable_frame

    list_entry_label = customtkinter.CTkLabel(right_frame, text="Listing Entries", font=customtkinter.CTkFont(size=15, weight="bold"))
    list_entry_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")

    # MySQL query that retrieves all the folders from the vault which is used
    # for displaying all entries or only specified entries.
    cursor.execute("SELECT folder FROM vault ORDER BY folder")
    rows = cursor.fetchall()
    folder_list = [row[0] for row in rows]
    unique_set = set(folder_list)
    unique_list = list(unique_set)

    folder_menu = customtkinter.CTkOptionMenu(right_frame, values=["All"]+unique_list)
    folder_menu.grid(row=1, column=0, padx=20, pady=0, sticky="w")

    scrollable_frame = customtkinter.CTkScrollableFrame(right_frame, width=550, height=235, corner_radius=6)
    scrollable_frame.grid(row=3, column=0, padx=(20, 0), pady=(10, 0), sticky="nsew")
    scrollable_frame.grid_columnconfigure(0, weight=1)

    # Passwords are not shown in plain text, the plain text password is stored between a
    # copy button which the user can press to copy that plain text password. This is done
    # for security reasons, no one in your surrounding's should be able to see the users
    # plain text passwords.
    def copy_to_clipboard(password, button):
        root.clipboard_clear()
        root.clipboard_append(password)
        if appearance_mode == "light":
            button.configure(text="Copied!", fg_color="#DAD9FC", hover_color="#DAD9FC", text_color="#0B0B12")
            scrollable_frame.after(2000, lambda: button.configure(text="Copy Pass", fg_color="#262639", hover_color="#30303F", text_color="#DAD9FC"))
        elif appearance_mode == "dark":
            button.configure(text="Copied!", fg_color="#0B0B12", hover_color="#0B0B12", text_color="#DAD9FC")
            scrollable_frame.after(2000, lambda: button.configure(text="Copy Pass", fg_color="#918ebc", hover_color="#7a77a9", text_color="#0B0B12"))
        else:
            button.configure(text="Copied!", fg_color="#DAD9FC", hover_color="#DAD9FC", text_color="#0B0B12")
            scrollable_frame.after(2000, lambda: button.configure(text="Copy Pass", fg_color="#262639", hover_color="#30303F", text_color="#DAD9FC"))

    # Function that retrieves all entries currently stored in the password manager,
    # but it does not retrieve the password.
    def updating_list():
        global copy_button
        if folder_menu.get() == "All":
            cursor.execute("SELECT username, password, folder FROM vault ORDER BY folder;")
        else:
            cursor.execute(f"SELECT username, password, folder FROM vault WHERE folder='{folder_menu.get()}' ORDER BY folder;")
        entries = cursor.fetchall()

        for widget in scrollable_frame.winfo_children():
            widget.destroy()

        entry_id = 3
        for entry in entries:
            title_username_label = customtkinter.CTkLabel(scrollable_frame, text="Username", font=customtkinter.CTkFont(size=13, weight="bold"))
            title_username_label.grid(row=2, column=0, padx=0, pady=5, sticky="w")
            title_folder_label = customtkinter.CTkLabel(scrollable_frame, text="Folder", font=customtkinter.CTkFont(size=13, weight="bold"))
            title_folder_label.grid(row=2, column=1, padx=(5,40), pady=5, sticky="w")
            title_password_label = customtkinter.CTkLabel(scrollable_frame, text="Password", font=customtkinter.CTkFont(size=13, weight="bold"))
            title_password_label.grid(row=2, column=2, padx=(5,0), pady=5, sticky="w")

            username_label = customtkinter.CTkLabel(scrollable_frame, text=f"{entry[0]}")
            username_label.grid(row=entry_id, column=0, padx=0, pady=5, sticky="w")

            folder_label = customtkinter.CTkLabel(scrollable_frame, text=f"{entry[2]}")
            folder_label.grid(row=entry_id, column=1, padx=(5,40), pady=5, sticky="w")

            password = entry[1]
            encode_password = password.encode()
            decrypted_password = cipher_instance.decrypt(encode_password)

            copy_button = customtkinter.CTkButton(scrollable_frame, text="Copy Pass")
            copy_button.grid(row=entry_id, column=2, padx=(5,0), pady=5, sticky="w")
            copy_button.configure(command=lambda p=decrypted_password, b=copy_button: copy_to_clipboard(p, b))
            entry_id += 1

    # Calls the updating list function immediately to update the current list of entries.
    updating_list()

    update_entries_button = customtkinter.CTkButton(right_frame, text="Search", command=updating_list, width=60)
    update_entries_button.grid(row=1, column=0, padx=180, pady=0, sticky="w")

################################################################################
#                                                                              #
#                               Main function                                  #
#                                                                              #
################################################################################

# This function powers the whole application, it has a button to trigger each of
# functions listed above, as well as buttons for changing appearance mode, and 
# quitting the application.
def main():
    # Calls the function to remove what is currently in the sidebar.
    remove_sidebar_objects()

    global right_frame, sidebar_frame, cipher_instance, button_change_appearance, button_home, button_exit_application, logo_label, title_bar, title_bar_close_button, title_bar_logo_label
    
    # Creates the database and the needed tables if they do not already exist.
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS lockandkey_{username}")
    cursor.execute(f"USE lockandkey_{username}")
    cursor.execute("CREATE TABLE IF NOT EXISTS vault (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(200) NOT NULL, password VARCHAR(1000) NOT NULL, folder VARCHAR(50) DEFAULT 'None')")
    cursor.execute("CREATE TABLE IF NOT EXISTS user (id INT AUTO_INCREMENT PRIMARY KEY, salt VARCHAR(50) NOT NULL)")
    connection.commit()

    # Retrieves the salt from the user table.
    cursor.execute("SELECT salt FROM user")
    retrieved_salt = cursor.fetchone()
    # If the salt exist then use that salt, but if no salt is present
    # create a randomly generated 50 character salt for the user.
    if retrieved_salt is not None:
        salt = retrieved_salt[0].encode()
    else:
        letters = [char for char in string.ascii_letters]
        digits = [char for char in string.digits]
        special_char = ["!","@","#","$","%","^","&","*"]
        combined_char_list = letters+digits+special_char
        random_salt = "".join(random.choices(combined_char_list, k=50))
        store_salt = random_salt
        salt = random_salt.encode()
        cursor.execute(f"INSERT INTO user (salt) VALUES ('{store_salt}')")
        connection.commit()

    # This function generates a key based on the users master password and user salt.
    # The key is then shortened to 32 characters and encoded with base64 to work with Ferent.
    def key_derivation_function(master_password, salt):
        kdf = argon2.PasswordHasher()
        hash_the_key = kdf.hash(master_password, salt=salt)
        key_length = hash_the_key[:32]
        key = base64.urlsafe_b64encode(key_length.encode()).decode()
        return key
    # Calls the KDF function and creates the cipher_instance with the generated key.
    # This cipher instance is now used for encryption and decryption.
    key = key_derivation_function(master_password.encode(),salt)
    cipher_instance = Fernet(key)

    root.geometry(f"{818}x{400}")

    # Removes the system title bar based on the current OS.
    if os_name == "Windows":
        root.overrideredirect(True)
    elif os_name == "Linux":
        root.attributes("-type", "splash")
    else:
        sys.exit()

    root.grid_columnconfigure(0, weight=0)
    root.grid_columnconfigure(1, weight=1)
    root.grid_rowconfigure(0, weight=0)
    root.grid_rowconfigure(1, weight=1)

    # Creates the custom title bar.
    title_bar = customtkinter.CTkFrame(root, height=5)
    title_bar.grid(row=0, column=0, columnspan=2, sticky="ew")

    title_bar.grid_columnconfigure(0, weight=1)
    title_bar.grid_columnconfigure(1, weight=0)

    title_bar_logo_label = customtkinter.CTkLabel(title_bar, text="", image=title_bar_logo_dark)
    title_bar_logo_label.grid(row=0, column=0, padx=5, sticky="w")

    title_bar_title = customtkinter.CTkLabel(title_bar, text="Lock&Key - Password Manager", font=customtkinter.CTkFont("bold"))
    title_bar_title.grid(row=0, column=0, padx=27, sticky="w")

    title_bar_close_button = customtkinter.CTkButton(title_bar, text="✕", width=20, height=5, command=exit_application)
    title_bar_close_button.grid(row=0, column=1, padx=5, sticky="e")
    # Binds to trigger the functions for clicking and dragging the task bar.
    title_bar.bind("<Button-1>", get_position)
    title_bar.bind("<B1-Motion>", move_application)

    title_bar.tkraise()
    # Creates the sidebar frame, creates buttons for all the provided functionalities. 
    sidebar_frame = customtkinter.CTkFrame(root, width=300)
    sidebar_frame.grid(row=1, column=0, rowspan=6, sticky="nsew")
    sidebar_frame.grid_rowconfigure(6, weight=1)

    logo_label = customtkinter.CTkLabel(sidebar_frame, text="", image=logo_image_dark)
    logo_label.grid(row=0, column=0, padx=(20,0), pady=(20, 10), sticky="w")

    button_adding_entry = customtkinter.CTkButton(sidebar_frame, text="Add", command=adding_entry, font=customtkinter.CTkFont(weight="bold"), width=165)
    button_adding_entry.grid(row=1, column=0, padx=(20,0), pady=10, sticky="w")

    button_updating_entry = customtkinter.CTkButton(sidebar_frame, text="Update", command=updating_entry, font=customtkinter.CTkFont(weight="bold"), width=165)
    button_updating_entry.grid(row=2, column=0, padx=(20,0), pady=10, sticky="w")

    button_deleting_entry = customtkinter.CTkButton(sidebar_frame, text="Delete", command=deleting_entry, font=customtkinter.CTkFont(weight="bold"), width=165)
    button_deleting_entry.grid(row=3, column=0, padx=(20,0), pady=10, sticky="w")

    button_listing_entries = customtkinter.CTkButton(sidebar_frame, text="List", command=listing_entries, font=customtkinter.CTkFont(weight="bold"), width=165)
    button_listing_entries.grid(row=4, column=0, padx=(20,0), pady=10, sticky="w")

    button_home = customtkinter.CTkButton(sidebar_frame, text="", image=information_image_dark, command=home_screen, font=customtkinter.CTkFont(weight="bold"), width=30, height=30)
    button_home.grid(row=6, column=0, padx=(32,0), pady=10, sticky="w")

    button_change_appearance = customtkinter.CTkButton(sidebar_frame, text="", image=dark_mode_image, command=change_appearance_mode, font=customtkinter.CTkFont(weight="bold"), width=30, height=30)
    button_change_appearance.grid(row=6, column=0, padx=(82,0), pady=10, sticky="w")

    button_exit_application = customtkinter.CTkButton(sidebar_frame, text="", image=exit_image_dark, command=exit_application, font=customtkinter.CTkFont(weight="bold"), width=30, height=30)
    button_exit_application.grid(row=6, column=0, padx=(132,0), pady=10, sticky="w")

    right_frame = customtkinter.CTkFrame(root)
    right_frame.grid(row=1, column=1, columnspan=2, rowspan=5, sticky="nsew")

    # Calls the home screen function to show the home screen on startup
    # Also calling the ui change function to update the UI based on the
    # current appearance theme.
    home_screen()
    root.focus_force()
    ui_change()

################################################################################
#                                                                              #
#                               Login function                                 #
#                                                                              #
################################################################################

# This function authenticates the user with the MySQL server, uses the MySQL
# password as the master password for the password manager.
def login():
    global root, login_frame, login_failure_message_label, title_bar, title_bar_close_button, title_bar_logo_label

    root = customtkinter.CTk()
    root.geometry(f"{225}x{310}")
    root.title("Login")
    root.resizable(False, False)

    # Removes the system title bar based on the current OS.
    if os_name == "Windows":
        root.overrideredirect(True)
    elif os_name == "Linux":
        root.attributes("-type", "splash")
    else:
        root.quit()
        sys.exit()

    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=1)

    # Creates the custom title bar.
    title_bar = customtkinter.CTkFrame(root, height=5, fg_color="#11111C")
    title_bar.grid(row=0, column=0, sticky="ew")

    title_bar.grid_columnconfigure(0, weight=1)
    title_bar.grid_columnconfigure(1, weight=0)

    title_bar_logo_label = customtkinter.CTkLabel(title_bar, text="", image=title_bar_logo_dark)
    title_bar_logo_label.grid(row=0, column=0, padx=5, sticky="w")

    title_bar_title = customtkinter.CTkLabel(title_bar, text="Login", font=customtkinter.CTkFont("bold"))
    title_bar_title.grid(row=0, column=0, padx=27, sticky="w")

    title_bar_close_button = customtkinter.CTkButton(title_bar, text="✕", width=20, height=5, command=exit_application)
    title_bar_close_button.grid(row=0, column=1, padx=5, sticky="e")
    # Binds to trigger the functions for clicking and dragging the task bar.
    title_bar.bind("<Button-1>", get_position)
    title_bar.bind("<B1-Motion>", move_application)

    title_bar.tkraise()

    login_frame = customtkinter.CTkFrame(root)
    login_frame.grid(row=1, column=0, rowspan=6, sticky="nsew")
    login_frame.grid_rowconfigure(6, weight=1)

    main_title_label = customtkinter.CTkLabel(login_frame, text="MySQL Login", font=customtkinter.CTkFont(size=20, weight="bold"))
    main_title_label.grid(row=0, column=0, padx=(20,0), pady=(10,10), sticky="ew")

    host_entry = customtkinter.CTkEntry(login_frame, placeholder_text="MySQL Server IP", width=120)
    host_entry.grid(row=1, column=0, padx=(20,0), pady=5, sticky="w")

    port_entry = customtkinter.CTkEntry(login_frame, placeholder_text="3306", width=58)
    port_entry.grid(row=1, column=0, padx=(145,0), pady=5, sticky="w")

    username_entry = customtkinter.CTkEntry(login_frame, placeholder_text="Username", width=185)
    username_entry.grid(row=2, column=0, padx=(20,0), pady=5, sticky="w")

    password_entry = customtkinter.CTkEntry(login_frame, placeholder_text="Password", show="*", width=185)
    password_entry.grid(row=3, column=0, padx=(20,0), pady=5, sticky="w")

    # Function for creating a document that will store the host and username
    # to provide a remember me functionality so the user does not need to
    # enter the host and username each time they launch the application.
    def remember_me():
        if remember_me_check.get():
            if os.path.isfile(resource_path(".remember_me.txt")):
                pass
            else:
                with open(resource_path(".remember_me.txt"), "x") as file:
                    file.close()
        else:
            if os.path.isfile(resource_path(".remember_me.txt")):
                os.remove(resource_path(".remember_me.txt"))

    # Checkbox that will trigger the remember_me function to trigger once clicked. 
    remember_me_check = customtkinter.CTkCheckBox(login_frame, text="Remember me", command=remember_me)
    remember_me_check.grid(row=4, column=0, padx=(20,0),pady=5, sticky="w")

    # Checks if there is a file called .remember_me.txt, and if this file
    # exists, read the file and place the host, port, and username in their 
    # input fields.
    if os.path.isfile(resource_path(".remember_me.txt")):
        with open(resource_path(".remember_me.txt"), "r") as file:
            line = file.readlines()
            file.close()
        if len(line) > 0:
            remember_me_check.select()
            host_line = line[0].strip()
            port_line = line[1].strip()
            host_entry.insert("end", host_line)
            port_entry.insert("end", port_line)
            username_entry.insert("end", line[2].strip())
        else:
            remember_me_check.deselect()
            port_entry.insert("end", "3306")
            os.remove(resource_path(".remember_me.txt"))
    else:
        port_entry.insert("end", "3306")
    
    # Function for checking if the host entered actually is reachable on the specified port.
    def mysql_server_alive_check(host, port):
        try:
            socket_instance = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_instance.settimeout(4)
            socket_instance.connect((host,port))
            socket_instance.close()
            return True
        except:
            return False

    # Function for authenticating the user to the MySQL server. User input in all fields
    # are run through regex's to make sure the user provides valid input.
    def authentication():
        global connection, cursor, username, master_password

        username = username_entry.get().strip()
        master_password = password_entry.get().strip()
        host = host_entry.get().strip()
        port = port_entry.get().strip()
        host_octet_regex = r"(?!.*(?:\d){4})(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"
        host_regex = rf"{host_octet_regex}\.{host_octet_regex}\.{host_octet_regex}\.{host_octet_regex}$"
        port_regex = r"^[0-9]{1,5}$"
        username_regex = r"^[A-Za-z_.@\-]+$"
        password_regex = r"^[A-Za-z0-9#!@#$^&*.]+$"

        if len(username) != 0 and len(port) != 0 and len(master_password) != 0 and len(host) != 0:
            login_failure_message_label.configure(text="")
            if re.match(host_regex,host):
                login_failure_message_label.configure(text="")
                if re.match(port_regex,port):
                    login_failure_message_label.configure(text="")
                    port = int(port)
                    if port >= 0 and port <= 65535:
                        if re.match(username_regex,username):
                            login_failure_message_label.configure(text="")
                            if re.match(password_regex,master_password):
                                login_failure_message_label.configure(text="")
                                if mysql_server_alive_check(host, port):
                                    login_failure_message_label.configure(text="")
                                    # If the user input pass all the above, it will try to connect to the MySQL server,
                                    # if it succeeds, the user information such as host and username will be stored in
                                    # the .remember_me.txt file and the a connection to the MySQL server will be established.
                                    try:
                                        if os.path.isfile(resource_path(".remember_me.txt")):
                                            with open(resource_path(".remember_me.txt"), "r") as file:
                                                line = file.readlines()
                                                file.close()
                                            if len(line) > 0:
                                                if host != line[0].strip() or port != line[1].strip() or username != line[2].strip():
                                                    with open(resource_path(".remember_me.txt"), "w") as file:
                                                        file.write(f"{host}\n{port}\n{username}")
                                                        file.close()
                                            else:
                                                with open(resource_path(".remember_me.txt"), "w") as file:
                                                    file.write(f"{host}\n{port}\n{username}")
                                                    file.close()
                                        else:
                                            pass

                                        connection = mysql.connector.connect(user=username, password=master_password, host=host, port=port)
                                        cursor = connection.cursor()

                                        # If the connection is established, the main function will be called.
                                        main()
                                    except mysql.connector.Error:
                                        login_failure_message_label.configure(text="Login failed.", text_color=error_color)
                                else:
                                    login_failure_message_label.configure(text="Host unreachable.", text_color=error_color)
                            else:
                                login_failure_message_label.configure(text="Password invalid.", text_color=error_color) 
                        else:
                            login_failure_message_label.configure(text="Username invalid.", text_color=error_color)
                    else:
                        login_failure_message_label.configure(text="Port not in valid range.", text_color=error_color)
                else:
                    login_failure_message_label.configure(text="Port invalid.", text_color=error_color)
            else:
                login_failure_message_label.configure(text="Host invalid.", text_color=error_color)
        else:
            login_failure_message_label.configure(text="Empty fields.", text_color=error_color)

    login_button = customtkinter.CTkButton(login_frame, text="Login", command=authentication, width=185)
    login_button.grid(row=5, column=0, padx=(20,0), pady=5, sticky="w")

    login_failure_message_label = customtkinter.CTkLabel(login_frame, text="")
    login_failure_message_label.grid(row=6, column=0, padx=(20,0), pady=5, sticky="ew")

    # On startup we get the color if the .appearance-mode.txt exists.
    get_color()
    # We force the application to being in focused mode, and we start the main loop of the root object.
    root.focus_force()
    root.mainloop()

# Starts the login function on application startup.
login()