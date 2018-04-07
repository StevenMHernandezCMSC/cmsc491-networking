import os
import sys
from socket import *

import re


class HTTPClient:
    def GET(self, url):
        # Validate URL
        if not self.__validate_url(url):
            exit("ERR - arg 1")

        # parse url into self.host self.path
        self.__parse_url(url)

        # build the request string
        request_string = self.__build_request_header("GET")

        print(request_string)  # required print statement

        # send the request string and get response
        response_string = self.__send_request(request_string)

        # get header data from response
        parsed_data = self.__parse_response_header(response_string)

        # print specific header data as specified for the project
        self.print_parsed_data(parsed_data)

        # store the response IF we received a 2xx response
        # these files are stored prefixed with a "__" to distinguish them from other files in the system.
        # the stored file name will be "__{hostname}{filepath}"
        if 200 <= parsed_data['response_code'] < 300:
            self.store_body(parsed_data['body'])

    def PUT(self, url, file_path):
        # Validate parameters (url and local filepath)
        if not self.__validate_url(url):
            exit("ERR - arg 2")
        if not os.path.isfile(file_path):
            exit("ERR - arg 3")

        # Get local file
        file_content = "\r\n".join(open(file_path).readlines())

        # parse url into self.host self.path
        self.__parse_url(url)

        # build the request string
        # this request must append header with a body of file content
        request_string = self.__build_request_header("PUT") + file_content + "\r\n\r\n"

        print(request_string)  # required print statement

        # send the request string and get response
        response_string = self.__send_request(request_string)

        # get header data from response
        parsed_data = self.__parse_response_header(response_string)

        # print specific header data as specified for the project
        self.print_parsed_data(parsed_data)

    def __validate_url(self, url):
        return url.startswith("http://")

    def __parse_url(self, url):
        # expecting http://hostname[:port][/path]
        m = re.match(r'http://([A-z0-9.]+)(:([0-9]+))?(/.*)?', url)

        # m.group(0) contains the whole url string, so we ignore it
        self.hostname = m.group(1)
        # m.group(2) contains the port WITH the colon at the beginning, so we ignore it
        self.port = int(m.group(3)) if m.group(3) else 80  # defaults to http port 80
        self.path = m.group(4) if m.group(4) else "/"  # defaults to base path

    def __build_request_header(self, method):
        return "{method} {path} HTTP/1.0\r\nHost: {hostname}\r\nUser-Agent: VCU-CMSC491\r\n\r\n" \
            .format(method=method, path=self.path, hostname=self.hostname)

    def __send_request(self, request_string):
        try:
            client_socket = socket(AF_INET, SOCK_STREAM)
            client_socket.connect((self.hostname, self.port))
            client_socket.send(request_string)
            server_sentence = client_socket.recv(1000000)
            client_socket.close()
            return server_sentence
        except:
            exit("ERR - Connection refused")

    def __parse_response_header(self, response_string):
        # Parse all metadata from the response string
        # Parsing (response_code, server) for all requests
        # For 2xx responses, we also parse (last-modified-date, content-length)
        # For 3xx responses, we als parse (redirect-location)
        # Additionally, for all of these parsed header values, I've set defaults of "Unknown"
        # because occasionally servers do not respond with all of the expected header components.
        header, body = response_string.split("\r\n\r\n", 1)

        # Get response code
        m = re.search(r'HTTP\/1\.[0-9] ([0-9]+)', header)
        response_code = int(m.group(1))

        # Get server name/type
        m = re.search('Server: (.*?)\r\n', header)
        server = m.group(1) if m is not None else "Unknown"

        # parse response header for 2xx responses
        if 200 <= response_code < 300:
            # Get last modified date
            m = re.search(r'Last-Modified: (.*?)\r\n', header)
            last_modified_date = m.group(1) if m is not None else "NOT SPECIFIED!"

            # Get content length
            m = re.search(r'Content-Length: (.*?)\r\n', header)
            content_length = m.group(1) if m is not None else "NOT SPECIFIED!"

            return {
                "response_code": response_code,
                "server": server,
                "last_modified_date": last_modified_date,
                "content_length": content_length,
                "header": header,
                "body": body,
            }

        # parse response header for 3xx responses
        if 300 <= response_code < 400:
            # Get redirect location
            m = re.search(r'Location: (.*?)\r\n', header)
            location = m.group(1)

            return {
                "response_code": response_code,
                "server": server,
                "location": location,
                "header": header,
                "body": body,
            }

        # Default not specified in project definition
        # This is useful if we receive a 606 for our "PUT" requests
        return {
            "response_code": response_code,
            "server": server,
            "header": header,
            "body": body,
        }

    def print_parsed_data(self, parsed_data):
        print(parsed_data['response_code'])  # required output
        print(parsed_data['server'])  # required output

        # Print fields from 2xx response codes
        if 200 <= parsed_data['response_code'] < 300:
            print(parsed_data['last_modified_date'])  # required output
            print(parsed_data['content_length'])  # required output

        # Print fields from 3xx response codes
        if 300 <= parsed_data['response_code'] < 400:
            print(parsed_data['location'])  # required output

        # Print the whole header
        print("\n" + parsed_data['header'])  # required output

    def store_body(self, body):
        # store file with appended "__" to distinguish it from the other files on the server
        # there weren't strong specification on how to store the file, so storing it with filename:
        # "__{hostname}{filepath}"
        filename = "__" + (".".join((self.hostname + self.path).split("/")))
        f = open(filename, "w+")
        f.write(body)
        f.close()


if __name__ == "__main__":
    # Get the command line arguments
    args = sys.argv

    client = HTTPClient()

    # If there are 2 arguments, we assume that the use is issuing a "GET" request
    if len(args) == 2:
        print(client.GET(args[1]))
        exit(0)

    # If there are 3 arguments, then the user is issuing something other than "GET"
    # We must also ensure that the middle parameter is "PUT", because this is the
    # only other method allowed from our client.
    if len(args) == 4 and args[1] == "PUT":
        print(client.PUT(args[2], args[3]))
        exit(0)

    # If we don't match the above command signatures, then the command wasn't entered as expected
    print("Usage: java HTTPClient URL or java HTTPClient PUT URL path/<filename>")
    exit(255)
