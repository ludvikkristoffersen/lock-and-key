
![Lock&Key](https://dl.dropboxusercontent.com/scl/fi/9oqp3mumdabuqertleppn/lock-and-key-github.png?rlkey=9b07vfcyqgtausavnn5r190nt&st=yhoy6udx&dl=0)
- Created by: [@ludvikkristoffersen](https://github.com/ludvikkristoffersen)
- Powered by Python, MySQL, and Customtkinter
- Current support: **Windows**, **Linux**
# About Lock&Key

Lock&Key is a self-hosted, self-managed, open-source password manager. It provides everything you need for storing and managing your accounts securely!

Lock&Key is built using Python as its main language with MySQL integrated to help store and manage password entries, it's self-hosted and open-source meaning you as the consumer have full control over everything. The master password for each user is used for encrypting and decrypting password entries so make it strong.
## Features
- Adding entries (strong password generation)
- Updating entries (strong password generation)
- Listing specified or all entries
- Deleting entries
- Encryption
## MySQL server set up
The user needs to have a local MySQL server set up and running, here is how to set up a MySQL server locally:
- [Windows MySQL server installation (workbench not needed)](https://www.youtube.com/watch?v=u96rVINbAUI)
- [Linux MySQL server installation (Debian)](https://www.youtube.com/watch?v=3qD6zv7thdE)

**IMPORTANT!** - When creating a MySQL user account, remember these credentials, this is how you are going to authenticate to the password manager. This acts as the master password, so make it strong!
## Installation
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
Starting the password manager:
```
python3 lock-and-key.py
```
Login by providing MySQL server IP address and MySQL user credentials, and you are good to go!
