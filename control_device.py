#!/usr/bin/env python
import subprocess
import threading
import datetime
import time
import socket
import serial

import os
import signal
import psutil

from tkinter import *

################################################################################
# Close connection of localhost port
try:
    pid_ter = subprocess.run(
        ["sudo", "ss", "-lptn", "sport = :3000"], stdout=subprocess.PIPE)
    if ('127.0.0.1:3000' in pid_ter.stdout.decode('utf-8') and ('python3' in pid_ter.stdout.decode('utf-8'))):
        data = pid_ter.stdout.decode(
            'utf-8').split('\n')[1].split('pid')[1].split(',')[0].replace('=', '')
        do_kill = subprocess.run(
            ["sudo", "kill", "-9", data], stdout=subprocess.PIPE)
except:
    donothing = True
try:
    subprocess.call(["gnome-terminal", "--working-directory=/home/admin1/Desktop/collect/",
                    "-x", "bash", "-c", "./Collect"])
except:
    donothing = True
################################################################################
################################################################################
# Make serial connection
try:
    serial_read_indicator = serial.Serial(
        '/dev/ttyUSB0', baudrate=9600, timeout=2)
except:
    donothing = True
################################################################################
################################################################################
# init first parameter from init parameter file
try:
    file1 = open('parameter.txt', 'r')
    dict_init = {}
    for line in file1:
        line = line.strip()
        list_line = line.split(' = ')
        dict_init[list_line[0]] = list_line[1]
    file1.close()
    # time zone
    init_timer_dws = int(dict_init['init_timer_dws'])
    # Init weight
    init_time_rsl = float(dict_init['init_time_rsl'])
    init_count = int(dict_init['init_count'])
    init_thresh_weight = int(dict_init['init_thresh_weight'])
    # Init Dim Cam and Weight
    packing_1 = list(dict_init['packing_1'])
    packing_2 = list(dict_init['packing_2'])
    packing_3 = list(dict_init['packing_3'])
    init_thresh_cam = int(dict_init['init_thresh_cam'])
    # Get init TID for testig
    list_tid = list(dict_init['list_tid'])
except:
    # Default setting
    init_timer_dws = 7200

    init_time_rsl = 0.2
    init_count = 10
    init_thresh_weight = 30

    packing_1 = [40700, 25800, 20800, 810]
    packing_2 = [43000, 27000, 22000, 1220]
    packing_3 = [41000, 37000, 29000, 2270]

    init_thresh_cam = 1000

    list_tid = ['A', 'B', 'C']
################################################################################
#Run checking internet and memory
checking_status = subprocess.run(
    ['checking_status.py'], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)
################################################################################

check_weight_done = False
init_weight = 0
weight_sta = False

init_cam_lenght = 0
init_cam_width = 0
init_cam_height = 0

time_check_back = datetime.datetime.now()
time_sta = False
got_check = False
need_get_cam_data = False

need_close_sta = False
pos = False
data_check_sta = False

################################################################################
# Network_TCP
# FROM COLLECT TOOL
# Listen signal
bufferSize = 1024
################################################################################
# Local host infomation
HOST = "127.0.0.1"
PORT = 3000
################################################################################
# Camera infomation (TCP server)
ip_CAMERA = "192.168.1.108"
port_CAMERA = 3000
FORMAT = "utf-8"

################################################################################


def init_time():
    global current_time, time_sta, init_timer_dws, time_check_back
    current_time = datetime.datetime.now()
    time_check_back = current_time + \
        datetime.timedelta(seconds=init_timer_dws)
    time_sta = True
    # print('Time Start: ' + str(current_time))
    # print('Time check back: ' + str(time_check_back))
    control_dws(True)


def confirm_packing(data):
    global init_weight, init_cam_lenght, init_cam_width, init_cam_height
    try:
        init_weight = int(data[3])
        init_cam_lenght = int(data[0])
        init_cam_width = int(data[1])
        init_cam_height = int(data[2])
    except:
        init_weight = 810
        init_cam_lenght = 40700
        init_cam_width = 25800
        init_cam_height = 20800


def control_dws(sta):
    if (sta):
        try:
            open = subprocess.Popen(["ninjavan"])
        except:
            print("execute ninjavan err")
    else:
        try:
            for pid in (process.pid for process in psutil.process_iter() if process.name() == "electron"):
                os.kill(pid, signal.SIGTERM)
            for pid in (process.pid for process in psutil.process_iter() if process.name() == "node"):
                os.kill(pid, signal.SIGTERM)
        except Exception as e:
            print("close ninjavan err ", e)


def need_close_dws():
    global time_sta, got_check, pos, check_weight_done
    check_weight_done = False
    time_sta = False
    got_check = False
    control_dws(False)
    if (pos):
        checking_mes_UI('TỚI GIỜ KIỂM TRA!', True)
    else:
        checking_mes_UI('SAI DỮ LIỆU MẪU!', False)

################################################################################
# UI function


def checking_mes_UI(data, sta):
    alarm_ui = Tk()
    alarm_ui.title('Message')
    alarm_ui.attributes('-fullscreen', True)
    alarm_ui.attributes('-topmost', True)
    if ('Try again' in data) or ('TỚI GIỜ' in data):
        alarm_ui.configure(background='yellow')
        mes_ui_4 = Label(alarm_ui, text="               ", font=(
            'Arial Black', 30, "bold"), background='yellow')
        mes_ui_4.pack()
        mes_ui_1 = Label(alarm_ui, text='THÔNG BÁO', font=(
            'Arial Black', 70), background='yellow')
        mes_ui_1.pack()
        mes_ui_3 = Label(alarm_ui, text="               ", font=(
            'Arial Black', 400, "bold"), background='yellow')
        mes_ui_3.pack()
        mes_ui_2 = Label(alarm_ui, text=data, font=(
            'Arial Black', 100), background='yellow')
        mes_ui_2.pack(fill='both', expand=True)
        alarm_ui.after(3000, lambda: alarm_ui.destroy())
        alarm_ui.mainloop()
    else:
        if not (sta):
            alarm_ui.configure(background='red')
            mes_ui_4 = Label(alarm_ui, text="               ", font=(
                'Arial Black', 30, "bold"), background='red')
            mes_ui_4.pack()
            mes_ui_1 = Label(alarm_ui, text='THÔNG BÁO', font=(
                'Arial Black', 70), background='red')
            mes_ui_1.pack()
            mes_ui_3 = Label(alarm_ui, text="               ", font=(
                'Arial Black', 400, "bold"), background='red')
            mes_ui_3.pack()
            mes_ui_2 = Label(alarm_ui, text=data, font=(
                'Arial Black', 100), background='red')
            mes_ui_2.pack(fill='both', expand=True)
            alarm_ui.after(3000, lambda: alarm_ui.destroy())
            alarm_ui.mainloop()

################################################################################


def recv_camera(weight_sta, init_cam_lenght, init_cam_width, init_cam_height, init_thresh_cam):
    global got_check, pos, check_weight_done, need_close_sta
    mes_recv_CAM = ''
    try:
        while mes_recv_CAM == '':
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((ip_CAMERA, port_CAMERA))
            mes_recv_CAM = client.recv(1024).decode(FORMAT)
            client.close()
    except:
        time.sleep(3)
        pos = False
        need_close_sta = True
    if (mes_recv_CAM.split(';')[0] == 'volumeNum=0'):
        time.sleep(3)
        got_check = False
        pos = False
        need_close_sta = True
    else:
        arr_data = []
        arr_data_convert = [0.0000, 0.0000, 0.0000]
        try:
            data_list = mes_recv_CAM.split(',')
            arr_data = [data_list[1],
                        data_list[2], data_list[3]]
            for x in arr_data:
                list_ = x.split('=')
                data_1 = float(list_[1])
                d = arr_data.index(x)

                arr_data_convert[d] = round(
                    data_1/10, 3)
        except:
            arr_data_convert = [
                0.0000, 0.0000, 0.0000]
        upper_lenght = init_cam_lenght + init_thresh_cam
        lower_lenght = init_cam_lenght - init_thresh_cam

        upper_width = init_cam_width + init_thresh_cam
        lower_width = init_cam_width - init_thresh_cam

        upper_height = init_cam_height + init_thresh_cam
        lower_height = init_cam_height - init_thresh_cam
        if not ((arr_data_convert[0]*1000) in range(lower_lenght, upper_lenght) and
                (arr_data_convert[1]*1000) in range(lower_width, upper_width) and
                (arr_data_convert[2]*1000) in range(lower_height, upper_height) and
                (weight_sta == True)):
            time.sleep(3)
            pos = False
            need_close_sta = True
        else:
            got_check = True
        check_weight_done = False


def read_indicator(init_count, init_time_rsl, init_weight, init_thresh_weight):
    global check_weight_done, weight_sta
    ################################################################################
    arr_data = []
    count_get_sample = 0
    avg_data = 0
    while (count_get_sample < init_count):
        try:
            data = serial_read_indicator.read(8).hex()
            time.sleep(init_time_rsl)
            data_handle = ''
            for x in range(2, 14, 2):
                data_handle = data_handle + \
                    str(chr(int(data[x:x+2], 16)))
            data_handle = int(data_handle[::-1])
            arr_data.append(data_handle)
            count_get_sample = count_get_sample + 1
        except:
            weight_sta = True
    try:
        for x in arr_data:
            avg_data = avg_data + x
        avg_data = avg_data / init_count
        print('Khoi luong TB: ' + str(avg_data))
        upper_weight = init_weight + init_thresh_weight
        lower_weight = init_weight - init_thresh_weight
        if not (avg_data in range(lower_weight, upper_weight)):
            weight_sta = False
        else:
            weight_sta = True
    except:
        weight_sta = False
    init_time()
    time.sleep(1)
    check_weight_done = True


def time_check_DWS():
    global time_sta, current_time, time_check_back, pos, need_close_sta
    while (True):
        if (need_close_sta):
            need_close_dws()
            need_close_sta = False
        else:
            if (time_sta == True):
                current_time = datetime.datetime.now()
                if (current_time > time_check_back):
                    pos = True
                    need_close_sta = True


def control_data_recv(mes_recv_sta):
    global packing_1, packing_2, packing_3, got_check,\
        init_count, init_time_rsl, init_weight, init_thresh_weight, weight_sta,\
        list_tid, data_check_sta
    if (mes_recv_sta == 'A'):
        confirm_packing(
            packing_1)
    elif (mes_recv_sta == 'B'):
        confirm_packing(
            packing_2)
    elif (mes_recv_sta == 'C'):
        confirm_packing(
            packing_3)
    elif (mes_recv_sta == 'SKIP'):
        got_check = True
        init_time()
    elif (mes_recv_sta == 'RESET01'):
        subprocess.run(
            ["shutdown", "-r", "now"])
    else:
        if not data_check_sta:
            got_check = True
            init_time()
        else:
            if not got_check:
                checking_mes_UI(
                    'CẦN KIỂM TRA DIM!', False)
    data_check_sta = True
    if (mes_recv_sta in list_tid):
        read_indicator(
            init_count, init_time_rsl, init_weight, init_thresh_weight)


def socket_recv():
    global check_weight_done, data_check_sta, pos, got_check,\
        packing_1, packing_2, packing_3,\
        time_check_back, current_time,  time_sta,\
        init_count, init_time_rsl, init_weight, init_thresh_weight, weight_sta,\
        init_cam_lenght, init_cam_width, init_cam_height, init_thresh_cam
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen()
            while True:
                try:
                    conn, addr = s.accept()
                    with conn:
                        while True:
                            try:
                                mes_recv = conn.recv(
                                    1024).decode(encoding=FORMAT)
                                if not mes_recv:
                                    break
                                if ('_' in mes_recv):
                                    list_mes_recv = mes_recv.split('_')
                                    mes_recv_sta = list_mes_recv[1]
                                    if (mes_recv_sta != ''):
                                        if (check_weight_done == False):
                                            control_data_recv(mes_recv_sta)
                                        else:
                                            if (mes_recv_sta in list_tid):
                                                recv_camera(
                                                    weight_sta, init_cam_lenght, init_cam_width, init_cam_height, init_thresh_cam)
                            except:
                                donothing = True
                except:
                    donothing = True
    except:
        donothing = True

################################################################################


thread_check_main = threading.Thread(target=socket_recv)
thread_check_main.start()

thread_check_time = threading.Thread(target=time_check_DWS)
thread_check_time.start()
