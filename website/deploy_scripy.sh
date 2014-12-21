# Checkout code
git pull
# Redeploy static
python manage.py collectstatic
# Restart Apache
sudo apachectl -k restart