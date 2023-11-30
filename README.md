# era_waste_dataproject
Waste management data solution for ERA

1.Project env
$ python3 -m venv venv
$ source env/bin/activate
(env)$ deactivate

(env)$ pip3 install django
pip3 install mysqlclient

mysql -u root -p
mysql> CREATE DATABASE era_waste CHARACTER SET utf8;
Query OK, 1 row affected (0.01 sec)

(venv) ➜  pip install mysqlclient


python manage.py migrate
mysql> use era_waste
Database changed
mysql> show tables;


python manage.py runserver 0.0.0.0:8000


2.Other:
(1)media directory for uploading
(2)static directory for storing static files


