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

sudo pip install requests-oauth

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


# Deploy with mod_wsgi and Apache
#Get the wsgi apache2 module
sudo apt-get install libapache2-mod-wsgi

# Edit /etc/apache2/sites-enabled/000-default apache configuration file
sudo cp /etc/apache2/sites-enabled/000-default /etc/apache2/sites-enabled/000-default-backup
sudo vim /etc/apache2/sites-enabled/000-default

change the contents to the following

<VirtualHost *:80>
        ServerAdmin webmaster@localhost

        WSGIDaemonProcess startup_sniffer
        WSGIScriptAlias / /var/www/startup_sniffer.wsgi

        DocumentRoot /var/www
        <Directory />
                WSGIProcessGroup startup_sniffer
                WSGIApplicationGroup %{GLOBAL}
                Options FollowSymLinks
                AllowOverride None
        </Directory>
        <Directory /var/www/>
                WSGIProcessGroup startup_sniffer
                WSGIApplicationGroup %{GLOBAL}
                Options Indexes FollowSymLinks MultiViews
                AllowOverride None
                Order allow,deny
                allow from all
        </Directory>

        ScriptAlias /cgi-bin/ /usr/lib/cgi-bin/
        <Directory "/usr/lib/cgi-bin">
                AllowOverride None
                Options +ExecCGI -MultiViews +SymLinksIfOwnerMatch
                Order allow,deny
                Allow from all
        </Directory>

        ErrorLog ${APACHE_LOG_DIR}/error.log

        # Possible values include: debug, info, notice, warn, error, crit,
        # alert, emerg.
        LogLevel warn

        CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>

#Create the file /var/www/startup_sniffer.wsgi and add the following contents:
import sys
sys.path.insert(0, '/home/ubuntu/startup_sniffer/webapp')
from app import app

# start the apache2 web server:
sudo apachectl start

# To stop or restart the server:
sudo apachectl stop
sudo apachectl restart

# Debug error:
tail /var/log/apache2/error.log
