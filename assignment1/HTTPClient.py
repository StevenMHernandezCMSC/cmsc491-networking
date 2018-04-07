import sys
from socket import *

import re


class HTTPClient:
    def get(self, url):
        if not self.__validate_url(url):
            exit("ERR - arg 1")
        self.__parse_url(url)
        request_string = self.__build_request_string()
        print(request_string)
        response_string = self.__send_request(request_string)
        parsed_data = self.__parse_response_header(response_string)
        self.print_parsed_data(parsed_data)
        if 200 <= parsed_data['response_code'] < 300:
            self.store_body(parsed_data['body'])

    def put(self):
        pass

    def __validate_url(self, url):
        return url.startswith("http://")

    def __parse_url(self, url):
        # http://hostname[:port][/path]
        m = re.match(r'http://([A-z0-9.]+)(:([0-9]+))?(/.*)?', url)

        # m.group(0) contains the whole url string, so we ignore it
        self.hostname = m.group(1)
        # m.group(2) contains the port WITH the colon at the beginning, so we ignore it
        self.port = int(m.group(3)) if m.group(3) else 80  # defaults to http port 80
        self.path = m.group(4) if m.group(4) else "/"  # defaults to base path

    def __build_request_string(self):
        return "GET {path} HTTP/1.0\r\nHost: {hostname}\r\nUser-Agent: VCU-CMSC4491\r\n\r\n" \
            .format(path=self.path, hostname=self.hostname)

    def __send_request(self, request_string):
        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket.connect((self.hostname, self.port))
        client_socket.send(request_string)
        server_sentence = client_socket.recv(1000000)
        client_socket.close()
        return server_sentence

    def __parse_response_header(self, response_string):
        header, body = response_string.split("\r\n\r\n", 1)
        m = re.search(r'HTTP/1\.[0-9] ([0-9]+)', header)
        response_code = int(m.group(1))
        m = re.search('Server: (.*?)\r\n', header)
        server = m.group(1)

        # parse response header for 2xx responses
        if 200 <= response_code < 300:
            m = re.search(r'Last-Modified: (.*?)\r\n', header)
            last_modified_date = m.group(1) if m is not None else "NOT SPECIFIED!"
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
            m = re.search(r'Location: (.*?)\r\n', header)
            location = m.group(1)
            return {
                "response_code": response_code,
                "server": server,
                "location": location,
                "header": header,
                "body": body,
            }

    def print_parsed_data(self, parsed_data):
        print("Response Code: {}".format(parsed_data['response_code']))
        print("Server: {}".format(parsed_data['server']))

        # Print fields from 2xx response codes
        if 200 <= parsed_data['response_code'] < 300:
            print("Last-Modified: {}".format(parsed_data['last_modified_date']))
            print("Content-Length: {}".format(parsed_data['content_length']))

        # Print fields from 3xx response codes
        if 300 <= parsed_data['response_code'] < 400:
            print("Location: {}".format(parsed_data['location']))

        # Print the whole header
        print("\n" + parsed_data['header'])

    def store_body(self, body):
        filename = "__" + (".".join((self.hostname + self.path).split("/")))
        f = open(filename, "w+")
        f.write(body)
        f.close()


if __name__ == "__main__":
    # Get the command line arguments
    args = sys.argv

    client = HTTPClient()
    client.get(args[1])
