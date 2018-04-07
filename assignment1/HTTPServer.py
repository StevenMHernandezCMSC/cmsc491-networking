import os
import sys
from datetime import datetime
from socket import *

import re


class HTTPServer:
    def listen(self, port):
        self._validate_port(port)

        # Create welcoming socket using the given port
        welcome_socket = socket(AF_INET, SOCK_STREAM)
        welcome_socket.bind(('', port))

        try:
            welcome_socket.listen(1)

            print('Listening on port', port)

            while 1:
                # Waits for some client to connect and creates new socket
                # for connection
                connection_socket, addr = welcome_socket.accept()
                print('Client Made Connection')
                client_ip, client_port = addr

                # Read input line from socket
                client_sentence = connection_socket.recv(1024)
                print('FROM CLIENT:', client_sentence)

                # Determine next action to take
                response_string = self.determine_response(client_ip, client_port, client_sentence)

                # Write output line to socket
                connection_socket.send(response_string)
                print('TO CLIENT', response_string)

                # Close the connection socket
                connection_socket.close()
        finally:
            welcome_socket.close()

    def _validate_port(self, port):
        if 0 >= port or port >= 65536:
            exit("ERR - arg 1")

    def determine_response(self, client_ip, client_port, client_sentence):
        server_response = ""
        method = self.get_method(client_sentence)

        print("{ip}:{port}:{method}".format(ip=client_ip, port=client_port, method=method))
        print(client_sentence)

        if method == "GET":
            server_response = self.GET(client_sentence)
        if method == "PUT":
            server_response = self.PUT(client_sentence)
        return server_response

    def get_method(self, client_sentence):
        if client_sentence.lower().startswith("get"):
            return "GET"
        if client_sentence.lower().startswith("put"):
            return "PUT"
        exit("ERR - unknown method")

    def build_response(self, response_code, response_message, response_body):
            return "\r\n".join([
                "HTTP/1.0 {} {}".format(response_code, response_message),
                "Server: CMSC491Server.v.1.0",
                "Content-Length: {}".format(len(response_body)),
                "Connection: close",
                "Content-Type: text/html;charset=utf-8",
                "",
                response_body,
            ])

    def GET(self, client_sentence):
        file_path = self.get_file_path_from_client_sentence(client_sentence)

        # Return 404 if the file does not exist currently
        if not os.path.isfile(file_path):
            return self.build_response(404, "Not Found", "404 Not Found")

        # Otherwise, we can return the file
        file_contents = "\r\n".join(open(file_path).readlines())

        return self.build_response(200, "OK", file_contents)

    def PUT(self, client_sentence):
        try:
            file_path = self.get_file_path_from_client_sentence(client_sentence)
            uploaded_file_content = client_sentence.split("\r\n", 1)[1]

            file = open(file_path, "w+")
            file.write(uploaded_file_content)
            file.close()

            return self.build_response(200, "OK File Created", "File Created")
        except:
            return self.build_response(606, "FAILED File NOT Created", "File NOT Created")

    def get_file_path_from_client_sentence(self, client_sentence):
        m = re.search(r'GET (.*) HTTP', client_sentence)
        path = m.group(1)

        # on a normal server, path `/` would indicate an `index.html` file.
        # (unless otherwise specified by the server such as apache, nginx etc.)
        # We will ignore that here though.

        # Additionally, on normal servers, we would want to protect certain servers
        # or other security risks such as in "GET /../../super_secret_file.txt HTTP:1/1"
        # which could potentially return any file on the server even if we don't want this.
        # Again, we will ignore the security aspects of this because this server will only
        # ever be run locally.
        print("." + path)
        return "." + path


if __name__ == "__main__":
    # Get the command line arguments
    args = sys.argv

    server = HTTPServer()
    server.listen(int(args[1]))

    print("\n\n\n\n")
