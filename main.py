from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import mimetypes
import pathlib
import datetime
import json


class HttpHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == "/":
            self.send_html_file("static/index.html")
        elif pr_url.path == "/message.html":
            self.send_html_file("static/message.html")
        elif pathlib.Path().joinpath("static/" + pr_url.path[1:]).exists():
            self.send_static()
        else:
            self.send_html_file("static/error.html", 404)

    def do_POST(self):
        data = self.rfile.read(int(self.headers["Content-Length"]))
        data_parse = urllib.parse.unquote_plus(data.decode())

        data_dict = {
            key: value for key, value in [el.split("=") for el in data_parse.split("&")]
        }
        MessageSaver().save_message(data_dict)

        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        with open(filename, "rb") as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", "text/plain")
        self.end_headers()
        with open(f"static{self.path}", "rb") as file:
            self.wfile.write(file.read())


class MessageSaver:
    def save_message(self, data):
        now = datetime.datetime.now()

        record = {now.__str__(): data}
        self.__write_into_file(record)

    def __write_into_file(self, data):
        filename = "storage/data.json"

        with open(filename, "r") as f:
            existing_json = json.load(f)

        existing_json.update(data)

        with open(filename, "w") as f:
            json.dump(existing_json, f, ensure_ascii=False, indent=4)


def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ("", 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


if __name__ == "__main__":
    run()
