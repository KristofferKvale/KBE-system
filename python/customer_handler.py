#!/usr/bin/python3

# Imports
# packages
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime

# local files
import db_coms
from product_checker import eval_chair

# Setting/getting global variables
# "Webpage" variables
HOST = "127.0.0.1"
PORT = 1234

# Folder variables
HOME_FOLDER = "D:/skole/KBE-system/chairs_project"
PYTHON_FOLDER = os.path.join(HOME_FOLDER, "python")
HTML_FOLDER = os.path.join(HOME_FOLDER, "html")
DATA_FOLDER = os.path.join(HOME_FOLDER, "data")
DFA_FOLDER = os.path.join(HOME_FOLDER, "DFAs")

# Customer variables, should be sent to/from customer each time
current_customer_id = 1
current_chair_id = 1

# DB setup/start up
print(os.path.join(DATA_FOLDER, "db.sqlite"))
db_connection = db_coms.create_connection(os.path.join(DATA_FOLDER, "db.sqlite"))
db_coms.setup(db_connection)


# Handeling requests
def send_file(handler, filepath, replace=[], replace_with=[]):
    file_index = open(filepath, 'r')
    content = file_index.read()
    for i in range(len(replace)):
        content = content.replace(replace[i], replace_with[i])
    handler.wfile.write(bytes(content, 'utf-8'))
    file_index.close()


class MyHandler(BaseHTTPRequestHandler):
    chair_id = current_chair_id

    def do_HEAD(self, response_code=200, content_type="text/html"):
        self.send_response(response_code)
        self.send_header("Content-type", content_type)
        self.end_headers()

    def do_GET(self):
        # Mapping the home page to customer page for now
        if self.path == "/":
            self.do_HEAD()
            send_file(self, os.path.join(HTML_FOLDER, "customer_page.html"))
        elif self.path.find("/newChair") != -1:
            if self.path.find("new=True") != -1:
                now = str(datetime.now())
                now = now.split(" ")
                success, self.chair_id = db_coms.add_chair(db_connection,
                                                           os.path.join(DATA_FOLDER, "DFAs", "temp_chair.dfa"), now[0])
            success, chair_values = db_coms.get_chair(db_connection, self.chair_id)
            replace_list = []
            replace_with_list = []
            if success:
                replace_list.append("<!--preview-->")
                replace_with_list.append(f"<p>chair info: {chair_values}")
            self.do_HEAD()
            send_file(self, os.path.join(HTML_FOLDER, "new_chair.html"), replace=replace_list,
                      replace_with=replace_with_list)
        else:
            if os.path.exists(os.path.join(HOME_FOLDER, self.path + ".html")):
                self.do_HEAD()
                send_file(self, os.path.join(HOME_FOLDER, self.path + ".html"))
            else:
                self.do_HEAD(response_code=404)

    def do_POST(self):

        content_len = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_len)
        content = post_body.decode()

        content_array = content.split('&')
        content_dict = {}
        for pair in content_array:
            pair = pair.split('=')
            content_dict[pair[0]] = pair[1]

        if self.path == "/saveChair":
            columns = ["sitting_height", "angle"]
            values = [int(content_dict["sitting_height"]), int(content_dict["back_angle"])]
            replace_list = []
            replace_with_list = []
            replace_list.append("<!--feedback-->")
            update_dfa = False
            if eval_chair(values[0], values[1]):
                success = db_coms.update_chair(db_connection, self.chair_id, columns, values)
                if success:
                    # make new dfa content
                    template_chair_file = open(os.path.join(DFA_FOLDER, "templates", "My_Chair_template.dfa"), 'r')
                    template_chair = template_chair_file.read()
                    template_chair = template_chair.replace("<PARAM_HEIGHT>", values[0])
                    template_chair = template_chair.replace("<PARAM_ANGLE>", values[1])
                    template_chair_file.close()
                    update_dfa = True
                    replace_with_list.append("<p>Chair saved.</p>")

                else:
                    replace_with_list.append("<p>Something went wrong while saving the chair to the database.</p>")
            else:
                replace_with_list.append("<p>Chair not following rules.</p><br>"
                                         + "<p>Sitting height needs to be between 50 and 80 cm.</p><br>"
                                         + "<p>Back angle needs to be between 5 and 15 degrees.")
            success, chair_values = db_coms.get_chair(db_connection, self.chair_id)
            if update_chair:
                # write to dfa file
                current_chair_file = open(chair_values[2], 'w')
                current_chair_file.write(template_chair)
                current_chair_file.close()
            
            if success:
                replace_list.append("<!--preview-->")
                replace_with_list.append(f"<p>chair info:</p><br>"
                                        + f"<p>Sitting height: {chair_values[0]} cm</p><br>"
                                        + f"<p>Back angle: {chair_values[1]} degrees</p>")
            self.do_HEAD()
            send_file(self, os.path.join(HTML_FOLDER, "new_chair.html"), replace=replace_list,
                      replace_with=replace_with_list)


# Main
if __name__ == '__main__':
    server_class = HTTPServer
    httpd = server_class((HOST, PORT), MyHandler)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
