#!/util/bin/python3.7
#
# This file is part of CSE 489/589 Grader.
#
# CSE 489/589 Grader is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# CSE 489/589 Grader is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with CSE 489/589 Grader. If not, see <http://www.gnu.org/licenses/>.
#

import os
import socket

def procStatus(pid):
    for line in open("/proc/%d/status" % pid).readlines():
        if line.startswith("State:"):
            return line.split(":",1)[1].strip().split(' ')[0]

def kill(pid):
    os.system('kill -9 '+str(pid))

def read_logfile(binary, port):
    logfile = os.path.dirname(binary) + "/logs/assignment_log_" + socket.getfqdn().split('.')[0] + "_" + str(port) + ".log"
    
    # Debugging output for logfile path
    print("Logfile path: {}".format(logfile))  
    print("Current working directory: {}".format(os.getcwd()))  

    if os.path.isfile(logfile):
        print("[DEBUG] Logfile found. Attempting to read...")
        try:
            with open(logfile, 'r') as f:
                content = f.read()
                print(f"[DEBUG] Logfile content:\n{content}")
                return content
        except Exception as e:
            # Handle any errors while reading the file
            print(f"[ERROR] Failed to read logfile: {str(e)}")
            return f"Error reading logfile: {str(e)}"
    else:
        return 'NoLogFile'
