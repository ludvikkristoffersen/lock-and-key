"""
Lock&Key v1.0 - Password Manager

Lock&Key is a self managed, open-source password manager. Everything you need would 
need to store and manage your passwords securely!

Created by: Ludvik Kristoffersen
"""
# Importing the necessary modules, this application is built with customtkinter
# and it uses mysql.connector to connect to the self hosted MySQL intance, and 
# uses Fernet to encrypt and decrypt passwords. Pillow is used for the processing 
# of images in conjunction with customtikinter. String and random are used for the
# creation of random passwords. Time is used for adding delays between certain 
# actions, and the os library is used to check if files exist or not.
from cryptography.fernet import Fernet
from PIL import Image
import customtkinter
import mysql.connector
import random
import string
import time
import os

# Setting the appearance mode and the color theme of the application
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

# Setting images
logo_image = customtkinter.CTkImage(dark_image=Image.open(".images/L&K-text-logo.png"), size=(150,27))
information_image = customtkinter.CTkImage(light_image=Image.open(".images/info.png"), size=(40,40))

# Functions for removing the contents from the frame objects
def remove_right_objects():
    for widget in right_frame.winfo_children():
        widget.destroy()

def remove_sidebar_objects():
    for widget in login_frame.winfo_children():
        widget.destroy()

def home_screen():
    remove_right_objects()
    information_image_label = customtkinter.CTkLabel(right_frame, text="", image=information_image)
    information_image_label.grid(row=0, column=0,padx=20, pady=(20,10), sticky="w")
    information_title_label = customtkinter.CTkLabel(right_frame, text="Information", font=customtkinter.CTkFont(size=20, weight="bold"))
    information_title_label.grid(row=0, column=0, padx=70, pady=(20,10), sticky="w")

    description_text = customtkinter.CTkTextbox(right_frame, width=582, height=50, fg_color="transparent")
    description_text.grid(row=1, column=0, padx=12, pady=10, sticky="w")
    description_text.insert("end", "Lock&Key is a self managed, open-source password manager. Everything you need would need to store and manage your passwords securely!")
    description_text.configure(state="disabled")

    usecase_label = customtkinter.CTkLabel(right_frame, text="Provided Functionalities", font=customtkinter.CTkFont(size=20, weight="bold"))
    usecase_label.grid(row=2, column=0, padx=20, pady=5, sticky="w")

    usage_text = customtkinter.CTkTextbox(right_frame, width=582, height=160, fg_color="transparent")
    usage_text.grid(row=3, column=0, padx=12, pady=5, sticky="w")
    usage_text.insert("end", """• Add new entries for any account you have. Generate strong random passwords to prevent    weak passwords.\n
• Update entries to change their details such as new username, password, and folder.\n
• Manage your entries by deleting those you no longer user.\n
• Easily list all or specified entries, and safely copy passwords.""")
    usage_text.configure(state="disabled")

# Function for adding a new username:password entry to the database
def adding_entry():
    remove_right_objects()

    add_entry_label = customtkinter.CTkLabel(right_frame, text="Add Entry", font=customtkinter.CTkFont(weight="bold"))
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
            encode_password = password.encode()
            encrypt_password = cipher_instance.encrypt(encode_password)
            decoded_encrypted_password = encrypt_password.decode()
            folder = folder_entry.get().strip()
            folder_select = folder_menu.get()

            if len(username) > 0 :
                if len(password) > 0:
                    if len(folder) > 0:
                        cursor.execute(f'INSERT INTO vault (username, password, folder) VALUES ("{username}","{decoded_encrypted_password}","{folder}");')
                        connection.commit()
                        message_label.configure(text="New entry added!", text_color="#90EE90")
                        username_entry.delete(0, 'end')
                        password_entry.delete(0, 'end')
                        folder_entry.delete(0, 'end')
                        right_frame.after(2000, lambda: message_label.configure(text=""))
                    else:
                        cursor.execute(f'INSERT INTO vault (username, password, folder) VALUES ("{username}","{decoded_encrypted_password}","{folder_select}");')
                        connection.commit()
                        message_label.configure(text="New entry added!", text_color="#90EE90")
                        username_entry.delete(0, 'end')
                        password_entry.delete(0, 'end')
                        folder_entry.delete(0, 'end')
                        right_frame.after(2000, lambda: message_label.configure(text=""))
                else:
                    message_label.configure(text="Password cannot be empty.", text_color="red")
                    right_frame.after(2000, lambda: message_label.configure(text=""))
            else:
                message_label.configure(text="Username cannot be empty.", text_color="red")
                right_frame.after(2000, lambda: message_label.configure(text=""))
        except mysql.connector.Error:
            message_label.configure(text="Failed to add new entry!", text_color="red")
            right_frame.after(2000, lambda: message_label.configure(text=""))

    add_button = customtkinter.CTkButton(right_frame, text="Add Entry", command=add_database_entry)
    add_button.grid(row=4, column=0, padx=20, pady=10, sticky="w")
    
    def generate_random_password():
        try:
            password_length = int(password_char_length.get())
            if password_length < 25:
                message_label.configure(text="Character length to short!", text_color="red")
                right_frame.after(2000, lambda: message_label.configure(text=""))
            elif password_length > 255:
                message_label.configure(text="Character length to long!", text_color="red")
                right_frame.after(2000, lambda: message_label.configure(text=""))
            else:
                password_entry.delete(0, "end")
                letters = [char for char in string.ascii_letters]
                digits = [char for char in string.digits]
                special_char = ["#","!","&","*","^","%"]
                combined_char_list = letters+digits+special_char
                random_password = "".join(random.choices(combined_char_list, k=password_length))
                password_entry.insert(0, random_password)
        except:
            message_label.configure(text="Character length not valid!", text_color="red")
            right_frame.after(2000, lambda: message_label.configure(text=""))
    
    password_char_length = customtkinter.CTkEntry(right_frame, placeholder_text="25-255", width=60, justify="center")
    password_char_length.grid(row=4, column=2, padx=10, pady=10, sticky="w")
    password_char_length.insert(0, "50")

    generate_password_button = customtkinter.CTkButton(right_frame, text="Generate Password", command=generate_random_password)
    generate_password_button.grid(row=4, column=1, pady=10, sticky="w")

    message_label = customtkinter.CTkLabel(right_frame, text="")
    message_label.grid(row=5, column=0, padx=20, pady=10, sticky="w")

# Function for updating an entry that is stored in the database
def updating_entry():
    remove_right_objects()

    global updating_list
    update_entry_label = customtkinter.CTkLabel(right_frame, text="Update Entry", font=customtkinter.CTkFont(weight="bold"))
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
            title_username_label = customtkinter.CTkLabel(scrollable_frame, text="Username", font=customtkinter.CTkFont(size=15, weight="bold"), text_color="#72ACEC")
            title_username_label.grid(row=2, column=0, padx=0, pady=5, sticky="w")
            title_folder_label = customtkinter.CTkLabel(scrollable_frame, text="Folder", font=customtkinter.CTkFont(size=15, weight="bold"), text_color="#72ACEC")
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
    
        update_entry_label = customtkinter.CTkLabel(right_frame, text="Update Entry")
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
                    message_label.configure(text="Character length to short!", text_color="red")
                    right_frame.after(2000, lambda: message_label.configure(text=""))
                elif password_length > 255:
                    message_label.configure(text="Character length to long!", text_color="red")
                    right_frame.after(2000, lambda: message_label.configure(text=""))
                else:
                    password_entry.delete(0, "end")
                    letters = [char for char in string.ascii_letters]
                    digits = [char for char in string.digits]
                    special_char = ["#","!","&","*","^","%"]
                    combined_char_list = letters+digits+special_char
                    random_password = "".join(random.choices(combined_char_list, k=password_length))
                    password_entry.insert(0, random_password)
            except:
                message_label.configure(text="Character length not valid!", text_color="red")
                right_frame.after(2000, lambda: message_label.configure(text=""))
    
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
            if len(password) != 0:
                password = password_entry.get()
                encode_password = password.encode()
                encrypt_password = cipher_instance.encrypt(encode_password)
                decoded_encrypted_password = encrypt_password.decode()
            else:
                pass
            if len(new_username) > 0:
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
                    message_label.configure(text="Nothing has been changed!", text_color="red")
                    right_frame.after(2000, lambda: message_label.configure(text="")) 
            else:
                message_label.configure(text="Username cannot be empty.", text_color="red")
                right_frame.after(2000, lambda: message_label.configure(text=""))
        def cancel_update():
            remove_right_objects()
            updating_entry()
        confirm_update_button = customtkinter.CTkButton(right_frame, text="Update", command=confirm_update, width=50)
        confirm_update_button.grid(row=4, column=0, padx=20, pady=10, sticky="w")
        cancel_update_button = customtkinter.CTkButton(right_frame, text="Cancel", command=cancel_update, width=50)
        cancel_update_button.grid(row=4, column=0, padx=90, pady=10, sticky="w")
    updating_list()
    update_entries_button = customtkinter.CTkButton(right_frame, text="Refresh", command=updating_list)
    update_entries_button.grid(row=1, column=0, padx=180, pady=0, sticky="w")

# Function for deleting an entry in the database
def deleting_entry():
    remove_right_objects()

    global updating_list
    delete_entry_label = customtkinter.CTkLabel(right_frame, text="Delete Entry", font=customtkinter.CTkFont(weight="bold"))
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
        delete_entry_label = customtkinter.CTkLabel(right_frame, text="Delete Entry")
        delete_entry_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")
        warning_label = customtkinter.CTkLabel(right_frame, text="Deletion of entries are final, are you sure?")
        warning_label.grid(row=1, column=0, padx=20, pady=5, sticky="w")

        def confirm_deletion():
            cursor.execute(f"DELETE FROM vault WHERE id={int(row_id)}")
            connection.commit()
            deleting_entry()
        confirm_deletion_button = customtkinter.CTkButton(right_frame, text="Yes", command=confirm_deletion, width=50, fg_color="#B30000", hover_color="#800000")
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
            title_username_label = customtkinter.CTkLabel(scrollable_frame, text="Username", font=customtkinter.CTkFont(size=15, weight="bold"), text_color="#72ACEC")
            title_username_label.grid(row=2, column=0, padx=0, pady=5, sticky="w")
            title_folder_label = customtkinter.CTkLabel(scrollable_frame, text="Folder", font=customtkinter.CTkFont(size=15, weight="bold"), text_color="#72ACEC")
            title_folder_label.grid(row=2, column=1, padx=20, pady=5, sticky="w")

            username_label = customtkinter.CTkLabel(scrollable_frame, text=f"{entry[1]}")
            username_label.grid(row=entry_id, column=0, padx=0, pady=5, sticky="w")

            folder_label = customtkinter.CTkLabel(scrollable_frame, text=f"{entry[2]}")
            folder_label.grid(row=entry_id, column=1, padx=20, pady=5, sticky="w")

            row_id = entry[0]

            remove_button = customtkinter.CTkButton(scrollable_frame, text="Delete", fg_color="#B30000", hover_color="#800000")
            remove_button.grid(row=entry_id, column=2, padx=5, pady=5, sticky="w")
            remove_button.configure(command=lambda r=row_id: delete_entry_button(r))
            entry_id += 1
    updating_list()
    update_entries_button = customtkinter.CTkButton(right_frame, text="Refresh", command=updating_list)
    update_entries_button.grid(row=1, column=0, padx=180, pady=0, sticky="w")

# Function for listing the entries stored in the database
def listing_entries():
    remove_right_objects()
    global scrollable_frame

    list_entry_label = customtkinter.CTkLabel(right_frame, text="Listing Entries", font=customtkinter.CTkFont(weight="bold"))
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
        button.configure(text="Copied!", fg_color="#4374AB", hover_color="#4374AB")
        scrollable_frame.after(2000, lambda: button.configure(text="Copy Pass", fg_color="#1F538D", hover_color="#14375E"))

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
            title_username_label = customtkinter.CTkLabel(scrollable_frame, text="Username", font=customtkinter.CTkFont(size=15, weight="bold"), text_color="#72ACEC")
            title_username_label.grid(row=2, column=0, padx=0, pady=5, sticky="w")
            title_folder_label = customtkinter.CTkLabel(scrollable_frame, text="Folder", font=customtkinter.CTkFont(size=15, weight="bold"), text_color="#72ACEC")
            title_folder_label.grid(row=2, column=1, padx=20, pady=5, sticky="w")
            title_password_label = customtkinter.CTkLabel(scrollable_frame, text="Password", font=customtkinter.CTkFont(size=15, weight="bold"), text_color="#72ACEC")
            title_password_label.grid(row=2, column=2, padx=5, pady=5, sticky="w")

            username_label = customtkinter.CTkLabel(scrollable_frame, text=f"{entry[0]}")
            username_label.grid(row=entry_id, column=0, padx=0, pady=5, sticky="w")

            password = entry[1]
            encode_password = password.encode()
            decrypted_password = cipher_instance.decrypt(encode_password)

            folder_label = customtkinter.CTkLabel(scrollable_frame, text=f"{entry[2]}")
            folder_label.grid(row=entry_id, column=1, padx=20, pady=5, sticky="w")

            copy_button = customtkinter.CTkButton(scrollable_frame, text="Copy Pass")
            copy_button.grid(row=entry_id, column=2, padx=5, pady=5, sticky="w")
            copy_button.configure(command=lambda p=decrypted_password, b=copy_button: copy_to_clipboard(p, b))
            entry_id += 1
    updating_list()
    update_entries_button = customtkinter.CTkButton(right_frame, text="Refresh", command=updating_list)
    update_entries_button.grid(row=1, column=0, padx=180, pady=0, sticky="w")

# Function for exiting the application and closing the database connection
def exit_application():
    cursor.close()
    connection.close()
    time.sleep(1)
    quit()

# The main function containing all functionality, creating the database and the table if not already created
def main():
    remove_sidebar_objects()

    global right_frame, sidebar_frame, cipher_instance
    cursor.execute("CREATE DATABASE IF NOT EXISTS passwordmanager")
    cursor.execute("USE passwordmanager")
    cursor.execute("CREATE TABLE IF NOT EXISTS vault (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(200) NOT NULL, password VARCHAR(1000) NOT NULL, folder VARCHAR(50) DEFAULT 'None')")
    connection.commit()

    if os.path.isfile(".key.txt"):
        with open(".key.txt", "r") as file:
            key = file.readline().strip()
            file.close()
        encoded_key = key.encode()
        cipher_instance = Fernet(encoded_key)
    else:
        with open(".key.txt", "x") as file:
            file.close()
        genKey = Fernet.generate_key()
        decode_key = genKey.decode()
        with open(".key.txt", "w+") as file:
            file.write(decode_key)
            file.seek(0)
            key = file.readline().strip()
            file.close()
        encoded_key = key.encode()
        cipher_instance = Fernet(encoded_key)

    root.geometry(f"{800}x{400}")
    root.title("Lock&Key V1.0")

    sidebar_frame = customtkinter.CTkFrame(root, width=300, corner_radius=0)
    sidebar_frame.grid(row=0, column=0, rowspan=6, sticky="nsew")
    sidebar_frame.grid_rowconfigure(6, weight=1)

    logo_label = customtkinter.CTkLabel(sidebar_frame, text="", image=logo_image)
    logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

    #label = customtkinter.CTkLabel(sidebar_frame, text="Lock&Key", font=customtkinter.CTkFont(size=20, weight="bold"))
    #label.grid(row=0, column=0, padx=20, pady=(20, 10))

    button_home = customtkinter.CTkButton(sidebar_frame, text="Home", command=home_screen, font=customtkinter.CTkFont(weight="bold"), corner_radius=5)
    button_home.grid(row=1, column=0, padx=20, pady=10)

    button_adding_entry = customtkinter.CTkButton(sidebar_frame, text="Add", command=adding_entry, font=customtkinter.CTkFont(weight="bold"), corner_radius=5)
    button_adding_entry.grid(row=2, column=0, padx=20, pady=10)

    button_updating_entry = customtkinter.CTkButton(sidebar_frame, text="Update", command=updating_entry, font=customtkinter.CTkFont(weight="bold"), corner_radius=5)
    button_updating_entry.grid(row=3, column=0, padx=20, pady=10)

    button_deleting_entry = customtkinter.CTkButton(sidebar_frame, text="Delete", command=deleting_entry, font=customtkinter.CTkFont(weight="bold"), corner_radius=5)
    button_deleting_entry.grid(row=4, column=0, padx=20, pady=10)

    button_listing_entries = customtkinter.CTkButton(sidebar_frame, text="List", command=listing_entries, font=customtkinter.CTkFont(weight="bold"), corner_radius=5)
    button_listing_entries.grid(row=5, column=0, padx=20, pady=10)

    button_exit_application = customtkinter.CTkButton(sidebar_frame, text="Exit", command=exit_application, fg_color="#B30000", hover_color="#800000", font=customtkinter.CTkFont(weight="bold"), corner_radius=5)
    button_exit_application.grid(row=6, column=0, padx=20, pady=10)

    right_frame = customtkinter.CTkFrame(root, corner_radius=0)
    right_frame.grid(row=0, column=1, rowspan=5, sticky="nsew")

    home_screen()

# Function to authenticate the user and logging them into the MySQL database
def login():
    global root, login_frame
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
                with open(".remember_me.txt", "a") as file:
                    file.write(host_entry.get() + "\n")
                    file.write(username_entry.get())
                    file.close()
        else:
            if os.path.isfile(".remember_me.txt"):
                os.remove(".remember_me.txt")

    remember_me_check = customtkinter.CTkCheckBox(login_frame, text="Remember me", command=remember_me)
    remember_me_check.grid(row=4, column=0, padx=20,pady=5, sticky="ew")

    if os.path.isfile(".remember_me.txt"):
        with open(".remember_me.txt", "r") as file:
            line = file.readlines()
            remember_me_check.select()
            stripped_line = line[0].strip()
            host_entry.insert("end", stripped_line)
            username_entry.insert("end", line[1])
    else:
        pass

    def authentication():
        global connection, cursor
        try:
            username = username_entry.get()
            password = password_entry.get()
            host = host_entry.get()
            connection = mysql.connector.connect(user=username, password=password, host=host)
            cursor = connection.cursor()
            main()
        except mysql.connector.Error:
            login_failure_message_label.configure(text="Login failed.", text_color="red")
            login_frame.after(2000, lambda: login_failure_message_label.configure(text=""))

    login_button = customtkinter.CTkButton(login_frame, text="Login", command=authentication)
    login_button.grid(row=5, column=0, padx=20, pady=(10,5), sticky="w")

    login_failure_message_label = customtkinter.CTkLabel(login_frame, text="")
    login_failure_message_label.grid(row=6, column=0, padx=20, pady=0, sticky="w")

    root.mainloop()

# Running the login function at startup
login()
