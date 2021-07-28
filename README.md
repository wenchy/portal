# portal
A simple yet powerful GM(GameMaker) tool mirco-framework.

## Requirements
- tornado v5.1.1+

## Features
- Support both **python2** and **python3**

## Design
利用反射机制将 controller, admin 目录下的 python 模块和函数映射到 tab 控件和 HTML 表单， 即

- Python module -> Web tab  
- Python function -> Web form

剥离Web UI层，只需新加一个Python函数就可以开发出一个Web页面可见的功能

## nginx config
reverse proxy
```
location / {
    rewrite / /dev redirect;
}

location = /favicon.ico {
    log_not_found off;
}

location ^~ /dev/ {
    rewrite  (/dev/)(.*)$ /$2 break;
    proxy_pass_header Server;
    proxy_set_header Host $http_host;
    proxy_redirect off;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Scheme $scheme;
    proxy_pass http://127.0.0.1:8001;
}
```

## Run
Run as **daemon**:
| Action | Command | Mode|
|--|--|--|
| start | ./startstop.sh start | singleprocess\|multiprocess |
| start | ./startstop.sh stop||
| start | ./startstop.sh restart | singleprocess\|multiprocess |

## log
```shell
vim nohup.log
vim logs/app
```

## Introduction
### Coding Standards

```python
@form.onpage
def func(__uid__, __env__, arg1, arg2, upload__file, opcode=0):
    '''
    {
        "title": "title demo",
        "tip": "...",
        "layout": "X-column",
        "theme"" "primary|danger"
        "target": "_self|_blank",
        "method": "get|post",
        "popup": "alert|prompt",
        "enctype": "application/x-www-form-urlencoded|multipart/form-data",
        "args": {
            "arg1": {
                "tip": "...",
                "desc": "...",
                "input": "text|textarea",
                "default": "...",
                "status": "readonly|disabled"
            },
            "arg2":
            {
                "input": "select",
                "options": {
                    "option1": "option1 demo",
                    "option2": "option2 demo"
                }
            },
            "upload__file": {
                "input": "file"
            },
            "opcode": {
                "desc": "操作类型",
                "input": "select",
                "options": {
                    "0": "查 询",
                    "1": "新 增",
                    "2": "删 除"
                }
            }
        },
        "submit": "opcode"
    }
    '''
    pass
    return ecode
    return ecode, object
	return 0, filecontent, {'content_type': 'text/plain', 'filename': 'filename.txt'}
```
### examples
#### 一个简单的查询表单
```python
@util.onpage
def manage_user(__uid__, __env__, username, opcode):
    '''
    {
        "title": "用户管理",
        "args": {
            "username": {
                "datalist": "$kwargs.get_user_dict"
            },
            "opcode": {
                "desc": "操作类型",
                "input": "select",
                "options": {
                    "1": "查 询",
                    "2": "删 除"
                }
            }
        },
        "submit": "opcode"
    }
    '''
    if opcode == 1:
        return username + " is queried"
    else:
        return username + " is deleted"
```
#### 上传文件
```python
@util.onpage
def upload(__uid__, __env__, upload__file):
    '''
    {
        "title": "upload",
        "enctype": "multipart/form-data",
        "args": {
            "upload__file": {
                "tip": "test.txt",
                "desc": "file path",
                "input": "file"
            }
        }
    }
    '''
    content = upload__file[0]['body']
    return 0, content
```
NOTE: 表单编码使用 `"enctype": "multipart/form-data"`，`"input": "file"`，与文件相关相关的参数必须以`_file`为后缀，即本例中的`upload__file`参数。

#### 下载文件
```python
@util.onpage
def download(__uid__, __env__):
    '''
    {
        "title": "download",
        "target": "_blank"
    }
    '''
    filename = "test.txt"
    content = "test file content."
    return 0, content, {'content_type': 'text/plain', 'filename': filename}
```
注意有三个返回值：错误码、文件内容、响应头设置；`"target": "_blank"`

## Concurrency
### HTTP连接池(HTTPConnectionPool)
`common/rpc/channel.py`: HTTPConnectionPoolManager  
A singleton for managing http connetion pool.  
Keep-alive and HTTP connection pooling are 100% automatic, thanks to urllib3.

### 协程并发(gevent) (TODO
`portal/core/concurrent.py`: Concurrent  
A concurrent module based on gevent.
```
def batch_send_mail(uids, title, content, attachment):
    def send_mail(uid, title, content, attachment):
	   // e.g.: RPC call 
       pass
    concurrency = concurrent.Concurrent()
    for uid in uids:
        concurrency.spawn(send_mail, uid, title, content, attachment)
    concurrency.wait()
    return
```

## Authentication
> 鉴权

`portal/core/auth.py`: auth implemented by python decorator.  
A pluggable 6-level authentication module.
```
 auths = collections.OrderedDict([
        ('admin',  {'handler': auth_admin,  'level': 6}),
        ('oa',     {'handler': auth_oa,     'level': 5}),
        ('test',   {'handler': auth_test,   'level': 4}),
        ('api',    {'handler': auth_api,    'level': 3}), // with API token
        ('basic',  {'handler': auth_basic,  'level': 2}), // http basic
        ('anonym', {'handler': auth_anonym, 'level': 1}), // anoymous
    ])
```

## Authorization
> 授权: 还未实现RBAC

## Configuration
`portal/config.py`: 区别不同环境和大区

## TODO
-   Authorization: role-based access control (RBAC)
-   **Select**  Autocomplete Dropdown
    -   Brower built-in Datalist Element: more options, more performance reduction
    -   remote data sets: no number restriction of select options