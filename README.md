# Deploy Fefore
```
pip freeze > requirement.txt
```

# Run Environment

```
python3 -m venv .env3
source .env3/bin/activate
pip install
pip install -r requirement.txt
```

# Development Configuration

```
export FLASK_APP=baby
export FLASK_ENV=development
flask run
```

# Deployment Configuration

## 第一种方式
export FLASK_APP=baby
export FLASK_ENV=production
flask run

## 第二种方式
gunicorn+supervisor
修改gunicorn.example.conf为gunicorn.conf，修改里面的对应的日志文件路径
supervisor启动配置，示例如下
```
[program:baby]
directory = /Users/durban/python/baby ; 程序的启动目录
command = gunicorn -c /Users/durban/python/baby/gunicorn.conf baby  ; 启动命令，可以看出与手动在命令行启动的命令是一样的
autostart = true     ; 在 supervisord 启动的时候也自动启动
startsecs = 5        ; 启动 5 秒后没有异常退出，就当作已经正常启动了
autorestart = true   ; 程序异常退出后自动重启
startretries = 3     ; 启动失败自动重试次数，默认是 3
user = durban          ; 用哪个用户启动
redirect_stderr = true  ; 把 stderr 重定向到 stdout，默认 false
stdout_logfile_maxbytes = 20MB  ; stdout 日志文件大小，默认 50MB
stdout_logfile_backups = 20     ; stdout 日志文件备份数
; stdout 日志文件，需要注意当指定目录不存在时无法正常启动，所以需要手动创建目录（supervisord 会自动创建日志文件）
stdout_logfile = /var/tmp/baby_stdout.log

; 可以通过 environment 来添加需要的环境变量，一种常见的用法是修改 PYTHONPATH
; environment=PYTHONPATH=$PYTHONPATH:/path/to/somewhere%                                                                  ```
启动supervisor
配置nginx，示例如下

```
server {
	charset utf-8;

	client_max_body_size 128M;

	listen 80;

	server_name flask1.walkerfree.local; # 这是HOST机器的外部域名，用地址也行

	access_log /var/log/flask1.walkerfree.local.access.log;
	error_log /var/log/flask1.walkerfree.local.error.log;

	location / {
		proxy_pass http://127.0.0.1:8000; # 这里是指向 gunicorn host 的服务地址
		proxy_set_header Host $host;
		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
	}

	location ~ /\.(git|svn|ht) {
		deny all;
	}
}
```

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

