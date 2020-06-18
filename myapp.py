from flask import Flask
from my_openapi import MyOpenAPI
import logging

outside = MyOpenAPI(Flask, './openapi.yaml')
logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
	outside.app.run(port=8080)