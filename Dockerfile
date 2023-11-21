FROM python:3.11.2-alpine3.17
ADD . /app
WORKDIR /app
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories\
    && apk add --no-cache --virtual .build-deps gcc musl-dev libffi-dev openssl-dev bash\
    && apk add --no-cache libffi openssl \
    && pip3 install --upgrade pip setuptools wheel gunicorn -i https://pypi.tuna.tsinghua.edu.cn/simple\
    && pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple\
    && apk del .build-deps
RUN rm -f /etc/localtime
RUN  ln -s /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo 'Asia/Shanghai' > /etc/timezone
RUN chmod 755 run.sh
CMD ./run.sh
EXPOSE 8000