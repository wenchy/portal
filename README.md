# Portal

> ⚠️ The old Python2 version is available in branch [portal-python2](https://github.com/wenchy/portal/tree/portal-python2).

A simple yet powerful Python3 mirco-framework for GM (Game Maker).

## Requirements

- python3: `yum install python39`
- python3-dev: `yum install python39-devel`
- tornado: `python3 -m pip install tornado`
- redis: `python3 -m pip install redis`
- protobuf: `python3 -m pip install --no-binary protobuf protobuf`
- urllib3: `python3 -m pip install urllib3`

Optional:
- gRPC tools(protoc): `python3 -m pip install grpcio-tools`
- Install gRPC: `python3 -m pip install grpcio`

## Nginx config

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


## Design

- Python module -> HTML tab  
- Python function -> HTML form

## Run

Run as **daemon**:
| Action  | Command                  | Mode                              |
| ------- | ------------------------ | --------------------------------- |
| start   | `./startstop.sh start`   | `singleprocess` or `multiprocess` |
| stop    | `./startstop.sh stop`    |                                   |
| restart | `./startstop.sh restart` | `singleprocess` or `multiprocess` |

## Logging

- nohup.log
- logs/app.log*
 

## Quick start

### Rules

```python
@form.onpage
def func(ctx, arg1, arg2, upload__file, opcode=0):
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
                "desc": "Operation",
                "input": "select",
                "options": {
                    "0": "Query",
                    "1": "Update",
                    "2": "Delete"
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

### Examples

#### A simple form

```python
@form.onpage
def manage_player(ctx, username, opcode):
    '''
    {
        "title": "Player",
        "args": {
            "username": {
                "desc": "Username"
            },
            "opcode": {
                "desc": "Operation",
                "input": "select",
                "options": {
                    "0": "Query",
                    "1": "Update",
                    "2": "Delete"
                }
            }
        },
        "submit": "opcode"
    }
    '''
    if opcode == 0:
        return "query: "username
    elif opcode == 1:
        return "update: "username
    else:
        return "delete: "username
```

#### Upload file

```python
@form.onpage
def upload(ctx, upload__file):
    """
    {
        "title": "Upload File",
        "enctype": "multipart/form-data",
        "args": {
            "upload__file": {
                "tip": "test.txt",
                "desc": "File Path",
                "input": "file"
            }
        }
    }
    """
    content = upload__file[0]["body"]
    return 0, content
```

NOTE:
- `"enctype": "multipart/form-data"`
- `"input": "file"`，
- The argument `upload__file` must be suffixed by`_file`

#### Download file

```python
@form.onpage
def download(ctx):
    """
    {
        "title": "Download File",
        "target": "_blank"
    }
    """
    filename = "test.txt"
    content = "This file content is generated from portal."
    return 0, content, {"content_type": "text/plain", "filename": filename}
```

Returning 3 values:
1. error code
2. file content 
3. HTTP response header: `{'content_type': 'text/plain', 'filename': filename}`

In addition, **target** must be set to blank, e.g.: `"target": "_blank"`

## Concurrency

### HTTPConnectionPool

`common/rpc/channel.py`: HTTPConnectionPoolManager is a singleton for managing HTTP connetion pool.  
Keep-alive and HTTP connection pooling are 100% automatic, thanks to urllib3.

## Authentication

`core/auth.py`: auth implemented by python decorator. 

A pluggable 6-level authentication module:
```python
 auths = collections.OrderedDict([
        ('admin',  {'handler': auth_admin,  'level': 6}),
        ('oa',     {'handler': auth_oa,     'level': 5}),
        ('test',   {'handler': auth_test,   'level': 4}),
        ('api',    {'handler': auth_api,    'level': 3}), # with API token
        ('basic',  {'handler': auth_basic,  'level': 2}), # http basic
        ('anonym', {'handler': auth_anonym, 'level': 1}), # anoymous
    ])
```

## Authorization

- [ ] Authorization: role-based access control (RBAC)

## Configuration

`config.py`: differernt environments' configurations.
