FROM python:3.11.2
ADD . /app
WORKDIR /app
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN rm -f /etc/localtime
RUN  ln -s /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo 'Asia/Shanghai' > /etc/timezone
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
EXPOSE 8000