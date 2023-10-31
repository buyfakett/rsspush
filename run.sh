python3 manage.py collectstatic
if [[ ! -f database]]; then
  python3 manage.py makemigrations rss
  python3 manage.py makemigrations push
  python3 manage.py makemigrations user
  python3 manage.py migrate
fi
python3 manage.py runserver 0.0.0.0:8000