#!/bin/bash
sudo apt update
sudo apt install libvips-dev


source /var/app/venv/*/bin/activate && {

# collecting static files
python manage.py collectstatic --noinput;

# # log which migrations have already been applied
# python manage.py makemigrations --noinput;

# migrate the rest
python manage.py migrate --noinput;

# # another command to create a superuser (write your own)
# python manage.py mysuperuser --noinput;

}