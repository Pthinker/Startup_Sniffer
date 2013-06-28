Startup_Sniffer
==================================================================

My InsightDataScience (http://insightdatascience.com/) data product.



Setup on Amazon EC2 Ubuntu instance:
==================================================================

# Python
wget https://pypi.python.org/packages/source/s/setuptools/setuptools-0.6c11.tar.gz (installing setuptools 0.7 version
seems having problem to install Mysql-python for me)
tar xzf setuptools-0.6c11.tar.gz
sudo python setup.py install

wget https://pypi.python.org/packages/source/p/pip/pip-1.3.1.tar.gz
tar xzf pip-1.3.1.tar.gz
sudo python setup.py install

Install virtualenv (Optional)
sudo pip install virtualenv

sudo apt-get install python-lxml

sudo apt-get install build-essential python-dev python-numpy python-setuptools python-scipy libatlas-dev

sudo apt-get install python-matplotlib

sudo pip install -U scikit-learn

sudo pip install -U pandas

sudo pip install scrapy

sudo pip install bitly_api

...

Alternatively, you could install required python modules by using:
sudo pip install -r requirements.txt
You could generate requirements.txt file by issuing:
pip freeze > requirements.txt

# Flask
sudo apt-get install python-flask

# Mysql
sudo apt-get install mysql-server
sudo apt-get install libmysqlclient-dev

sudo pip install MySQL-python

login to mysql, create a new account(change USER and PASSWD):
GRANT ALL ON *.* TO USER@localhost IDENTIFIED BY 'PASSWD';

Dump data to sql file to transfter to EC2 host (Optionally):
mysqldump -uuser -ppwd  --databases db_name > db.sql
To load into mysql:
mysql -u user -p pwd db_name < db.sql
or
login into mysql and:
source db.sql

# Git
sudo apt-get install git

# Domain(Godaddy) and AWS EC2 mapping
http://www.quora.com/If-I-bought-a-domain-name-from-Godaddy-but-plan-to-use-amazon-EC2-to-run-the-site-do-I-need-hosting-from-Godaddy

# To run Flask server
Open a new screen, and issue:
sudo python run.py


