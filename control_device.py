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
    init_timer_enet = int(dict_init['init_timer_enet'])
    # Control DWS
    init_open = int(dict_init['init_open'])
    init_close = int(dict_init['init_close'])
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
    # Init System
    init_picture_path = str(dict_init['init_picture_path'])
    init_timer_space = int(dict_init['init_timer_space'])
    init_space = int(dict_init['init_space'])
    # Init Network config
    wifi_default_name = str(dict_init['wifi_default_name'])
    wifi_4g_name = str(dict_init['wifi_4g_name'])
    wifi_pass = str(dict_init['wifi_pass'])
except:
    # Default setting
    init_timer_dws = 7200
    init_timer_enet = 120

    init_open = 3
    init_close = 2

    init_time_rsl = 0.2
    init_count = 10
    init_thresh_weight = 30

    packing_1 = [40700, 25800, 20800, 810]
    packing_2 = [43000, 27000, 22000, 1220]
    packing_3 = [41000, 37000, 29000, 2270]

    init_thresh_cam = 1000

    init_picture_path = '/home/admin1/Pictures/nvdws'
    init_timer_space = 18000
    init_space = 10

    wifi_default_name = 'Ninja Van'
    wifi_4g_name = 'dws4g'
    wifi_pass = 'Ninjav@nwifi!'
################################################################################
# Variable space
get_speed = '0.000'
LAN_to_wifi = False
wifi_driver = True
wifi_connecting = False

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


def enet_mes_UI(data, sta):
    global enet_ui
    enet_ui = Tk()
    enet_ui.title('Message from DWS Record')
    enet_ui.geometry("775x140+100+200")
    if ('Connecting' in data):
        enet_ui.configure(background='yellow')
        mes_txt = Label(enet_ui, text=data, font=(
            'Arial Black', 30), background='yellow')
    else:
        if (sta):
            enet_ui.configure(background='green')
            mes_txt = Label(enet_ui, text=data, font=(
                'Arial Black', 30), background='green')
        else:
            enet_ui.configure(background='red')
            mes_txt = Label(enet_ui, text=data, font=(
                'Arial Black', 60), background='red')
    mes_txt.pack(fill='both', expand=True)
    enet_ui.after(3000, lambda: enet_ui.destroy())
    enet_ui.mainloop()


def memory_mes_UI(data):
    global memory_ui
    memory_ui = Tk()
    memory_ui.title('Message from DWS Record')
    memory_ui.attributes('-fullscreen', True)
    memory_ui.configure(background='red')
    mes_ui_1 = Label(memory_ui, text=data, font=(
        'Arial Black', 100), background='red')
    mes_ui_1.pack()
    mes_ui_3 = Label(memory_ui, text="               ", font=(
        'Arial Black', 200, "bold"), background='red')
    mes_ui_3.pack()
    mes_ui_2 = Label(memory_ui, text="Refreshing Data", font=(
        'Arial Black', 150, "bold"), background='red')
    mes_ui_2.pack()

    memory_ui.after(60000, lambda: memory_ui.destroy())
    memory_ui.mainloop()


################################################################################

def resfresh_wifi():
    subprocess.run("nmcli radio wifi off",
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    time.sleep(2)
    subprocess.run("nmcli radio wifi on",
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    time.sleep(10)


def verify_wifi_sta():
    global LAN_to_wifi, wifi_connecting
    time.sleep(15)
    ver_wifi = subprocess.run(["curl", "-I", "https://linuxhint.com/"],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=1.5)
    ver_wifi_mes = ver_wifi.stdout.decode(encoding='utf-8')
    if (ver_wifi_mes == ''):
        raise Exception
    LAN_to_wifi = True
    wifi_connecting = False


def verify_interrupt_sta():
    global wifi_connecting
    time.sleep(3)
    try:
        ver_net = subprocess.run(["curl", "-I", "https://linuxhint.com/"],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=2)
        ver_net_mes = ver_net.stdout.decode(encoding='utf-8')
        if (ver_net_mes == ''):
            raise Exception
    except Exception:
        wifi_connecting = True
        enet_mes_UI(
            'Connecting to Wifi, Please wait', True)


def get_speed_net():
    global get_speed, LAN_to_wifi, wifi_driver, net_sta, \
        init_timer_enet, wifi_pass, wifi_default_name, wifi_4g_name, wifi_connecting
    while (True):
        try:
            check_net = subprocess.run(["curl", "-I", "https://linuxhint.com/"],
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=3)
            check_net_mes = check_net.stdout.decode(encoding='utf-8')
            if not ('HTTP/2 200' in check_net_mes):
                raise Exception
            try:
                response_speed = subprocess.Popen(
                    '/usr/bin/speedtest', shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
                index_fst = response_speed.find('Download: ')
                index_ser = response_speed.find('Mbit/s')
                get_speed = response_speed[index_fst +
                                           9:index_ser-1].strip()
                get_speed_con = float(get_speed)
            except:
                raise Exception

            if (LAN_to_wifi == True) and (get_speed_con >= 70):
                subprocess.run("nmcli radio wifi off",
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                LAN_to_wifi = False
                time.sleep(10)
                enet_mes_UI('LAN network is Back', True)
            print('Internet is good: Speed ' +
                  str(get_speed) + 'Mbit/s')
            time.sleep(init_timer_enet)
        except Exception:
            verify_interrupt_sta()
            time.sleep(1)
            if wifi_connecting:
                password = r'{}'.format(wifi_pass)
                try:
                    resfresh_wifi()
                    output = subprocess.check_output(
                        ['nmcli d wifi connect "{wifi_default_name}" password "{password}"'.format(
                            wifi_default_name=wifi_default_name, password=password)],
                        shell=True
                    ).decode('utf-8')
                    verify_wifi_sta()
                    enet_mes_UI('NinjaVan Wifi has connected', True)
                except Exception:
                    try:
                        resfresh_wifi()
                        output_4g = subprocess.check_output(
                            ['nmcli d wifi connect "{wifi_4g_name}" password "{password}"'.format(
                                wifi_4g_name=wifi_4g_name, password=password)],
                            shell=True
                        ).decode('utf-8')
                        verify_wifi_sta()
                        enet_mes_UI('4G Wifi has connected', True)
                    except Exception:
                        enet_mes_UI('Network is Crash', False)


def Alarm_free_space():
    global init_timer_space, init_space
    while (True):
        p = subprocess.run(["df", "-h"],
                           stdout=subprocess.PIPE)
        respone_space = p.stdout.decode("utf-8")
        available_space = respone_space.split(
            '\n')[3].split('       ')[1].split('  ')[2]
        free_use = available_space.replace('G', '')
        free_use = float(free_use)
        if (free_use < init_space):
            # print('Disk in Alarm')
            memory_mes_UI('Disk in Alarm')
        else:
            print('Still able in using (Free in use: ' + available_space + ')')
        time.sleep(init_timer_space)

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
                                            if (data_check_sta == True):
                                                control_data_recv(mes_recv_sta)
                                            else:
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

thread_check_speed_net = threading.Thread(target=get_speed_net)
thread_check_speed_net.start()

thread_Alarm_free_space = threading.Thread(target=Alarm_free_space)
thread_Alarm_free_space.start()
