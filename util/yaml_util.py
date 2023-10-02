import os
import yaml


# 读取yaml
def read_yaml(key, url):
    with open(os.getcwd() + '/config/' + url, encoding="utf-8") as f:
        value = yaml.load(stream=f, Loader=yaml.FullLoader)
        return value[key]


# 追加写入yaml
def write_yaml(data, url):
    with open(os.getcwd() + '/config/' + url, encoding="utf-8", mode="a") as f:
        yaml.dump(data=data, stream=f, allow_unicode=True)


# 写入yaml
def write_yaml_value(data, url):
    with open(os.getcwd() + '/config/' + url, encoding="utf-8", mode="w") as f:
        yaml.safe_dump(data=data, stream=f, allow_unicode=True)


# 清空yaml
def clear_yaml(url):
    with open(os.getcwd() + '/config/' + url, encoding="utf-8", mode="w") as f:
        f.truncate()


# 读取全部yaml配置
def read_all_yaml(url):
    with open(os.getcwd() + '/config/' + url, encoding="utf-8") as f:
        value: object = yaml.load(stream=f, Loader=yaml.FullLoader)
        return value
