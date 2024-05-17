
![Lock&Key](https://dl.dropboxusercontent.com/scl/fi/px52iz9awidm89zw698ly/lock-keytest.png?rlkey=60tx3mc998z4mr7ev3gkcb9eg&st=h6xplz8y&dl=0)
- Created by: [@ludvikkristoffersen](https://github.com/ludvikkristoffersen)
- Requires Python3 and MySQL server
# About Lock&Key

Lock&Key is a self-hosted, self-managed, open-source password manager. Everything you need to store and manage your passwords securely!

Lock&Key is built using Python as its main language with MySQL integrated to help store and manage password entries, it's self-hosted and open-source meaning you as the consumer have full control over everything. All entries are stored with encryption providing safe storage.
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
Change directory to the 'lock-and-key' directory:
```
cd lock-and-key
```
Install the required libraries:
```
pip install -r requirements.txt

pip install --upgrade --force-reinstall Pillow
```
## Usage
Starting the password manager:
```
python3 lock-and-key.py
```
Login by providing MySQL server IP address and MySQL user credentials, and you are good to go!
