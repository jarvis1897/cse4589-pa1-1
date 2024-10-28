#!/util/bin/python3.7

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

def inspect_tarball(filename):
    """Inspect the contents of the tarball."""
    try:
        tar_path = os.path.join(udir, filename)
        with tarfile.open(tar_path) as tar:
            print("Contents of tarball:")
            for member in tar.getmembers():
                print(f" - {member.name}")
    except Exception as e:
        print(f"Failed to inspect tarball: {str(e)}")

def build_submission(filename):
    success = True
    try:
        student_dir = os.path.join(gdir, os.path.splitext(filename)[0])
        if not os.path.exists(student_dir):
            os.makedirs(student_dir)
            print(f"Created directory: {student_dir}")  # Debug statement

        tar_path = os.path.join(udir, filename)
        print(f"Extracting tarball: {tar_path} to {student_dir}")  # Debug statement
        
        # Inspect the tarball contents before extraction
        inspect_tarball(filename)

        tar = tarfile.open(tar_path)
        tar.extractall(path=student_dir)
        tar.close()
        print(f"Extraction completed: {os.listdir(student_dir)}")

        if filename.endswith('.py'):
            return success

        if os.system(f'cd {student_dir} && make clean && make') != 0:
            success = False

    except Exception as e:
        print(f"Error during build: {str(e)}")
        success = False

    return success


def init_grading_server(remote_grader_path, python, port):
    subprocess.Popen(f'cd {remote_grader_path};/util/bin/python3.7 grader_remote.py -p {port}', shell=True)


class HTTPHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed = urlparse(self.path)
        message = parse_qs(parsed.query)
        action = message.get('action', [None])[0]
        response = 'OK'
        summary = []

        try:
            if action == 'build':
                tarball = message.get('tarball', [None])[0]
                if not build_submission(tarball):
                    response = 'FAILED: Unable to build the submission. Check the tarball and its contents.'
                    summary.append(f"Build failed for tarball: {tarball}")
                else:
                    summary.append(f"Build succeeded for tarball: {tarball}")

            elif action == 'init':
                remote_grader_path = message.get('remote_grader_path', [None])[0]
                python = message.get('python', [None])[0]
                port = message.get('port', [None])[0]
                init_grading_server(remote_grader_path, python, port)
                summary.append(f"Initialized grading server at {remote_grader_path} on port {port}")

            elif action == 'get-gdir':
                response = gdir
                summary.append(f"Grading directory retrieved: {gdir}")

            elif action == 'terminate':
                port = message.get('port', [None])[0]
                os.system(f"kill -9 $(netstat -tpal | grep :{port} | awk '{{print $NF}}' | cut -d/ -f1) > /dev/null 2>&1")
                summary.append(f"Terminated grading server on port {port}")

        except Exception as e:
            response = f'FAILED: {str(e)}'
            summary.append(f"Error occurred: {str(e)}")

        self.send_response(200)
        self.end_headers()
        
        # Send both response and summary
        try:
            summary_message = "Summary:" + " ".join(summary)
            self.wfile.write((response + " " + summary_message).encode('utf-8'))
        except ValueError as e:
            print(f"Error writing response: {str(e)}")
        
        # summary_message = "Summary:\n" + "\n".join(summary)
        # self.wfile.write((response + "\n" + summary_message).encode('utf-8'))
        # self.wfile.close()


    def do_POST(self):
        parsed = cgi.FieldStorage(fp=self.rfile, headers=self.headers,
                                  environ={'REQUEST_METHOD': 'POST',
                                           'CONTENT_TYPE': self.headers['Content-Type']})

        submit_file = parsed['submit']
        upload_file(submit_file)
        
        summary_message = f"Uploaded file: {submit_file.filename}"

        self.send_response(200)
        self.end_headers()
        # Correct way to send summary
        self.wfile.write((b'OK\n' + summary_message.encode('utf-8')))


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

