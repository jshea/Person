# Deployment infrastructure
A Python/Flask application will handle a single request at a time. Running multiple instances of your application is handled by middleware supporting the Web Server Gateway Interface ([WSGI](https://wikipedia.org/wiki/Web_Server_Gateway_Interface)). Flask has a WSGI server suitable for development. For production usig a WSGI server as middleware between a proxy server (NGINX/Apache) and the Flask application allows pooling instances of the Flask application.

## Proxy Server
[NGINX](https://nginx.com/) is an industry standard proxy server. This uses the Open Source version of NGINX with the following configration from the Flask docs https://flask.palletsprojects.com/en/1.1.x/deploying/wsgi-standalone/#proxy-setup.
```conf
server {
  listen       80;
  server_name  localhost;

  location / {
    # root   html;
    # index  index.html index.htm;

    proxy_pass         http://127.0.0.1:5000/;
    proxy_redirect     off;

    proxy_set_header   Host                 $host;
    proxy_set_header   X-Real-IP            $remote_addr;
    proxy_set_header   X-Forwarded-For      $proxy_add_x_forwarded_for;
    proxy_set_header   X-Forwarded-Proto    $scheme;
  }

  # redirect server error pages to the static page /50x.html
  error_page   500 502 503 504  /50x.html;
  location = /50x.html {
    root   html;
  }
}

```
Run nginx with this command
```bash
nginx
```

## WSGI Server
>[Waitress](https://docs.pylonsproject.org/projects/waitress/) "is meant to be a production-quality pure-Python WSGI server with very acceptable performance. It has no dependencies except ones which live in the Python standard library. It runs on CPython on Unix and Windows under Python 2.7+ and Python 3.4+."

Using the above NGINX configuration which forwards to localhost on port 5000, this command will run the
person app, listening on port 5000. The Waitress [default](https://docs.pylonsproject.org/projects/waitress/en/stable/runner.html#runner) is to run 4 threads.
```
waitress-serve --listen=*:5000 app:app
```

## Accessing via browser or REST application
Use http://localhost to run the web application.

Use the following APIs for your REST application
| API | URL | Method | Description |
|-----|-----|--------|-------------|
| Get all data   | http://localhost/api/all/     | GET    | Retrieves all data |
| Get one person | http://localhost/api/person/X | GET    | Retrieves person with the id of X |
| Add            | http://localhost/api/person   | POST   | Add a person |
| Update         | http://localhost/api/person   | PUT    | Update person |
| Delete         | http://localhost/api/person/X | DELETE | Delete person with the id of X |
