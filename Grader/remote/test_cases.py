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

import subprocess
import os
import time
import ast

from utils import *
    
def grade_startup(py_script, s_or_c, port):
    # command = binary+" "+s_or_c+" "+str(port)
    command = f"python3.7 {py_script} {s_or_c} {port}"
    process = subprocess.Popen(command, shell=True, stdout=open(os.devnull, 'w'), stderr=subprocess.STDOUT)
    time.sleep(2)
    status = procStatus(process.pid)
    if status in ['R', 'S']:
        kill(process.pid)
        return True
    return False

def grade_author(py_script, s_or_c, port):
    print(f"py_script: {py_script}, s_or_c: {s_or_c}, port: {port}")
    command = f"expect -f author.exp {py_script} {s_or_c} {port}"
    print(f"Executing command: {command}")
    process = subprocess.Popen(command, shell=True, stdout=open(os.devnull, 'w'), stderr=subprocess.STDOUT)

    time.sleep(3)
    kill(process.pid)

    log = read_logfile(py_script, port)
    print(f"log: {log}")
    return log

def grade_ip(py_script, s_or_c, port):
    print(f"py_script: {py_script}, s_or_c: {s_or_c}, port: {port}")
    command = f"expect -f ip.exp {py_script} {s_or_c} {port}"
    print(f"Executing command: {command}")
    process = subprocess.Popen(command, shell=True)

    time.sleep(2)
    kill(process.pid)

    log = read_logfile(py_script, port)
    print(f"log: {log}")
    return log

def grade_port(py_script, s_or_c, port):
    print(f"py_script: {py_script}, s_or_c: {s_or_c}, port: {port}")
    command = f"expect -f port.exp {py_script} {s_or_c} {port}"
    print(f"Executing command: {command}")
    process = subprocess.Popen(command, shell=True, stdout=open(os.devnull, 'w'), stderr=subprocess.STDOUT)

    time.sleep(2)
    kill(process.pid)

    log = read_logfile(py_script, port)
    print(f"log: {log}")
    return log

def grade_list(py_script, s_or_c, port, s_ip="", s_port=""):
    if s_or_c == 's':
        command = f"expect -f list_server.exp {py_script} {s_or_c} {port}"
    else:
        command = f"expect -f list_client.exp {py_script} {s_or_c} {port} {s_ip} {s_port}"
    process = subprocess.Popen(command, shell=True, close_fds=True)

    if s_or_c == 's': time.sleep(15)
    else: time.sleep(2)

    return read_logfile(py_script, port)

def grade_refresh(py_script, s_or_c, port, s_ip, s_port):
    # command = "expect -f refresh_client.exp "+binary+" "+s_or_c+" "+str(port)+" "+s_ip+" "+s_port
    command = f"expect -f refresh_client.exp {py_script} {s_or_c} {port} {s_ip} {s_port}"
    process = subprocess.Popen(command, shell=True)
    time.sleep(8)
    kill(process.pid)
    return read_logfile(py_script, port)

def grade_send(py_script, s_or_c, port, s_ip="", s_port=""):
    if s_or_c == 's':
        command = f"expect -f send_server.exp {py_script} {s_or_c} {port}"
    else:
        command = f"expect -f send_client_r.exp {py_script} {s_or_c} {port} {s_ip} {s_port}"
    process = subprocess.Popen(command, shell=True)
    time.sleep(15)
    kill(process.pid)
    return read_logfile(py_script, port)

def ssend(py_script, s_or_c, port, s_ip, s_port, sender_string):
    sender_info = ast.literal_eval(sender_string)
    command = f"expect -f send_client_s.exp {py_script} {s_or_c} {port} {s_ip} {s_port} {' '.join(sender_info)}"
    process = subprocess.Popen(command, shell=True)
    time.sleep(12)
    kill(process.pid)
    return read_logfile(py_script, port)

def grade_broadcast(py_script, s_or_c, port, s_ip, s_port, num_messages, msg):
    command = f"expect -f broadcast_client_s.exp {py_script} {s_or_c} {port} {s_ip} {s_port} {num_messages} {msg}"
    process = subprocess.Popen(command, shell=True)
    time.sleep(12)
    kill(process.pid)
    return read_logfile(py_script, port)

def grade_block(py_script, s_or_c, port, s_ip, s_port, server_to_send):
    command = f"expect -f blocked_client.exp {py_script} {s_or_c} {port} {s_ip} {s_port} {server_to_send}"
    process = subprocess.Popen(command, shell=True)
    time.sleep(7)
    kill(process.pid)
    return read_logfile(py_script, port)

def sblock(py_script, s_or_c, port, s_ip, s_port, target):
    command = f"expect -f block_server.exp {py_script} {s_or_c} {port} {s_ip} {s_port} {target}"
    process = subprocess.Popen(command, shell=True)
    time.sleep(8)
    kill(process.pid)
    return read_logfile(py_script, port)

def bblock(py_script, s_or_c, port, s_ip, s_port, target):
    command = f"expect -f block_client.exp {py_script} {s_or_c} {port} {s_ip} {s_port} {target}"
    process = subprocess.Popen(command, shell=True)
    time.sleep(8)
    kill(process.pid)
    return read_logfile(py_script, port)

def grade_blocked(py_script, s_or_c, port, s_ip="", s_port=""):
    command = f"expect -f blocked_server.exp {py_script} {s_or_c} {port} {s_ip} {s_port}"
    process = subprocess.Popen(command, shell=True)
    time.sleep(8)
    kill(process.pid)
    return read_logfile(py_script, port)

def ablocked(py_script, s_or_c, port, s_ip, s_port, target):
    command = f"expect -f blocked_client.exp {py_script} {s_or_c} {port} {s_ip} {s_port} {target}"
    process = subprocess.Popen(command, shell=True)
    time.sleep(7)
    kill(process.pid)
    return read_logfile(py_script, port)

def grade_unblock(py_script, s_or_c, port, s_ip, s_port, target):
    command = f"expect -f unblock_server.exp {py_script} {s_or_c} {port} {s_ip} {s_port} {target}"
    process = subprocess.Popen(command, shell=True)
    time.sleep(5)
    kill(process.pid)
    return read_logfile(py_script, port)

def uunblock(py_script, s_or_c, port, s_ip, s_port, target):
    command = f"expect -f unblock_client.exp {py_script} {s_or_c} {port} {s_ip} {s_port} {target}"
    process = subprocess.Popen(command, shell=True)
    time.sleep(5)
    kill(process.pid)
    return read_logfile(py_script, port)

def grade_logout(py_script, s_or_c, port, s_ip, s_port):
    command = f"expect -f logout_client.exp {py_script} {s_or_c} {port} {s_ip} {s_port}"
    process = subprocess.Popen(command, shell=True)
    time.sleep(4)
    kill(process.pid)
    return read_logfile(py_script, port)

def grade_buffer(py_script, s_or_c, port, s_ip="", s_port=""):
    command = f"expect -f buffer_server.exp {py_script} {s_or_c} {port} {s_ip} {s_port}"
    process = subprocess.Popen(command, shell=True)
    time.sleep(12)
    kill(process.pid)
    return read_logfile(py_script, port)

def sbuffer(py_script, s_or_c, port, s_ip, s_port, sender_string):
    sender_info = ast.literal_eval(sender_string)
    command = f"expect -f buffer_client.exp {py_script} {s_or_c} {port} {s_ip} {s_port} {' '.join(sender_info)}"
    process = subprocess.Popen(command, shell=True)
    time.sleep(10)
    kill(process.pid)
    return read_logfile(py_script, port)

def grade_exit(py_script, s_or_c, port):
    command = f"python3.7 {py_script} {s_or_c} {port}"
    process = subprocess.Popen(command, shell=True, stdout=open(os.devnull, 'w'), stderr=subprocess.STDOUT)
    time.sleep(2)
    status = procStatus(process.pid)
    if status in ['R', 'S']:
        kill(process.pid)
        command = f"expect -f exit.exp {py_script} {s_or_c} {port}"
        process = subprocess.Popen(command, shell=True, stdout=open(os.devnull, 'w'), stderr=subprocess.STDOUT)
        time.sleep(2)
        status = procStatus(process.pid)
        kill(process.pid)
        return status == 'Z'
    return False

def grade_statistics(py_script, s_or_c, port, s_ip="", s_port="", sender_string=""):
    if s_or_c == 's':
        command = f"expect -f statistics_server.exp {py_script} {s_or_c} {port}"
    else:
        sender_info = ast.literal_eval(sender_string)
        command = f"expect -f statistics_client_s.exp {py_script} {s_or_c} {port} {s_ip} {s_port} {' '.join(sender_info)}"
    process = subprocess.Popen(command, shell=True)
    time.sleep(16)
    kill(process.pid)
    return read_logfile(py_script, port)

def grade_exception_login(py_script, s_or_c, port):
    command = f"expect -f exception_login.exp {py_script} {s_or_c} {port}"
    process = subprocess.Popen(command, shell=True)
    time.sleep(15)
    kill(process.pid)
    return read_logfile(py_script, port)

def grade_exception_send(py_script, s_or_c, port, s_ip, s_port):
    command = f"expect -f exception_send.exp {py_script} {s_or_c} {port} {s_ip} {s_port}"
    process = subprocess.Popen(command, shell=True)
    time.sleep(5)
    kill(process.pid)
    return read_logfile(py_script, port)

def grade_exception_block(py_script, s_or_c, port, s_ip, s_port, server_to_block=""):
    if not server_to_block:
        command = f"expect -f exception_block_bd.exp {py_script} {s_or_c} {port} {s_ip} {s_port}"
    else:
        command = f"expect -f exception_block_bg.exp {py_script} {s_or_c} {port} {s_ip} {s_port} {server_to_block}"
    process = subprocess.Popen(command, shell=True)
    time.sleep(5)
    kill(process.pid)
    return read_logfile(py_script, port)

def grade_exception_unblock(py_script, s_or_c, port, s_ip, s_port, target):
    command = f"expect -f exception_unblock.exp {py_script} {s_or_c} {port} {s_ip} {s_port} {target}"
    process = subprocess.Popen(command, shell=True)
    time.sleep(5)
    kill(process.pid)
    return read_logfile(py_script, port)

def grade_exception_blocked(py_script, s_or_c, port, s_ip, s_port):
    command = f"expect -f exception_blocked.exp {py_script} {s_or_c} {port} {s_ip} {s_port}"
    process = subprocess.Popen(command, shell=True)
    time.sleep(5)
    kill(process.pid)
    return read_logfile(py_script, port)

def grade_bonus(py_script, s_or_c, port, s_ip="", s_port=""):
    if s_or_c == 's':
        command = f"expect -f bonus_server.exp {py_script} {s_or_c} {port}"
    else:
        folder = os.path.dirname(py_script)
        os.system(f'rm -f {folder}/cse4589test.txt {folder}/cse4589test.pdf')
        command = f"expect -f bonus_client_r.exp {py_script} {s_or_c} {port} {s_ip} {s_port}"
    process = subprocess.Popen(command, shell=True)
    time.sleep(15)
    kill(process.pid)
    return read_logfile(py_script, port)

def sbonus(py_script, s_or_c, port, s_ip, s_port, send_to_server):
    folder = os.path.dirname(py_script)
    os.system(f'cp -f cse4589test.txt {folder}')
    os.system(f'cp -f cse4589test.pdf {folder}')
    command = f"expect -f bonus_client_s.exp {py_script} {s_or_c} {port} {s_ip} {s_port} {send_to_server}"
    process = subprocess.Popen(command, shell=True)
    time.sleep(12)
    kill(process.pid)
    return 'DONE'

def cbonus(py_script, s_or_c, port, s_ip, s_port, server_to_send):
    command = f"expect -f cbonus.exp {py_script} {s_or_c} {port} {s_ip} {s_port} {server_to_send}"
    process = subprocess.Popen(command, shell=True)
    time.sleep(12)
    kill(process.pid)
    return 'DONE'
