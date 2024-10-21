#!/usr/bin/python3.7

# This file is part of CSE 489/589 Grader.
#
# CSE 489/589 Grader is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
# CSE 489/589 Grader is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; 
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with CSE 489/589 Grader. If not, see <http://www.gnu.org/licenses/>.

__author__ = "Swetank Kumar Saha (swetankk@buffalo.edu)"
__copyright__ = "Copyright (C) 2017 Swetank Kumar Saha"
__license__ = "GNU GPL"
__version__ = "2.0"
__contributor__ = "Ritik Ranjan (ritikran@buffalo.edu)"

from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from urllib.parse import urlparse, parse_qs
import argparse
import os
import cgi
import tarfile
import subprocess

parser = argparse.ArgumentParser(description='CSE 489/589 Grader Launcher v' + __version__)

requiredArgs = parser.add_argument_group('required named arguments')
requiredArgs.add_argument('-p', '--port', dest='port', type=int, nargs=1, help='server port', required=True)
requiredArgs.add_argument('-u', '--upload-dir', dest='upload_dir', type=str, nargs=1, help='upload directory', required=True)
requiredArgs.add_argument('-g', '--grade-dir', dest='grading_dir', type=str, nargs=1, help='grading directory', required=True)


def upload_file(submit_file):
    file_name = submit_file.filename
    file_data = submit_file.file.read()

    with open(os.path.join(udir, file_name), 'wb') as submission:
        submission.write(file_data)

    del file_data


def build_submission(filename):
    success = True
    try:
        student_dir = os.path.join(gdir, os.path.splitext(filename)[0])
        if not os.path.exists(student_dir):
            os.makedirs(student_dir)

        tar = tarfile.open(os.path.join(udir, filename))
        tar.extractall(path=student_dir)
        tar.close()

        if filename.endswith('.py'):
            return success

        if os.system(f'cd {student_dir} && make clean && make') != 0:
            success = False

    except Exception as e:
        print(f"Error during build: {str(e)}")
        success = False

    return success


def init_grading_server(remote_grader_path, python, port):
    subprocess.Popen(f'cd {remote_grader_path};{python} grader_remote.py -p {port}', shell=True)


class HTTPHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed = urlparse(self.path)
        message = parse_qs(parsed.query)
        action = message.get('action', [None])[0]
        response = 'OK'

        try:
            if action == 'build':
                tarball = message.get('tarball', [None])[0]
                if not build_submission(tarball):
                    response = 'FAILED'

            elif action == 'run-python':
                tarball = message.get('tarball', [None])[0]
                script_name = message.get('script', [None])[0]

                student_dir = os.path.join(gdir, os.path.splitext(tarball)[0])
                script_path = os.path.join(student_dir, script_name)

                result = subprocess.check_output(['python3', script_path]).decode('utf-8')
                response = result

            elif action == 'init':
                remote_grader_path = message.get('remote_grader_path', [None])[0]
                python = message.get('python', [None])[0]
                port = message.get('port', [None])[0]
                init_grading_server(remote_grader_path, python, port)

            elif action == 'get-gdir':
                response = gdir

            elif action == 'terminate':
                port = message.get('port', [None])[0]
                os.system(f"kill -9 $(netstat -tpal | grep :{port} | awk '{{print $NF}}' | cut -d/ -f1) > /dev/null 2>&1")

        except Exception as e:
            response = f'FAILED: {str(e)}'

        self.send_response(200)
        self.end_headers()
        self.wfile.write(response.encode('utf-8'))
        self.wfile.close()

    def do_POST(self):
        parsed = cgi.FieldStorage(fp=self.rfile, headers=self.headers,
                                  environ={'REQUEST_METHOD': 'POST',
                                           'CONTENT_TYPE': self.headers['Content-Type']})

        submit_file = parsed['submit']
        upload_file(submit_file)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'OK')
        self.wfile.close()


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass


if __name__ == '__main__':
    args = parser.parse_args()

    port = args.port[0]
    udir = args.upload_dir[0]
    gdir = args.grading_dir[0]

    os.system(f"kill -9 $(netstat -tpal | grep :{port} | awk '{{print $NF}}' | cut -d/ -f1) > /dev/null 2>&1")

    server = ThreadedHTTPServer(('0.0.0.0', port), HTTPHandler)
    server.serve_forever()
