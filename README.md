# Portal

> ⚠️ The old Python2 version is available in branch [portal-python2](https://github.com/wenchy/portal/tree/portal-python2).

A simple yet powerful Python3 mirco-framework for GM (Game Maker).

## Requirements

- python3 (v3.12+): `dnf install python3.12-pip`
- python3-dev: `dnf install python3.12-devel`
- tornado: `python3 -m pip install tornado`
- redis: `python3 -m pip install redis`
- protobuf: `python3 -m pip install --no-binary protobuf protobuf`
- urllib3: `python3 -m pip install urllib3`

Optional:
- gRPC tools(protoc): `python3 -m pip install grpcio-tools`
- Install gRPC: `python3 -m pip install grpcio`


## Design: Python -> HTML mapping

| Python                                                                                      | HTML                                                                                                                                                                                                                                                   |
| ------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [module](https://docs.python.org/3/tutorial/modules.html)                                   | [tab](https://getbootstrap.com/docs/3.4/components/#nav-tabs)                                                                                                                                                                                          |
| [function](https://docs.python.org/3/tutorial/controlflow.html#defining-functions)          | [form](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/form)                                                                                                                                                                                 |
| [arguments](https://docs.python.org/3/tutorial/controlflow.html#more-on-defining-functions) | - [input](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input) <br> - [textarea](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/textarea) <br> - [select](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/select)<br> |

## Nginx reverse proxy

```nginx
location / {
    rewrite / /dev redirect;
}

location = /favicon.ico {
    log_not_found off;
}

location ^~ /dev/ {
    # NOTE: new portal version support prefix path, no need to rewrite
    # rewrite  (/dev/)(.*)$ /$2 break;
    proxy_pass_header Server;
    proxy_set_header Host $http_host;
    proxy_redirect off;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Scheme $scheme;
    proxy_pass http://127.0.0.1:8001;
}
```

## Run

Run: `python3 app.py`

Run as **daemon**:
| Action  | Command                  | Mode                              |
| ------- | ------------------------ | --------------------------------- |
| start   | `./startstop.sh start`   | `singleprocess` or `multiprocess` |
| stop    | `./startstop.sh stop`    |                                   |
| restart | `./startstop.sh restart` | `singleprocess` or `multiprocess` |

## Logging

- nohup.log
- logs/app.log*
 

## Specification

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
    return object...
    return ecode
    return ecode, object...
	return form.File
	return form.Editor
```

## Examples

- *controller/index/example_modifier.py*
- *controller/index/example_editor.py*


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

## References

- [bootstrap v3.4](https://getbootstrap.com/docs/3.4/)
- [Masonry: Cascading grid layout library](https://masonry.desandro.com/)
- [bootstrap-select](https://developer.snapappointments.com/bootstrap-select/)
- [JSON Editor: A web-based tool to view, edit, format, and validate JSON](https://github.com/josdejong/jsoneditor)
- [Python inspect](https://docs.python.org/3/library/inspect.html)
- [Python typing](https://docs.python.org/3/library/typing.html)
- [Python function](https://docs.python.org/3/tutorial/controlflow.html#defining-functions)
