import logging

import azure.functions as func
import requests
import json
import os
import redis


r = redis.Redis(
    host=os.getenv("redis_server"),
    port=os.getenv("redis_port"), 
    password=os.getenv("redis_password"))

def get_weather(location):
    url = "https://api.m3o.com/v1/weather/Now"

    payload = json.dumps({
    "location": location
    })
    headers = {
    'Authorization': 'Bearer ' + os.getenv("weather_token"),
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    r.set(location, response.text, 60)
    logging.info('Setting cache')
    return response.text

def main(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse("Teste :" + os.getenv("redis_server"),status_code=200)

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        res = r.get(name)
        if res:
            logging.info('Got cache')
            return func.HttpResponse(res,status_code=200)
        else:
            logging.info('Did the Request')
            return func.HttpResponse(get_weather(name),status_code=200)
    else:
        return func.HttpResponse(
             status_code=200
        )
