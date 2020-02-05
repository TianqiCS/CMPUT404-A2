#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, https://github.com/treedust, and Tianqi Wang
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        try:
            code = int(data.split()[1])
            if 100 <= code <= 599:
                return code
            else:
                return 404
        except:
            return None

    def get_headers(self, data):
        header = "GET /%s HTTP/1.1\r\n" % data.path
        header += "Host: %s\r\n" % data.netloc
        header += "Connection: close\r\n"
        header += "\r\n"
        return header

    def post_headers(self, data, args):
        a = ""
        if args:
            for i in args:
                a += i
                a += "="
                a += urllib.parse.quote(args[i])
                a += "&"
            a = a[:-1]
            counts = len(a)
        else:
            counts = 0
        header = "POST /%s HTTP/1.1\r\n" % data.path
        header += "Host: %s\r\n" % data.netloc
        header += "Content-Type: application/json\r\n"
        header += "Content-Length: %d\r\n" % counts
#        header += "Connection: close\r\n"
        header += "\r\n"
        header += a
        print(header)
        return header

    def get_body(self, data):
        i = data.find("\r\n\r\n")
        return data[i+4:]
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))

    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        self.parse_result = urllib.parse.urlparse(url)
        host = self.parse_result.netloc.split(":")
        if len(host) != 2:
            if self.parse_result.scheme == "http":
                port = 80
            elif self.parse_result.scheme == "https":
                port = 443
            else:
                port = 80
        else:
            port = int(host[1])
        host = host[0]
        self.connect(host, port)

        self.sendall(self.get_headers(self.parse_result))
        data = self.recvall(self.socket)
        code = self.get_code(data)
        if code != 404:
            body = self.get_body(data)
        else:
            body = ''
        #print(body)
        self.close()
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        self.parse_result = urllib.parse.urlparse(url)
        host = self.parse_result.netloc.split(":")
        if len(host) != 2:
            if self.parse_result.scheme == "http":
                port = 80
            elif self.parse_result.scheme == "https":
                port = 443
            else:
                port = 80
        else:
            port = int(host[1])
        host = host[0]

        self.connect(host, port)
        #data = self.recvall(self.socket)

        self.sendall(self.post_headers(self.parse_result, args))
        data = self.recvall(self.socket)
        code = self.get_code(data)
        if code != 404:
            body = self.get_body(data)
        else:
            body = ''
        self.close()
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )

if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    #sys.argv = ["a","POST","http://www.example.com"]
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
