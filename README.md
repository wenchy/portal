# portal
A simple yet powerful GM(GameMaker) tool mirco-framework.

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
