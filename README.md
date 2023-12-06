# era_waste_dataproject
Waste management data solution for ERA

1. Create Project env and install some xx
$ python3 -m venv venv
$ source venv/bin/activate
(env)$ deactivate

(env)$ pip3 install django

Windows
Building mysqlclient on Windows is very hard. But there are some binary wheels you can install easily.

If binary wheels do not exist for your version of Python, it may be possible to build from source, but if this does not work, do not come asking for support. To build from source, download the MariaDB C Connector and install it. It must be installed in the default location (usually "C:\Program Files\MariaDB\MariaDB Connector C" or "C:\Program Files (x86)\MariaDB\MariaDB Connector C" for 32-bit). If you build the connector yourself or install it in a different location, set the environment variable MYSQLCLIENT_CONNECTOR before installing. Once you have the connector installed and an appropriate version of Visual Studio for your version of Python:

$ pip install mysqlclient

macOS (Homebrew)
If you don't want to install MySQL server, you can use mysql-client instead:
# Assume you are activating Python 3 venv
$ brew install mysql-client pkg-config
$ export PKG_CONFIG_PATH="/opt/homebrew/opt/mysql-client/lib/pkgconfig"
$ pip install mysqlclient


mysql -u root -p
mysql> CREATE DATABASE era_waste CHARACTER SET utf8;
Query OK, 1 row affected (0.01 sec)

python manage.py makemigrations
python manage.py migrate
mysql> use era_waste
Database changed
mysql> show tables;

python manage.py clean_solo

python manage.py runserver 0.0.0.0:8000


2.Other:
(1)media directory for uploading
(2)static directory for storing static files


