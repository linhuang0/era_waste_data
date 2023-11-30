# era_waste_dataproject
Waste management data solution for ERA

Project env
$ python3 -m venv env
$ source env/bin/activate
(env)$ deactivate

(env)$ pip3 install django
pip3 install mysqlclient

python manage.py makemigrations
python manage.py migrate

media directory for uploading
static directory for storing static files





pip3 install mysqlclient \
    --global-option=build_ext \
    --global-option="-I/usr/local/mysql-5.7.30-macos10.14-x86_64/include/mysql.h" \
    --global-option="-L/usr/local/mysql-5.7.30-macos10.14-x86_64/lib/libmysqlclient.dylib"

