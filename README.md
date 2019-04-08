# Deploy Fefore
pip freeze > requirement.txt

# Run Environment

python3 -m venv .env3
source .env3/bin/activate
pip install
pip install -r requirement.txt

# Development Configuration

export FLASK_APP=baby
export FLASK_ENV=development
flask run

# Deployment Configuration

## 第一种方式
export FLASK_APP=baby
export FLASK_ENV=production
flask run

## 第二种方式
gunicorn -w 4 -b 127.0.0.1:4000 baby

## 第三种方式
通过wheel打包后，使用安装包进行安装

## 秘钥生成及配置
import os;os.urandom(32)

在安装的实例目录下 创建 config.py 配置文件并添加如下行
SECRET_KEY=''

# 单元测试
pip install -e .
pytest
coverage run -m pytest
coverage report
coverage html

