#-------------------------------------------------#
# Title: http_server.py
# Dev:   Scott Luse
# Date:  July 10, 2018
#
# Status: indentation of server function while loop fixed!
# 1. server successfully sends html, txt, py content and 404 errors
# 2. server still has issues sending contents of image files
#-------------------------------------------------#

import socket
import sys

def response_ok(body=b"This is a minimal response", mimetype=b"text/plain"):
    """
    returns a basic HTTP response
    Ex:
        response_ok(
            b"<html><h1>Welcome:</h1></html>",
            b"text/html"
        ) ->

        b'''
        HTTP/1.1 200 OK\r\n
        Content-Type: text/html\r\n
        \r\n
        <html><h1>Welcome:</h1></html>\r\n
        '''
    """
    resp = []
    resp.append(b"HTTP/1.1 200 OK")
    resp.append(b"Content-Type: " + mimetype)
    resp.append(b'')
    resp.append(b'' + body)
    return b"\r\n".join(resp)


def parse_request(request):
    """
    Given the content of an HTTP request, returns the uri of that request.

    This server only handles GET requests, so this method shall raise a
    NotImplementedError if the method of the request is not GET.
    """
    one_line = request.split("\r\n", 1)[0]
    method, uri, protocol = one_line.split()

    if method != "GET":
        raise NotImplementedError

    return uri


def response_method_not_allowed():
    """Returns a 405 Method Not Allowed response"""
    resp = []
    resp.append(b"HTTP/1.1 405 Method Not Allowed")
    resp.append(b"Content-Type: text/html")
    resp.append(b'')
    resp.append(b"405 You can't do that on this server!")
    return b"\r\n".join(resp)


def response_not_found():
    """Returns a 404 Not Found response"""
    resp = []
    resp.append(b"HTTP/1.1 404 Error")
    resp.append(b"Content-Type: text/html")
    resp.append(b'')
    resp.append(b"404 Not Found")
    return b"\r\n".join(resp)

    
def mime_type_define(ext_value):
    mime = "text/plain"
    if ext_value == "txt": mime = "text/plain"
    if ext_value == "html": mime = "text/html"
    if ext_value == "py": mime = "text/html"
    if ext_value == "jpeg": mime = "image/jpeg"
    if ext_value == "png": mime = "image/png"
    print("mime lookup:", mime)
    return mime

def resolve_uri(uri):
    """
    This method should return appropriate content and a mime type.

    If the requested URI is a directory, then the content should be a
    plain-text listing of the contents with mimetype `text/plain`.

    If the URI is a file, it should return the contents of that file
    and its correct mimetype.

    If the URI does not map to a real location, it should raise an
    exception that the server can catch to return a 404 response.

    Ex:
        resolve_uri('/a_web_page.html') -> (b"<html><h1>North Carolina...",
                                            b"text/html")

        resolve_uri('/images/sample_1.png')
                        -> (b"A12BCF...",  # contents of sample_1.png
                            b"image/png")

        resolve_uri('/') -> (b"images/, a_web_page.html, make_type.py,...",
                             b"text/plain")

        resolve_uri('/a_page_that_doesnt_exist.html') -> Raises a NameError

    """

    content = b"File not found"
    mime_type = b"text/plain"
    try:
        ext_value = uri.split(".")[-1]
        mime_type = bytes(mime_type_define(ext_value), 'utf-8')

        # do we really need to open the file?

        if ext_value == "txt" or "html" or "py":
            file = open("webroot/" + uri, "r")
            if (file != None):
                file.seek(0)
                body = file.read()
                file.close()
                content = bytes(body, 'utf-8')
                return content, mime_type

        # Error: 'charmap' codec can't decode byte 0x81 in position 178:
        # character maps to <undefined>
        if ext_value == "jpeg" or "png":
            file = open("webroot/" + uri, "rb")
            if (file != None):
                file.seek(0)
                body = file.read()
                file.close()
                content = body
                return content, mime_type

    except Exception as e:
        print("Error: " + str(e))
        raise NameError

def server(log_buffer=sys.stderr):
    address = ('127.0.0.1', 10000)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print("making a server on {0}:{1}".format(*address), file=log_buffer)
    sock.bind(address)
    sock.listen(1)

    try:
        while True:
            print('waiting for a connection', file=log_buffer)
            conn, addr = sock.accept()  # blocking
            try:
                print('connection with - {0}:{1}'.format(*addr), file=log_buffer)

                request = ""
                while True:
                    data = conn.recv(16)
                    request += data.decode('utf-8')

                    if '\r\n\r\n' in request:
                        break

                print('received first line "{0}"'.format(request), file=log_buffer)

                try:
                    uri = parse_request(request)
                except NotImplementedError:
                    response = response_method_not_allowed()
                else:
                    try:
                        content, mime_type = resolve_uri(uri)
                    except NameError:
                        response = response_not_found()
                    else:
                        response = response_ok(content, mime_type)

                if response:
                    print('sending data back to client', file=log_buffer)
                    print(response)
                    conn.sendall(response)
                else:
                    msg = 'no more data from {0}:{1}'.format(*addr)
                    print(msg, log_buffer)
                    break
            finally:
                conn.close()

    except KeyboardInterrupt:
        sock.close()
        return


if __name__ == '__main__':
    server()
    sys.exit(0)


