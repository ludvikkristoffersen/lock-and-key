#------------------------------------------------------------------------#
# Lock&Key Password Manager                                              #
#------------------------------------------------------------------------#
# Version: 1.0                                                           #
# Open-source and self-hosted                                            #
#                                                                        #
# created by - Ludvik Kristoffersen                                      #
#________________________________________________________________________#


#---------------------------IMPORTING MODULES-----------------------------
# 1. Cryptography for encrypting and decrypting passwords.
# 2. Pillow for importing and handling images.
# 3. Customtkinter for creating the application interface.
# 4. MySQL connector for connecting and interacting with the MySQL database.
# 5. Random for randomly selecting characters for password generating.
# 6. String for easily getting lowercase, uppercase, and digit characters.
# 7. Socket for testing the connection of the user supplied IP address.
# 8. Base64 for encoding the encryption/decryption key into base64
# 9. Time for creating small time delays between some actions.
# 10. OS for mainly checking for if files exist or not.
# 11. RE for creating regex to be used to check user input.
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet
from PIL import Image
import mysql.connector
import customtkinter
import random
import string
import socket
import base64
import time
import os
import re


#--------------------------------IMAGES----------------------------------
# Importing images from the ".images" folder, and saving these images as
# variables to be used later in the script.
logo_image_dark = customtkinter.CTkImage(dark_image=Image.open(".images/lock-and-key-darkmode.png"), size=(140,34))
logo_image_light = customtkinter.CTkImage(light_image=Image.open(".images/lock-and-key-lightmode.png"), size=(140,34))
information_image_light = customtkinter.CTkImage(light_image=Image.open(".images/info-button-lightmode.png"), size=(24,24))
information_image_dark = customtkinter.CTkImage(dark_image=Image.open(".images/info-button-darkmode.png"), size=(24,24))
dark_mode_image = customtkinter.CTkImage(light_image=Image.open(".images/light-mode.png"), size=(24,24))
light_mode_image = customtkinter.CTkImage(dark_image=Image.open(".images/dark-mode.png"), size=(24,24))
exit_image_light = customtkinter.CTkImage(light_image=Image.open(".images/exit-button-lightmode.png"), size=(24,24))
exit_image_dark = customtkinter.CTkImage(dark_image=Image.open(".images/exit-button-darkmode.png"), size=(24,24))

#---------------------------APPEARANCE MODE-----------------------------
# Setting the default appearance mode of the application to custom JSON
# theme, and setting the default color mode to being dark.
customtkinter.set_default_color_theme(".app-theme.json")
error_color = "#D81E5B"
succeed_color = "#3A3DFD"

appearance_mode = "dark"

def get_color():
    global appearance_mode
    if os.path.isfile(".appearance-mode.txt"):
        with open(".appearance-mode.txt", "r") as file:
            appearance_mode = file.readline().strip()
        if appearance_mode == "dark":
            customtkinter.set_appearance_mode("light")
            appearance_mode = "dark"
        elif appearance_mode == "light":
            customtkinter.set_appearance_mode("dark")
            appearance_mode = "light"
        else:
            customtkinter.set_appearance_mode("dark")
            appearance_mode = "light"
    else:
        with open(".appearance-mode.txt", "x") as file:
            file.close()
        with open(".appearance-mode.txt", "w") as file:
            file.write("light")
            file.close()
        with open(".appearance-mode.txt", "r") as file:
            appearance_mode = file.readline()
            file.close()
        if appearance_mode == "light":
            customtkinter.set_appearance_mode("dark")
            appearance_mode = "light"
        else:
            customtkinter.set_appearance_mode("dark")
            appearance_mode = "light"

#--------------------------------CHANGING COLOR-----------------------------------
# User can change the appearance mode from dark to light mode and vice versa.
def ui_change():
    if appearance_mode == "dark":
        button_change_appearance.configure(image=light_mode_image)
        button_home.configure(image=information_image_light)
        button_exit_application.configure(image=exit_image_light)
        logo_label.configure(image=logo_image_light)
        right_frame.configure(fg_color="#DAD9FC", bg_color="#DAD9FC")
        customtkinter.set_appearance_mode("light")
    elif appearance_mode == "light":
        button_change_appearance.configure(image=dark_mode_image)
        button_home.configure(image=information_image_dark)
        button_exit_application.configure(image=exit_image_dark)
        logo_label.configure(image=logo_image_dark)
        right_frame.configure(fg_color="#11111C", bg_color="#11111C")
        customtkinter.set_appearance_mode("dark")
    else:
        button_change_appearance.configure(image=dark_mode_image)
        button_home.configure(image=information_image_dark)
        button_exit_application.configure(image=exit_image_dark)
        logo_label.configure(image=logo_image_dark)
        right_frame.configure(fg_color="#11111C", bg_color="#11111C")
        customtkinter.set_appearance_mode("dark")

def change_appearance_mode():
    global appearance_mode
    if appearance_mode == "dark":
        appearance_mode = "light"
        with open(".appearance-mode.txt", "w") as file:
            file.write("light")
            file.close()
        ui_change()
    else:
        appearance_mode = "dark"
        with open(".appearance-mode.txt", "w") as file:
            file.write("dark")
            file.close()
        ui_change()

#--------------------------------REGEX-----------------------------------
# Creating some regex's that determine what the user is allowed to type
# in the various input fields, checks if the user has used characters that 
# is not allowed.
username_regex = r"^[A-Za-z0-9_.@\-]+$"
password_regex = r"^[A-Za-z0-9!@#$%^&*]+$"
folder_regex = r"^[A-Za-z0-9]+$"

#----------------------------MINOR FUNCTIONS-----------------------------
# 1. remove_right_objects is used to remove all objects that are currently 
#    present on the right hand side.
# 2. remove_sidebar_objects are used to remove the sidebar objects.
# 3. mysql_server_alive_check is used to check if the user supplied IP
#    address is reachable on port 3306.
def remove_right_objects():
    for widget in right_frame.winfo_children():
        widget.destroy()

def remove_sidebar_objects():
    for widget in login_frame.winfo_children():
        widget.destroy()

def mysql_server_alive_check(host, port=3306):
    try:
        socket_instance = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_instance.settimeout(4)
        socket_instance.connect((host,port))
        socket_instance.close()
        return True
    except:
        return False

#-----------------------------KDF--------------------------
# Used to create a encryption/decryption key from combining
# the master password with a salt created on first runtime
def key_derivation_function(master_password, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000
    )
    key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
    return key

#----------------------------HOME SCREEN------------------------------
# Creating a home screen where the user should be informed of what
# features are in the password manager, also given a short description
# of the password manager itself.
def home_screen():
    remove_right_objects()
    description_title_label = customtkinter.CTkLabel(right_frame, text="Description", font=customtkinter.CTkFont(size=20, weight="bold"))
    description_title_label.grid(row=0, column=0, padx=20, pady=(20,5), sticky="w")

    description_text = customtkinter.CTkTextbox(right_frame, width=550, height=50, font=customtkinter.CTkFont(size=13), wrap="word")
    description_text.grid(row=1, column=0, padx=20, pady=(10,20), sticky="w")
    description_text.insert("end", "Lock&Key is a self-hosted, self-managed, open-source password manager. It provides everything you need for storing and managing your accounts securely!")
    description_text.configure(state="disabled")

    functionalities_label = customtkinter.CTkLabel(right_frame, text="Provided Functionalities", font=customtkinter.CTkFont(size=20, weight="bold"))
    functionalities_label.grid(row=2, column=0, padx=20, pady=5, sticky="w")


    functionalities_text = customtkinter.CTkTextbox(right_frame, width=550, height=200, font=customtkinter.CTkFont(size=13), wrap="word")
    functionalities_text.grid(row=3, column=0, padx=20, pady=5, sticky="w")
    functionalities_text.insert("end", """• Adding account entries: Create new or add existing account entries.\n
• Updating account entries: Modify account entries with new information.\n
• Deleting account entries: Remove unwanted account entries.\n
• Listing account entries: Display a list of all or specified account entries.\n
• Password generation: Generate random, complex passwords.\n
• Encryption: Data securely stored with encryption.""")
    functionalities_text.configure(state="disabled")

#----------------------------ADDING ENTRY-----------------------------
# One of the main functions. This let's the user add a new account entry
# to the database, they can choose to generate a random password in the
# 25-255 character limit, and they can also choose to save this account
# in a group by specifying a folder name.
def adding_entry():
    remove_right_objects()

    add_entry_label = customtkinter.CTkLabel(right_frame, text="Add Entry", font=customtkinter.CTkFont(size=15, weight="bold"))
    add_entry_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")

    username_label = customtkinter.CTkLabel(right_frame, text="Username:")
    username_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
    username_entry = customtkinter.CTkEntry(right_frame)
    username_entry.grid(row=1, column=0, padx=100, pady=10, sticky="w")

    def toggle_password_show():
        if password_show.get():
            password_entry.configure(show="")
        else:
            password_entry.configure(show="*")
    
    password_label = customtkinter.CTkLabel(right_frame, text="Password:")
    password_label.grid(row=2, column=0, padx=20, pady=10, sticky="w")
    password_entry = customtkinter.CTkEntry(right_frame, show="*")
    password_entry.grid(row=2, column=0, padx=100, pady=10, sticky="w")

    password_show = customtkinter.CTkCheckBox(right_frame, text="Show password", command=toggle_password_show)
    password_show.grid(row=2, column=1, pady=10, sticky="w")

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
    folder_label.grid(row=3, column=0, padx=20, pady=10, sticky="w")
    folder_entry = customtkinter.CTkEntry(right_frame)
    folder_entry.grid(row=3, column=0, padx=100, pady=10, sticky="w")
    folder_menu = customtkinter.CTkOptionMenu(right_frame, values=["None"]+unique_list)
    folder_menu.grid(row=3, column=1, pady=10)

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
                    else:
                        message_label.configure(text="Password invalid.", text_color=error_color)
                else:
                    message_label.configure(text="Username invalid.", text_color=error_color)
            else:
                message_label.configure(text="Username or password cannot be empty.", text_color=error_color)
        except mysql.connector.Error:
            message_label.configure(text="Failed to add new entry.", text_color=error_color)

    add_button = customtkinter.CTkButton(right_frame, text="Add Entry", command=add_database_entry)
    add_button.grid(row=4, column=0, padx=20, pady=10, sticky="w")
    
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
                letters = [char for char in string.ascii_letters]
                digits = [char for char in string.digits]
                special_char = ["!","@","#","$","%","^","&","*"]
                combined_char_list = letters+digits+special_char
                random_password = "".join(random.choices(combined_char_list, k=password_length))
                password_entry.insert(0, random_password)
        except:
            message_label.configure(text="Password character length not valid.", text_color=error_color)
    
    password_char_length = customtkinter.CTkEntry(right_frame, placeholder_text="25-255", width=60, justify="center")
    password_char_length.grid(row=4, column=2, padx=10, pady=10, sticky="w")
    password_char_length.insert(0, "50")

    generate_password_button = customtkinter.CTkButton(right_frame, text="Generate Password", command=generate_random_password)
    generate_password_button.grid(row=4, column=1, pady=10, sticky="w")

    message_label = customtkinter.CTkLabel(right_frame, text="")
    message_label.grid(row=5, column=0, padx=20, pady=10, sticky="w")

#----------------------------UPDATING ENTRY---------------------------
# One of the main functions. This let's the user update a entry that is
# already stored in the database, they can change everything or just 
# small parts of the entry such as only the username, password, or folder.
# The user should also be allowed to generate a random password here with
# the same 25-255 range character limit.
def updating_entry():
    remove_right_objects()

    global updating_list
    update_entry_label = customtkinter.CTkLabel(right_frame, text="Update Entry", font=customtkinter.CTkFont(size=15, weight="bold"))
    update_entry_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")

    cursor.execute("SELECT folder FROM vault ORDER BY folder")
    rows = cursor.fetchall()
    folder_list = [row[0] for row in rows]
    unique_set = set(folder_list)
    unique_list = list(unique_set)

    folder_menu = customtkinter.CTkOptionMenu(right_frame, values=["All"]+unique_list)
    folder_menu.grid(row=1, column=0, padx=20, pady=0, sticky="w")

    scrollable_frame = customtkinter.CTkScrollableFrame(right_frame, width=550, height=250)
    scrollable_frame.grid(row=3, column=0, padx=(20, 0), pady=(10, 0), sticky="nsew")
    scrollable_frame.grid_columnconfigure(0, weight=1)

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
            title_username_label = customtkinter.CTkLabel(scrollable_frame, text="Username", font=customtkinter.CTkFont(size=15, weight="bold"))
            title_username_label.grid(row=2, column=0, padx=0, pady=5, sticky="w")
            title_folder_label = customtkinter.CTkLabel(scrollable_frame, text="Folder", font=customtkinter.CTkFont(size=15, weight="bold"))
            title_folder_label.grid(row=2, column=1, padx=20, pady=5, sticky="w")

            username_label = customtkinter.CTkLabel(scrollable_frame, text=f"{entry[1]}")
            username_label.grid(row=entry_id, column=0, padx=0, pady=5, sticky="w")

            folder_label = customtkinter.CTkLabel(scrollable_frame, text=f"{entry[2]}")
            folder_label.grid(row=entry_id, column=1, padx=20, pady=5, sticky="w")

            row_id = entry[0]
            username = entry[1]
            folder = entry[2]

            select_entry_button = customtkinter.CTkButton(scrollable_frame, text="Select")
            select_entry_button.grid(row=entry_id, column=2, padx=5, pady=5, sticky="w")
            select_entry_button.configure(command=lambda r=row_id, u=username, f=folder: updating_entry_button(r,u,f))
            entry_id += 1
            
    def updating_entry_button(row_id, username, folder):
        remove_right_objects()
    
        update_entry_label = customtkinter.CTkLabel(right_frame, text="Update Entry", font=customtkinter.CTkFont(weight="bold"))
        update_entry_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")
    
        username_label = customtkinter.CTkLabel(right_frame, text="Username:")
        username_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        username_entry = customtkinter.CTkEntry(right_frame)
        username_entry.grid(row=1, column=0, padx=100, pady=10, sticky="ew")
        username_entry.insert(0, username)

        def toggle_password_show():
            if password_show.get():
                password_entry.configure(show="")
            else:
                password_entry.configure(show="*")
    
        password_label = customtkinter.CTkLabel(right_frame, text="Password:")
        password_label.grid(row=2, column=0, padx=20, pady=10, sticky="w")
        password_entry = customtkinter.CTkEntry(right_frame, show="*")
        password_entry.grid(row=2, column=0, padx=100, pady=10, sticky="ew")

        password_show = customtkinter.CTkCheckBox(right_frame, text="Show password", command=toggle_password_show)
        password_show.grid(row=2, column=1, pady=10, sticky="w")

        def generate_random_password():
            try:
                password_length = int(password_char_length.get())
                if password_length < 25:
                    message_label.configure(text="Password character length to short.", text_color=error_color)
                elif password_length > 255:
                    message_label.configure(text="Password character length to long.", text_color=error_color)
                else:
                    password_entry.delete(0, "end")
                    letters = [char for char in string.ascii_letters]
                    digits = [char for char in string.digits]
                    special_char = ["!","@","#","$","%","^","&","*"]
                    combined_char_list = letters+digits+special_char
                    random_password = "".join(random.choices(combined_char_list, k=password_length))
                    password_entry.insert(0, random_password)
            except:
                message_label.configure(text="Password character length not valid.", text_color=error_color)
    
        password_char_length = customtkinter.CTkEntry(right_frame, placeholder_text="25-255", width=60, justify="center")
        password_char_length.grid(row=4, column=2, padx=10, pady=10, sticky="w")
        password_char_length.insert(0, "50")

        generate_password_button = customtkinter.CTkButton(right_frame, text="Generate Password", command=generate_random_password)
        generate_password_button.grid(row=4, column=1, pady=10, sticky="w")

        message_label = customtkinter.CTkLabel(right_frame, text="")
        message_label.grid(row=5, column=0, padx=20, pady=10, sticky="w")
    
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
        folder_label.grid(row=3, column=0, padx=20, pady=10, sticky="w")
        folder_entry = customtkinter.CTkEntry(right_frame)
        folder_entry.grid(row=3, column=0, padx=100, pady=10, sticky="ew")
        folder_entry.insert(0, folder)
        folder_menu = customtkinter.CTkOptionMenu(right_frame, values=["None"]+unique_list)
        folder_menu.grid(row=3, column=1, padx=0, pady=10)
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
                                    updating_entry()
                                else:
                                    cursor.execute(f"UPDATE vault SET username='{new_username}', password='{decoded_encrypted_password}', folder='{new_folder}' WHERE id={int(row_id)}")
                                    connection.commit()
                                    updating_entry()
                            elif new_username != username and len(password) != 0:
                                cursor.execute(f"UPDATE vault SET username='{new_username}', password='{decoded_encrypted_password}' WHERE id={int(row_id)}")
                                connection.commit()
                                updating_entry()
                            elif new_username != username and new_folder != folder:
                                if len(folder_length) == 0:
                                    cursor.execute(f"UPDATE vault SET username='{new_username}', folder='{folder_menu.get()}' WHERE id={int(row_id)}")
                                    connection.commit()
                                    updating_entry()
                                else:
                                    cursor.execute(f"UPDATE vault SET username='{new_username}', folder='{new_folder}' WHERE id={int(row_id)}")
                                    connection.commit()
                                    updating_entry()
                            elif len(password) != 0 and new_folder != folder:
                                if len(folder_length) == 0:
                                    cursor.execute(f"UPDATE vault SET password='{decoded_encrypted_password}', folder='{folder_menu.get()}' WHERE id={int(row_id)}")
                                    connection.commit()
                                    updating_entry()
                                else:
                                    cursor.execute(f"UPDATE vault SET username='{decoded_encrypted_password}', folder='{new_folder}' WHERE id={int(row_id)}")
                                    connection.commit()
                                    updating_entry()
                            elif new_username != username:
                                cursor.execute(f"UPDATE vault SET username='{new_username}' WHERE id={int(row_id)}")
                                connection.commit()
                                updating_entry()
                            elif len(password) != 0:
                                cursor.execute(f"UPDATE vault SET password='{decoded_encrypted_password}' WHERE id={int(row_id)}")
                                connection.commit()
                                updating_entry()
                            elif new_folder != folder:
                                if len(folder_length) == 0:
                                    cursor.execute(f"UPDATE vault SET folder='{folder_menu.get()}' WHERE id={int(row_id)}")
                                    connection.commit()
                                    updating_entry()
                                else:
                                    cursor.execute(f"UPDATE vault SET folder='{new_folder}' WHERE id={int(row_id)}")
                                    connection.commit()
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

        def cancel_update():
            remove_right_objects()
            updating_entry()
        confirm_update_button = customtkinter.CTkButton(right_frame, text="Update", command=confirm_update, width=50)
        confirm_update_button.grid(row=4, column=0, padx=20, pady=10, sticky="w")
        cancel_update_button = customtkinter.CTkButton(right_frame, text="Cancel", command=cancel_update, width=50)
        cancel_update_button.grid(row=4, column=0, padx=90, pady=10, sticky="w")
    updating_list()

    update_entries_button = customtkinter.CTkButton(right_frame, text="Search", command=updating_list, width=60)
    update_entries_button.grid(row=1, column=0, padx=180, pady=0, sticky="w")

#----------------------------DELETING ENTRY---------------------------
# One of the main functions. This let's the user delete one or more 
# entries stored in the database. This is not reversible so we must
# notify the user before deleting an entry.
def deleting_entry():
    remove_right_objects()

    global updating_list
    delete_entry_label = customtkinter.CTkLabel(right_frame, text="Delete Entry", font=customtkinter.CTkFont(size=15, weight="bold"))
    delete_entry_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")

    cursor.execute("SELECT folder FROM vault ORDER BY folder")
    rows = cursor.fetchall()
    folder_list = [row[0] for row in rows]
    unique_set = set(folder_list)
    unique_list = list(unique_set)

    folder_menu = customtkinter.CTkOptionMenu(right_frame, values=["All"]+unique_list)
    folder_menu.grid(row=1, column=0, padx=20, pady=0, sticky="w")

    scrollable_frame = customtkinter.CTkScrollableFrame(right_frame, width=550, height=250)
    scrollable_frame.grid(row=3, column=0, padx=(20, 0), pady=(10, 0), sticky="nsew")
    scrollable_frame.grid_columnconfigure(0, weight=1)

    # Function for deleting a entry in the main deleting function
    def delete_entry_button(row_id):
        remove_right_objects()
        delete_entry_label = customtkinter.CTkLabel(right_frame, text="Delete Entry", font=customtkinter.CTkFont(weight="bold"))
        delete_entry_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")
        warning_label = customtkinter.CTkLabel(right_frame, text="Deletion of entries are final, are you sure?")
        warning_label.grid(row=1, column=0, padx=20, pady=5, sticky="w")

        def confirm_deletion():
            cursor.execute(f"DELETE FROM vault WHERE id={int(row_id)}")
            connection.commit()
            deleting_entry()
        confirm_deletion_button = customtkinter.CTkButton(right_frame, text="Yes", command=confirm_deletion, width=50, text_color=error_color)
        confirm_deletion_button.grid(row=2, column=0, padx=20, pady=5, sticky="w")
        regret_deletion_button = customtkinter.CTkButton(right_frame, text="No", command=deleting_entry, width=50)
        regret_deletion_button.grid(row=2, column=0, padx=90, pady=5, sticky="w")

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
            title_username_label = customtkinter.CTkLabel(scrollable_frame, text="Username", font=customtkinter.CTkFont(size=15, weight="bold"))
            title_username_label.grid(row=2, column=0, padx=0, pady=5, sticky="w")
            title_folder_label = customtkinter.CTkLabel(scrollable_frame, text="Folder", font=customtkinter.CTkFont(size=15, weight="bold"))
            title_folder_label.grid(row=2, column=1, padx=20, pady=5, sticky="w")

            username_label = customtkinter.CTkLabel(scrollable_frame, text=f"{entry[1]}")
            username_label.grid(row=entry_id, column=0, padx=0, pady=5, sticky="w")

            folder_label = customtkinter.CTkLabel(scrollable_frame, text=f"{entry[2]}")
            folder_label.grid(row=entry_id, column=1, padx=20, pady=5, sticky="w")

            row_id = entry[0]

            remove_button = customtkinter.CTkButton(scrollable_frame, text="Delete", text_color=error_color)
            remove_button.grid(row=entry_id, column=2, padx=5, pady=5, sticky="w")
            remove_button.configure(command=lambda r=row_id: delete_entry_button(r))
            entry_id += 1

    updating_list()

    update_entries_button = customtkinter.CTkButton(right_frame, text="Search", command=updating_list, width=60)
    update_entries_button.grid(row=1, column=0, padx=180, pady=0, sticky="w")

#----------------------------LISTING ENTRIES--------------------------
# One of the main functions. This let's the user list all or specified
# entries from the database, this is also where the user can copy the 
# password for their accounts directly. Passwords are not shown in
# plaintext for security reasons.
def listing_entries():
    remove_right_objects()
    global scrollable_frame

    list_entry_label = customtkinter.CTkLabel(right_frame, text="Listing Entries", font=customtkinter.CTkFont(size=15, weight="bold"))
    list_entry_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")

    cursor.execute("SELECT folder FROM vault ORDER BY folder")
    rows = cursor.fetchall()
    folder_list = [row[0] for row in rows]
    unique_set = set(folder_list)
    unique_list = list(unique_set)

    folder_menu = customtkinter.CTkOptionMenu(right_frame, values=["All"]+unique_list)
    folder_menu.grid(row=1, column=0, padx=20, pady=0, sticky="w")

    scrollable_frame = customtkinter.CTkScrollableFrame(right_frame, width=550, height=250)
    scrollable_frame.grid(row=3, column=0, padx=(20, 0), pady=(10, 0), sticky="nsew")
    scrollable_frame.grid_columnconfigure(0, weight=1)

    # Function that copies the password from the list entries main function
    def copy_to_clipboard(password, button):
        root.clipboard_clear()
        root.clipboard_append(password)
        button.configure(text="Copied!")
        scrollable_frame.after(2000, lambda: button.configure(text="Copy Pass"))

    def updating_list():
        if folder_menu.get() == "All":
            cursor.execute("SELECT username, password, folder FROM vault ORDER BY folder;")
        else:
            cursor.execute(f"SELECT username, password, folder FROM vault WHERE folder='{folder_menu.get()}' ORDER BY folder;")
        entries = cursor.fetchall()

        for widget in scrollable_frame.winfo_children():
            widget.destroy()

        entry_id = 3
        for entry in entries:
            title_username_label = customtkinter.CTkLabel(scrollable_frame, text="Username", font=customtkinter.CTkFont(size=15, weight="bold"))
            title_username_label.grid(row=2, column=0, padx=0, pady=5, sticky="w")
            title_folder_label = customtkinter.CTkLabel(scrollable_frame, text="Folder", font=customtkinter.CTkFont(size=15, weight="bold"))
            title_folder_label.grid(row=2, column=1, padx=20, pady=5, sticky="w")
            title_password_label = customtkinter.CTkLabel(scrollable_frame, text="Password", font=customtkinter.CTkFont(size=15, weight="bold"))
            title_password_label.grid(row=2, column=2, padx=5, pady=5, sticky="w")

            username_label = customtkinter.CTkLabel(scrollable_frame, text=f"{entry[0]}")
            username_label.grid(row=entry_id, column=0, padx=0, pady=5, sticky="w")

            folder_label = customtkinter.CTkLabel(scrollable_frame, text=f"{entry[2]}")
            folder_label.grid(row=entry_id, column=1, padx=20, pady=5, sticky="w")

            password = entry[1]
            encode_password = password.encode()
            decrypted_password = cipher_instance.decrypt(encode_password)

            copy_button = customtkinter.CTkButton(scrollable_frame, text="Copy Pass")
            copy_button.grid(row=entry_id, column=2, padx=5, pady=5, sticky="w")
            copy_button.configure(command=lambda p=decrypted_password, b=copy_button: copy_to_clipboard(p, b))
            entry_id += 1

    updating_list()

    update_entries_button = customtkinter.CTkButton(right_frame, text="Search", command=updating_list, width=60)
    update_entries_button.grid(row=1, column=0, padx=180, pady=0, sticky="w")

#----------------------------EXIT APPLICATION-------------------------
# Simply let's the user exit the application.
def exit_application():
    cursor.close()
    connection.close()
    time.sleep(1)
    quit()

#-----------------------------MAIN FUNCTION---------------------------
# The main function powers all the functions above by creating buttons
# that call these functions when clicked.
def main():
    remove_sidebar_objects()
    global right_frame, sidebar_frame, cipher_instance, button_change_appearance, button_home, button_exit_application, logo_label

    cursor.execute("SELECT salt FROM user")
    retrieved_salt = cursor.fetchone()

    if retrieved_salt is not None:
        salt = bytes.fromhex(retrieved_salt[0])
    else:
        salt = os.urandom(16)
        store_salt = salt.hex()
        cursor.execute(f"INSERT INTO user (salt) VALUES ('{store_salt}')")
        connection.commit()
    
    key = key_derivation_function(master_password,salt)
    cipher_instance = Fernet(key)

    root.geometry(f"{770}x{400}")
    root.title("Lock&Key - Password Manager")

    sidebar_frame = customtkinter.CTkFrame(root, width=300)
    sidebar_frame.grid(row=0, column=0, rowspan=6, sticky="nsew")
    sidebar_frame.grid_rowconfigure(6, weight=1)

    logo_label = customtkinter.CTkLabel(sidebar_frame, text="", image=logo_image_dark)
    logo_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

    button_adding_entry = customtkinter.CTkButton(sidebar_frame, text="Add", command=adding_entry, font=customtkinter.CTkFont(weight="bold"))
    button_adding_entry.grid(row=1, column=0, padx=20, pady=10, sticky="w")

    button_updating_entry = customtkinter.CTkButton(sidebar_frame, text="Update", command=updating_entry, font=customtkinter.CTkFont(weight="bold"))
    button_updating_entry.grid(row=2, column=0, padx=20, pady=10, sticky="w")

    button_deleting_entry = customtkinter.CTkButton(sidebar_frame, text="Delete", command=deleting_entry, font=customtkinter.CTkFont(weight="bold"))
    button_deleting_entry.grid(row=3, column=0, padx=20, pady=10, sticky="w")

    button_listing_entries = customtkinter.CTkButton(sidebar_frame, text="List", command=listing_entries, font=customtkinter.CTkFont(weight="bold"))
    button_listing_entries.grid(row=4, column=0, padx=20, pady=10, sticky="w")

    button_home = customtkinter.CTkButton(sidebar_frame, text="", image=information_image_dark, command=home_screen, font=customtkinter.CTkFont(weight="bold"), width=30, height=30)
    button_home.grid(row=6, column=0, padx=(20,0), pady=10, sticky="w")

    button_change_appearance = customtkinter.CTkButton(sidebar_frame, text="", image=dark_mode_image, command=change_appearance_mode, font=customtkinter.CTkFont(weight="bold"), width=30, height=30)
    button_change_appearance.grid(row=6, column=0, padx=(70,0), pady=10, sticky="w")

    button_exit_application = customtkinter.CTkButton(sidebar_frame, text="", image=exit_image_dark, command=exit_application, font=customtkinter.CTkFont(weight="bold"), width=30, height=30)
    button_exit_application.grid(row=6, column=0, padx=(120,0), pady=10, sticky="w")

    right_frame = customtkinter.CTkFrame(root)
    right_frame.grid(row=0, column=1, rowspan=5, sticky="nsew")
    home_screen()
    ui_change()

#-----------------------------DATABASE CREATION--------------------------
# Creates the database for the user and tables if not already cerated.
def creating_db():
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS lockandkey_{username}")
    cursor.execute(f"USE lockandkey_{username}")
    cursor.execute("CREATE TABLE IF NOT EXISTS vault (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(200) NOT NULL, password VARCHAR(1000) NOT NULL, folder VARCHAR(50) DEFAULT 'None')")
    cursor.execute("CREATE TABLE IF NOT EXISTS user (id INT AUTO_INCREMENT PRIMARY KEY, salt VARCHAR(50) NOT NULL)")
    connection.commit()
    main()

#-----------------------------LOGIN FUNCTION--------------------------
# The login function authenticates the user before being able to use
# the password manager, it establishes a connection to the specified
# MySQL server, and uses the MySQL credentials for authentication.
# The login function also has a "remember me" functionality which
# remembers the IP and username.
def login():
    global root, login_frame, login_failure_message_label
    root = customtkinter.CTk()
    root.geometry(f"{180}x{280}")
    root.title("Login")
    root.resizable(False, False)

    root.grid_columnconfigure(1, weight=1)
    root.grid_columnconfigure((2, 3), weight=0)
    root.grid_rowconfigure((0, 1, 2), weight=1)

    login_frame = customtkinter.CTkFrame(root)
    login_frame.grid(row=0, column=0, rowspan=6, sticky="nsew")
    login_frame.grid_rowconfigure(6, weight=1)


    main_title_label = customtkinter.CTkLabel(login_frame, text="MySQL Login", font=customtkinter.CTkFont(size=20, weight="bold"))
    main_title_label.grid(row=0, column=0, padx=20, pady=(10,10), sticky="w")

    host_entry = customtkinter.CTkEntry(login_frame, placeholder_text="MySQL Server IP")
    host_entry.grid(row=1, column=0, padx=20, pady=5, sticky="ew")

    username_entry = customtkinter.CTkEntry(login_frame, placeholder_text="Username")
    username_entry.grid(row=2, column=0, padx=20, pady=5, sticky="ew")

    password_entry = customtkinter.CTkEntry(login_frame, placeholder_text="Password", show="*")
    password_entry.grid(row=3, column=0, padx=20, pady=5, sticky="ew")

    def remember_me():
        if remember_me_check.get():
            if os.path.isfile(".remember_me.txt"):
                pass
            else:
                with open(".remember_me.txt", "x") as file:
                    file.close()
        else:
            if os.path.isfile(".remember_me.txt"):
                os.remove(".remember_me.txt")

    remember_me_check = customtkinter.CTkCheckBox(login_frame, text="Remember me", command=remember_me)
    remember_me_check.grid(row=4, column=0, padx=20,pady=5, sticky="ew")

    if os.path.isfile(".remember_me.txt"):
        with open(".remember_me.txt", "r") as file:
            line = file.readlines()
        if len(line) > 0:
            remember_me_check.select()
            stripped_line = line[0].strip()
            host_entry.insert("end", stripped_line)
            username_entry.insert("end", line[1])
        else:
            remember_me_check.deselect()
            os.remove(".remember_me.txt")
    else:
        pass

    def authentication():
        global connection, cursor, username, master_password

        username = username_entry.get().strip()
        master_password = password_entry.get().strip()
        host = host_entry.get().strip()
        octet_regex = r"(?!.*(?:\d){4})(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"
        host_regex = rf"{octet_regex}\.{octet_regex}\.{octet_regex}\.{octet_regex}$"
        username_regex = r"^[A-Za-z_.@\-]+$"
        password_regex = r"^[A-Za-z0-9#!@#$^&*.]+$"
        if re.match(host_regex,host):
            login_failure_message_label.configure(text="")
            if re.match(username_regex,username):
                login_failure_message_label.configure(text="")
                if re.match(password_regex,master_password):
                    login_failure_message_label.configure(text="")
                    if mysql_server_alive_check(host):
                        login_failure_message_label.configure(text="")
                        try:
                            if os.path.isfile(".remember_me.txt"):
                                with open(".remember_me.txt", "r") as file:
                                    line = file.readlines()
                                if len(line) > 0:
                                    pass
                                else:
                                    with open(".remember_me.txt", "a") as file:
                                        file.write(host_entry.get() + "\n")
                                        file.write(username_entry.get())
                                        file.close()
                            else:
                                pass
                            connection = mysql.connector.connect(user=username, password=master_password, host=host)
                            cursor = connection.cursor()
                            creating_db()
                        except mysql.connector.Error:
                            login_failure_message_label.configure(text="Login failed.", text_color=error_color)
                    else:
                        login_failure_message_label.configure(text="Host unreachable.", text_color=error_color)
                else:
                    login_failure_message_label.configure(text="Password invalid.", text_color=error_color) 
            else:
                login_failure_message_label.configure(text="Username invalid.", text_color=error_color)
        else:
            login_failure_message_label.configure(text="Host invalid.", text_color=error_color)

    login_button = customtkinter.CTkButton(login_frame, text="Login", command=authentication)
    login_button.grid(row=5, column=0, padx=20, pady=(10,5), sticky="w")

    login_failure_message_label = customtkinter.CTkLabel(login_frame, text="")
    login_failure_message_label.grid(row=6, column=0, padx=20, pady=0, sticky="w")

    get_color()
    root.mainloop()


# RUNS THE LOGIN FUNCTION UPON RUNTIME
login()
