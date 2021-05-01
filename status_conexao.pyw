# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk
import random
import datetime
import os
import subprocess
from pathlib import Path
import requests
import json
from pandas import DataFrame
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class MyWindow:
    def __init__(self, win):
        self.win = win
        self.label_ip=tk.Label(self.win)   
        self.label_ip.place(x=30, y=20)     
        self.label_operadora=tk.Label(self.win)   
        self.label_operadora.place(x=30, y=50)     
        self.label_cidade=tk.Label(self.win)   
        self.label_cidade.place(x=30, y=80)     
        self.label_internet=tk.Label(self.win)   
        self.label_internet.place(x=30, y=110)     
        self.label_vpn=tk.Label(self.win)        
        self.label_vpn.place(x=30, y=140)
        #self.button_testar=Button(win, text='Iniciar Teste', command=self.retorno_teste)
        #self.button_testar.place(x=120, y=120)
        self.label_testando=tk.Label(self.win)        
        self.label_testando.place(x=30, y=170)
        self.grafico=tk.Frame(self.win)
        self.grafico.place(x=0, y=200)
        self.figure = plt.Figure(figsize=(6,5), dpi=50)
        self.ax1 = self.figure.add_subplot(111)
        self.ax2 = self.ax1.twiny()
        self.ax1.set_ylabel("VPN")
        self.ax2.set_ylabel("Internet")
        self.line = FigureCanvasTkAgg(self.figure, self.grafico)
        self.line.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH)
        self.dict_vpn = {'Hora': [], 'VPN': []}
        self.dict_internet = {'Hora': [], 'Internet': []}
        self.retorno_ipapi = self.ipapi()
        self.retorno_teste()

    def retorno_teste(self):
        self.label_testando['text'] = "Testado em: {}".format(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        ms_internet = self.check_ping("208.67.222.222")
        self.label_internet['text'] = 'INTERNET: {} ms'.format(ms_internet)
        ms_vpn = self.check_ping("8.8.8.8")
        self.label_vpn['text'] = 'VPN XP: {} ms'.format(ms_vpn)
        if self.retorno_ipapi.get("error"):
            self.label_ip['text'] = "Seu IP: -"
            self.label_operadora['text'] = "Operadora: -"
            self.label_cidade['text'] = "Cidade: -"
        else:
            self.label_ip['text'] = "Seu IP: {}".format(self.retorno_ipapi.get("ip"))
            self.label_operadora['text'] = "Operadora: {}".format(self.retorno_ipapi.get("org"))
            self.label_cidade['text'] = "Cidade: {}/{}".format(self.retorno_ipapi.get("city"), self.retorno_ipapi.get("region_code")) 

        limite_registros = 1440
        if len(self.dict_vpn['Hora']) > limite_registros:
            self.dict_vpn["Hora"] = self.dict_vpn["Hora"][1:]
            self.dict_vpn["VPN"] = self.dict_vpn["VPN"][1:]
            self.dict_internet["Hora"] = self.dict_internet["Hora"][1:]
            self.dict_internet["Internet"] = self.dict_internet["Internet"][1:]

        self.dict_vpn["Hora"].append(datetime.datetime.now().strftime("%H:%M")) 
        self.dict_vpn["VPN"].append(ms_vpn) 
        self.dict_internet["Hora"].append(datetime.datetime.now().strftime("%H:%M")) 
        self.dict_internet["Internet"].append(ms_internet) 

        df_vpn = DataFrame(self.dict_vpn,columns=['Hora','VPN'])            
        df_internet = DataFrame(self.dict_internet,columns=['Hora','Internet'])            

        self.ax1.clear()
        self.ax2.clear()

        #print(self.line)
        #print(dir(self.line))
        df_vpn = df_vpn[['Hora','VPN']].groupby('Hora').mean()
        df_vpn.plot(kind='line', legend=True, ax=self.ax1, color='r', fontsize=15)
        df_internet = df_internet[['Hora','Internet']].groupby('Hora').mean()
        df_internet.plot(kind='line', legend=True, ax=self.ax2, color='b', fontsize=15)

        #self.line.draw()
        self.figure.canvas.draw()

        #self.ax1.set_ylabel('VPN')
        #self.ax2.set_ylabel('Internet')

        #self.ax2.set_title('Média ms por hora')        

        self.win.after(5000, self.retorno_teste)

    def check_ping(self, hostname):
        try:
            response = subprocess.check_output("ping -t 5 " + hostname, shell=True, stdin=subprocess.DEVNULL) 
        except subprocess.CalledProcessError as e:
            response = None
        print(str(response).split("\\n")[-2])
        if response:
            #pingstatus = int(str(response).split("\\r\\n")[-2].split(" = ")[-1].replace("ms", ""))
            #round-trip min/avg/max/stddev = 25.939/33.971/48.759/8.369 ms
            pingstatus = int(str(response).split("\\n")[-2].split(" = ")[1].split("/")[1].split(".")[0])
        else:
            pingstatus = 0
        print(pingstatus)
        return pingstatus

    def ipapi(self):
        #return {"ip": "34.95.146.85", "city": "São Paulo"}
        retorno_ipapi = {}
        try:
            ret = requests.get("https://ipapi.co/json/", verify=False, timeout=5)
            ret.encoding = 'utf-8'
            retorno_ipapi = json.loads(ret.text)
        except requests.exceptions.ConnectionError:
            retorno_ipapi = {"error": True}
        except requests.exceptions.ReadTimeout:
            retorno_ipapi = {"error": True}            
        return retorno_ipapi


window=tk.Tk()
mywin=MyWindow(window)
window.title('Status Conexão')
window.geometry("300x480+10+10")
window.mainloop()
