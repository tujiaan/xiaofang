#!/usr/bin/python3
# coding: utf-8
from app import create_app
application=create_app()
#app_ctx = application.app_context()

if __name__ == '__main__':
    application.run(host="127.0.0.1", port=8022, threaded=True)
    #application.run(host="0.0.0.0", port=3389, threaded=True)
