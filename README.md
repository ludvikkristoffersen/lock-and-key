
![Lock&Key](https://dl.dropboxusercontent.com/scl/fi/9oqp3mumdabuqertleppn/lock-and-key-github.png?rlkey=9b07vfcyqgtausavnn5r190nt&st=yhoy6udx&dl=0)
- Created by: [@ludvikkristoffersen](https://github.com/ludvikkristoffersen)
- Powered by Python, MySQL, and Customtkinter
- Current OS support: **Windows**, **Linux**
- [MIT License](https://github.com/ludvikkristoffersen/lock-and-key/blob/main/license.md)
# About Lock&Key

Lock&Key is a self-hosted, self-managed, open-source password manager. It provides everything you need for storing and managing your accounts securely!

Lock&Key is built using Python as its main language with MySQL integrated to help store and manage password entries, it's self-hosted and open-source meaning you as the consumer have full control over everything. The master password for each user is used for encrypting and decrypting password entries so make it strong.
## Features
- **Adding account entries**: Create new or add existing account entries.
- **Updating account entries**: Modify account entries with new information.
- **Deleting account entries**: Remove unwanted account entries.
- **Listing account entries**: Display a list of all or specified account entries.
- **Password generation**: Generate random, complex passwords.
- **Encryption**: Data securely stored with encryption.

# Installation and Set Up
## MySQL Server Set Up
The user needs to have a local MySQL server set up and running, here is how to set up a MySQL server locally:

**IMPORTANT!** - When creating a MySQL user account, remember these credentials, this is how you are going to authenticate to the password manager. This acts as the master password, so make it strong!
- [Windows MySQL server installation (workbench not needed)](https://www.youtube.com/watch?v=u96rVINbAUI)
- [Linux MySQL server installation (Debian)](https://www.youtube.com/watch?v=3qD6zv7thdE)
## Application Installation
The Lock&Key password manager has been packaged as an executable for both Windows and Linux using the "pyinstaller" tool. Downloading the executable for your operating system eliminates the need to install any dependencies. It’s designed to work seamlessly right out of the box!
- [Download Windows executable here.](https://github.com/ludvikkristoffersen/lock-and-key/releases/tag/Lock%26Key-Windows)
- [Download Linux executable here.](https://github.com/ludvikkristoffersen/lock-and-key/releases/tag/Lock%26Key-Linux)
## Manual Installation
Clone repository (requires git to be installed):
```
git clone https://github.com/ludvikkristoffersen/lock-and-key
```
Change the directory to the 'lock-and-key' directory:
```
cd lock-and-key
```
Install the required libraries:
```
pip install -r requirements.txt
```
Install and fix the Pillow library:
```
pip install --upgrade --force-reinstall Pillow
```
## Usage
Executable installation? Launch the executable file.
Manual installation? Start the password manager:
```
python3 lock-and-key.py
```
Login by providing MySQL server IP address and MySQL user credentials, and you are good to go!


```
Hashing algorithm used: MD5
Stored hash: 42f749ade7f9e195bf475f37a44cafcb

Matching process
______________________________________________________________________________________________
| Plain text  | Generated hash                     Stored hash                      | Match? |
|--------------------------------------------------------------------------------------------|
| supersecret | 9a618248b64db62d15b300a07b00580b = 42f749ade7f9e195bf475f37a44cafcb | No     |
| password123 | 482c811da5d5b4bc6d497ffa98491e38 = 42f749ade7f9e195bf475f37a44cafcb | No     |
| Password123 | 42f749ade7f9e195bf475f37a44cafcb = 42f749ade7f9e195bf475f37a44cafcb | Yes    |
---------------------------------------------------------------------------------------------|
```
