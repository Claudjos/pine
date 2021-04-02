# Pine Web Framework

## Overview
This is a very simple web framework WSGI compatible. Written for fun and self education.

## Develop your Web App using Pine
Checkout the [examples](examples) to learn how to develop your app.

## Deploy your Web App

### With Gunicorn
```
pip install gunicorn
gunicorn examples.books:app
```

## Unit test

### Testing your Web App
Checkout the [tests](tests) to learn how to test your app.

### Testing Pine package
```
pip install -r test-requirements.txt
python -m pytest tests --cov=pine
```