# HTTP Server template / Chair example with sketch for manufacturability check
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
from Server import db_coms
import datetime
from os import path
import json
from pathlib import Path


config_file = open(Path(__file__).parent / "./config.json", 'r')
config = json.load(config_file)
config_file.close()
# TODO: Generalize
# HOME_FOLDER = 'C:/Users/kri_k/PycharmProjects/KBE-system/KBE-system'
HOME_FOLDER = config["config"][0]["folders"][0]["HOME"]

# TODO: Move to setup or config file
HOST_NAME = config["config"][1]["connections"][0]["HOST"]
PORT_NUMBER = config["config"][1]["connections"][0]["PORT"]
DFAPATH = config["config"][0]["folders"][1]["DFAs"]
TEMPLATES = config["config"][0]["folders"][2]["Templates"]
TEMPLATE_CHAIR = config["config"][0]["folders"][2]["Templates"][0]["Chair"]


# Check if chairs folder and template for chairs is set up correctly
if not path.exists(DFAPATH):
    print("Error: DFA Path not correct or not existing.")
    quit()

if not path.exists(TEMPLATES):
    print("Error: Could not find templates folder in the chosen DFA folder")
    quit()

if not path.exists(TEMPLATE_CHAIR):
    print("Error: Template chair file not found or has the wrong name.")
    quit()


FILE_TEMPLATE_CHAIR = open(TEMPLATE_CHAIR, "r")
FILE_TEMPLATE_CHAIR_CONTENT = FILE_TEMPLATE_CHAIR.read()
FILE_TEMPLATE_CHAIR.close()


# Connect to database, and make sure the chair table is there
db_connection = db_coms.create_connection(HOME_FOLDER + '/Server/db.sqlite')
db_coms.setup(db_connection)


def send_file(handler, filepath):
    file_index = open(filepath, 'r')
    handler.wfile.write(bytes(file_index.read(), 'utf-8'))
    file_index.close()


# Handler of HTTP requests / responses
class MyHandler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_GET(self):
        """Respond to a GET request."""
        self.do_HEAD()

        # Check what is the path
        path = self.path
        if path == '/':
            send_file(self, HOME_FOLDER + '/index.html')
        else:
            send_file(self, HOME_FOLDER + path + '.html')
        # elif path.find("/info") != -1:
        #     # TODO: Write Information html page
        #     # TODO: Replace with above file
        #     self.wfile.write(bytes('<html><head><title>Cool interface.</title></head>', 'utf-8'))
        #     self.wfile.write(bytes("<body><p>Current path: " + path + "</p>", "utf-8"))
        #     self.wfile.write(bytes("<body><p>Let's order a chair</p>", "utf-8"))
        #     self.wfile.write(bytes('</body></html>', "utf-8"))
        # elif path.find("/setLength") != -1:  # FIXME: Why have this???
        #     self.wfile.write(bytes('<html><body><h2>Chair</h2>', 'utf-8'))
        #     self.wfile.write(bytes('<form action="/setLength" method="post">', 'utf-8'))
        #     self.wfile.write(bytes('<label for="clength">Set Length:</label><br>', 'utf-8'))
        #     self.wfile.write(bytes('<input type="text" id="clength" name="clength" value="100"><br><br>', 'utf-8'))
        #     self.wfile.write(bytes('<input type="submit" value="Submit">', 'utf-8'))
        #     self.wfile.write(bytes('</form></body></html>', 'utf-8'))
        # elif path.find("/orderChair") != -1:
        #     # TODO: Make html file for value input
        #     # TODO: Replace with above file
        #     self.wfile.write(bytes('<html><body><h2>Chair</h2>', 'utf-8'))
        #     self.wfile.write(bytes('<form action="/orderChair" method="post">', 'utf-8'))
        #
        #     self.wfile.write(bytes('<label for="cside">Set Side of the chair (outer):</label><br>', 'utf-8'))
        #     self.wfile.write(bytes('<input type="text" id="cside" name="cside" value="1500"><br><br>', 'utf-8'))
        #     self.wfile.write(bytes('<label for="cdepth">Set Depth for the seat:</label><br>', 'utf-8'))
        #     self.wfile.write(bytes('<input type="text" id="cdepth" name="cdepth" value="1100"><br><br>', 'utf-8'))
        #     self.wfile.write(bytes('<label for="cheight">Set Height for the seat:</label><br>', 'utf-8'))
        #     self.wfile.write(bytes('<input type="text" id="cheight" name="cheight" value="1100"><br><br>', 'utf-8'))
        #     self.wfile.write(bytes('<label for="cwidth">Set Width of the seat:</label><br>', 'utf-8'))
        #     self.wfile.write(bytes('<input type="text" id="cwidth" name="cwidth" value="1100"><br><br>', 'utf-8'))
        #
        #     self.wfile.write(bytes('<input type="submit" value="Submit">', 'utf-8'))
        #     self.wfile.write(bytes('</form></body></html>', 'utf-8'))
        # else:
        #     # FIXME: This seems to be the landing page, or a backup if shit aint workin
        #     self.wfile.write(bytes('<html><head><title>Cool interface.</title></head>', 'utf-8'))
        #     self.wfile.write(bytes("<body><p>The path: " + path + "</p>", "utf-8"))
        #     self.wfile.write(bytes('</body></html>', "utf-8"))

    def do_POST(self):

        self.do_HEAD()

        # Check what is the path
        path = self.path
        print("Path: ", path)

        content_len = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_len)
        content = post_body.decode()
        print('Body content: ', content)

        content_array = content.split('&')
        content_dict = {}
        for pair in content_array:
            pair = pair.split('=')
            content_dict[pair[0]] = pair[1]

        print(content_dict)

        # TODO: create chair file and write based on the template
        # Updating / writing DFA file
        # Set in parameters.
        file_content_out = FILE_TEMPLATE_CHAIR_CONTENT
        for i in content_dict.keys():
            file_content_out = file_content_out.replace(f"<PARAM_{content_dict.keys(i)}>",
                                                                   str(content_dict[i]))

        # Let's write the file
        datetime_now = datetime.datetime.now()
        file_current_chair = open(DFAPATH + f"My_Chair_{str(datetime_now).replace(' ', '')}.dfa", "w")
        file_current_chair.write(file_content_out)
        file_current_chair.close()

        # Add entry to database
        db_coms.add_chair(db_connection, file_current_chair, datetime_now)

        # TODO: get a preview and show that on the page



        # if path.find("/setLength") != -1:  # FIXME: Whats up with these not not find???
        #
        #     content_len = int(self.headers.get('Content-Length'))
        #     post_body = self.rfile.read(content_len)
        #     param_line = post_body.decode()
        #     print("Body: ", param_line)
        #
        #     # Get the param value
        #     pair = param_line.split("=")
        #
        #     self.wfile.write(bytes('<html><body><h2>Chair</h2>', 'utf-8'))
        #     self.wfile.write(bytes('<form action="/setLength" method="post">', 'utf-8'))
        #     self.wfile.write(bytes('<label for="clength">Set Length:</label><br>', 'utf-8'))
        #     self.wfile.write(
        #         bytes('<input type="text" id="clength" name="clength" value="' + pair[1] + '"><br><br>', 'utf-8'))
        #     self.wfile.write(bytes('<input type="submit" value="Submit">', 'utf-8'))
        #
        #     self.wfile.write(bytes('<p>The value of the length was set to ' + pair[1] + '</p>', 'utf-8'))
        #
        #     self.wfile.write(bytes('</form></body></html>', 'utf-8'))
        # elif path.find("/orderChair") != -1:
        #     global file_template_chair_content
        #
        #     content_len = int(self.headers.get('Content-Length'))
        #     post_body = self.rfile.read(content_len)
        #     param_line = post_body.decode()
        #     print("Body: ", param_line)
        #
        #     # Get the param value
        #     pairs = param_line.split("&")
        #     side_pair = pairs[0].split("=")
        #     depth_pair = pairs[1].split("=")
        #     height_pair = pairs[2].split("=")
        #     width_pair = pairs[3].split("=")
        #
        #     # Check if the parameters are in the range - manufacturability check
        #     # Integrating http Post method
        #     url = 'http://127.0.0.1:4321/orderChair'
        #     x = requests.post(url, data='a=1111&b=1234&c=1500&d=1600')
        #
        #     # Gettin and processing a reply
        #     reply_by_checker = x.text
        #
        #     if reply_by_checker.find("NOK") != -1:
        #         # TODO - Tell customer not ok.
        #         print('not OK')
        #     else:
        #         # TODO - Normal reply.
        #         print('OK')
        #
        #     # Giving corresponding message to the customer.
        #
        #     self.wfile.write(bytes('<html><body><h2>Chair</h2>', 'utf-8'))
        #     self.wfile.write(bytes('<form action="/orderChair" method="post">', 'utf-8'))
        #
        #     self.wfile.write(bytes(
        #         '<p>The following parameters have arrived: ' + str(side_pair[1]) + ', ' + str(depth_pair[1]) + ', ' + str(
        #             height_pair[1]) + ', ' + str(width_pair[1]) + '</p>', 'utf-8'))
        #
        #     self.wfile.write(bytes('<label for="cside">Set Side of the chair (outer):</label><br>', 'utf-8'))
        #     self.wfile.write(
        #         bytes('<input type="text" id="cside" name="cside" value="' + str(side_pair[1]) + '"><br><br>', 'utf-8'))
        #     self.wfile.write(bytes('<label for="cdepth">Set Depth for the seat:</label><br>', 'utf-8'))
        #     self.wfile.write(
        #         bytes('<input type="text" id="cdepth" name="cdepth" value="' + str(depth_pair[1]) + '"><br><br>',
        #               'utf-8'))
        #     self.wfile.write(bytes('<label for="cheight">Set Height for the seat:</label><br>', 'utf-8'))
        #     self.wfile.write(
        #         bytes('<input type="text" id="cheight" name="cheight" value="' + str(height_pair[1]) + '"><br><br>',
        #               'utf-8'))
        #     self.wfile.write(bytes('<label for="cwidth">Set Width of the seat:</label><br>', 'utf-8'))
        #     self.wfile.write(
        #         bytes('<input type="text" id="cwidth" name="cwidth" value="' + str(width_pair[1]) + '"><br><br>',
        #               'utf-8'))
        #
        #     self.wfile.write(bytes('<input type="submit" value="Submit">', 'utf-8'))
        #     self.wfile.write(bytes('</form></body></html>', 'utf-8'))
        #
            # # Updating / wiring DFA file
            # # Set in parameters.
            # file_content_out = file_template_chair_content.replace("<PARAM_SIDE>", str(side_pair[1]))
            # file_content_out = file_content_out.replace("<PARAM_DEPTH>", str(depth_pair[1]))
            # file_content_out = file_content_out.replace("<PARAM_WIDTH>", str(height_pair[1]))
            # file_content_out = file_content_out.replace("<PARAM_HEIGHT>", str(width_pair[1]))
            #
            # # Let's write the file
            # file_current_chair = open(dfaPath + "My_Chair_210201.dfa", "w")
            # file_current_chair.write(file_content_out)
            # file_current_chair.close()


        #  In case of issues, redirect to index
        self.path = '/'
        self.do_GET()


if __name__ == '__main__':
    server_class = HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
