FROM python:3.11.2
ADD . /app
WORKDIR /app
RUN pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN python manage.py collectstatic
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
EXPOSE 8000