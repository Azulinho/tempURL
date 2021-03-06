#!/usr/bin/env python -tt -u

from flask import Flask, request
import redis
import re
import os


app = Flask(__name__)

redis_host = os.getenv('REDIS_HOST', 'redis')
redis_port = os.getenv('REDIS_PORT', 6379)

r = redis.StrictRedis(host=redis_host, port=redis_port, db=0)

@app.route(u'/api', methods=['GET'])
def api_get():
    # don't accept ints as an url
    if not isinstance(request.args.get('tempurl'), basestring):
        return 'NOT VALID TEMPURL: ints are not valid\n', 400

    # don't accept empty strings for an url
    if len(request.args.get('tempurl')) == 0:
        return 'NOT VALID TEMPURL: empty strings are not valid\n', 400

    tempurl = str(request.args.get('tempurl').encode('utf-8'))
    # don't accept dodgy URL strings
    # and our strings need to be larger than 3 characters
    if not re.match("^[A-Za-z0-9_-]{4,}$", tempurl):
        return 'NOT VALID TEMPURL: tempurl needs to be over 3 chars \n', 400

    data = r.get(tempurl)
    r.delete(tempurl)

    # this will return null if ''
    if data:
        return data, 200
    else:
        return 'NOT FOUND\n', 404


@app.route(u'/api', methods=['POST'])
def api_post():
    # don't accept ints as an url
    if not isinstance(request.args.get('tempurl'), basestring):
        return 'NOT VALID TEMPURL: ints are not valid\n', 400

    # don't accept empty strings for an url
    if len(request.args.get('tempurl')) == 0:
        return 'NOT VALID TEMPURL: empty strings are not valid\n', 400

    tempurl = str(request.args.get('tempurl').encode('utf-8'))
    # and our strings need to be larger than 3 characters
    if not re.match("^[A-Za-z0-9_-]{4,}$", tempurl):
        return 'NOT VALID TEMPURL: tempurl needs to be over 3 chars\n', 400

    ttl = int(request.args.get('ttl'))
    # mex value we'll take is 65535
    if ttl > 65535:
        return 'TTL TOO LARGE: ttl needs to be under 65535\n', 400

    data = request.files['file'].read()
    # we don't take empty files
    if len(data) == 0:
        return 'EMPTY FILE: data file is empty\n', 400

    r.set(
        tempurl,
        data,
    )
    r.expire(tempurl, ttl)
    return 'OK\n', 201



@app.route(u'/health', methods=['GET'])
def health():
    tempurl = 'health'
    ttl = 5
    data = 'probing...'

    r.set(
        tempurl,
        data
    )
    r.expire(tempurl, ttl)

    data = r.get('health')
    r.delete('health')

    if data:
        return data, 200
    else:
        return 'NOT FOUND\n', 404

if __name__ == "__main__":
    # add the handlers to the console for local debug
    app.debug = True
    app.run(host="0.0.0.0", port=6222)
