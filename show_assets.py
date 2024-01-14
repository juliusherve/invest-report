#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 18 21:32:23 2023

@author: julius
"""
import requests                                                                #used for api requests
import csv                                                                     #used for saving history in a csv
import time                                                                    #used to set history timestamp
from datetime import datetime, timedelta,date
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker

import numpy as np
#save data
history_path = 'history_assets.csv' #history of investment value
invested_path = 'history_investment.csv'#history of investment made

plt.close("all")

def load_csv_data(csv_file):
    with open(csv_file, 'r', newline='') as file:
        reader = csv.reader(file)
        lines = list(reader)
    file.close()
    return lines


def sort_list_by_time(time,amount):
    #organize the table according to time schedule 
    sort_indice = sorted(range(len(time)), key=lambda k: time[k])
    time = [time[i] for i in sort_indice]
    amount = [amount[i] for i in sort_indice]
    return time, amount


"""  -------- investment --------  """
def extract_investment_list_sorted(type_inv,lines):
    deposit_time = []
    deposit_amount = []
    for line in lines[1:len(lines)]:
        if line[1] == type_inv :
            deposit_time.append(float(line[0]))
            deposit_amount.append(float(line[2]))
    deposit_time_s, deposit_amount_s = sort_list_by_time(deposit_time,
                                                         deposit_amount)
    return deposit_time_s, deposit_amount_s
    
def find_all_type_invest(lines):
    list_type = []
    for line in lines[1:len(lines)]:
        if line[1] not in list_type :
            list_type.append(line[1])
    return list_type
    
def save_list_all_invest():
    lines = load_csv_data(invested_path)
    invest_list = find_all_type_invest(lines)
    time_invest = []
    amount_invest = []
    for inv in invest_list:
        inv_time, inv_amount = extract_investment_list_sorted(inv,lines)
        time_invest.append(inv_time)
        amount_invest.append(inv_amount)
    return invest_list,time_invest, amount_invest

def marge_date_together_invest(timess,amount):
   
    global_invest_time = []
    global_invest_amount = []
    for timing in timess:
        for timed in timing:
            if timed not in global_invest_time:
                global_invest_time.append(timed)
    global_invest_time.append(time.time())
    global_invest_time = sorted(global_invest_time)
    for i in range(len(amount)):
        global_invest_amount.append([])
        for j in range(len(global_invest_time)):
            if global_invest_time[j] in timess[i]:
                k = timess[i].index(global_invest_time[j])
                if len(global_invest_amount[i]) == 0 :
                    global_invest_amount[i].append(amount[i][k])
                else : 
                    global_invest_amount[i].append(amount[i][k]+ global_invest_amount[i][j-1] )
            else:
                if len(global_invest_amount[i]) == 0 :
                    global_invest_amount[i].append(0)
                else : 
                    global_invest_amount[i].append(global_invest_amount[i][j-1])
    return global_invest_time,global_invest_amount
    




"""  -------- assets --------  """

def find_all_type_assets(lines):
    list_type = ["stocks","btc","not invested"]
    if len(lines[0]) > 6 :
        list_type += lines[0][6:len(lines)]
    return list_type

def save_list_all_assets():
    lines = load_csv_data(history_path)
    assets_list = find_all_type_assets(lines)
    time_assets = []
    amount_assets = []
    for i in assets_list : (amount_assets.append([])) 
    for line in lines[1:len(lines)] :
        list_line = line
        time_assets.append(float(list_line[0]))
        if list_line[1] == "" :
            amount_assets[1].append(0) #btc
        else :
            amount_assets[1].append(float(list_line[1])) #btc
        amount_assets[0].append(float(list_line[3])) #stocks
        amount_assets[2].append(float(list_line[4])) #not invested
        try :
            amount_assets[3].append(float(list_line[6])) #assurance vie
        except :
            amount_assets[3].append(0) #assurance vie
    return assets_list,time_assets, amount_assets


"""  ----------- data -----------  """
assets_list, assets_time, assets_amount = save_list_all_assets()
invest_list, invest_time, invest_amount = save_list_all_invest()

invest_date,invest_data = marge_date_together_invest(invest_time, invest_amount)
invest_date_list = [datetime.utcfromtimestamp(timee) for timee in invest_date]
assets_date_list = [datetime.utcfromtimestamp(timee) for timee in assets_time]

""" ----------- merge timing """

def create_list_time(list_of_list):
    list_of_time = []
    for liste in list_of_list:
        for time in liste:
            if time not in list_of_time:
                list_of_time.append(time)
    sort_indice = sorted(range(len(list_of_time)), key=lambda k: list_of_time[k])
    list_of_time = [list_of_time[i] for i in sort_indice]
    return list_of_time

def create_matching_value(liste_time, assets, invest):
    #assets and invest list as [time[],value[]]
    assets_combine = []
    invest_combine = []
    assets[0],assets[1] = sort_list_by_time(assets[0],assets[1])
    invest[0],invest[1] = sort_list_by_time(invest[0],invest[1])
    for time in liste_time:
        if time in assets[0]:
            assets_combine.append(assets[1][assets[0].index(time)])
        else : 
            i = 0
            while assets[0][i] < time and i < len(assets[0]) - 1 :
                i+= 1
            if i == len(assets[0]) :
                assets_combine.append(0)
            else :
                assets_combine.append(assets[1][i-1])
                i = 0
                
        if time in invest[0]:
            invest_combine.append(invest[1][invest[0].index(time)])
        else : 
            i = 0
            while invest[0][i] < time and i < len(invest[0]):
                i+= 1
            if i == len(invest[0]) :
                invest_combine.append(0)
            else :
                invest_combine.append(invest[1][i-1])
                i = 0
    
    return assets_combine, invest_combine
        
total_invest = []
total_assets = []

for  i in range(len(invest_data[1])) :
    total_invest.append(invest_data[0][i]+
                 invest_data[1][i] + 
                 invest_data[2][i]+ 
                 invest_data[3][i])

for  i in range(len(assets_amount[1])) :
    total_assets.append( assets_amount[0][i]+
                        assets_amount[1][i]+
                        assets_amount[2][i]+
                        assets_amount[3][i])
total_times = create_list_time([assets_time, invest_date])
total_times_list = [datetime.utcfromtimestamp(timee) for timee in total_times]
a,b = create_matching_value(total_times,[assets_time, total_assets],[invest_date, total_invest] )
gain = []
yield_invest = []
for i in range(len(a)):
    gain.append(a[i]-b[i])
    yield_invest.append(gain[i]/b[i])        
        


"""  -------- graph data --------  """
assets_color = ["#6184D8","#F5E464","#D1423D","#06D6A0"]    
invest_color = ["#891511","#1D3878","#BFAB25","#007D5C"]

fig = plt.figure()
#repartition / pie chart 
assets_pourcent = []
for i in range(len(assets_list)):
    assets_pourcent.append(assets_amount[i][-1]/total_invest[-1])
ax_repart = plt.subplot2grid((3, 4), (0, 3))
ax_repart.pie(assets_pourcent, 
              autopct='%1.1f%%',
              colors= assets_color,
              radius=1.5)




ax_global = plt.subplot2grid((3, 4), (0, 0),colspan=3, rowspan=2) 

#global view
ax_global.stackplot(assets_date_list,
             assets_amount[0],
             assets_amount[1],
             assets_amount[2],
             assets_amount[3],
             colors= assets_color,
             labels=assets_list,
             alpha=0.8)

ax_global.plot(invest_date_list,
             invest_data[0],
             "--", 
             linewidth=1.5,
             label="dividende",
             color = invest_color[0],
             alpha=0.8)

ax_global.plot(invest_date_list,
             invest_data[1],
             "--", 
             linewidth=1.5,
             label="buy stocks",
             color = invest_color[1],
             alpha=0.8)

ax_global.plot(invest_date_list,
             invest_data[2],
             "--", 
             linewidth=1.5,
             label="buy bitcoin",
             color = invest_color[2],
             alpha=0.8)

ax_global.plot(invest_date_list,
             invest_data[3],
             "--", 
             linewidth=1.5,
             label="assurance vie",
             color = invest_color[3],
             alpha=0.8)

ax_global.plot(invest_date_list,
             total_invest,
             "k--", 
             linewidth=2,
             label="total investment",
             alpha=1)

def euro(x, pos):
    return f'{x:1.0f}€'

years = mdates.YearLocator()   # every year
months = mdates.MonthLocator()  # every month
years_fmt = mdates.DateFormatter('%Y') 
ax_global.xaxis.set_major_locator(years)
ax_global.xaxis.set_major_formatter(years_fmt)
ax_global.xaxis.set_minor_locator(months)
ax_global.yaxis.set_major_formatter(euro)
#ax_global.xaxis.set_visible(False)
ax_global.grid(True, linestyle='--', alpha=0.5)
# Add labels and title
#ax_global.set_title('Investissement')

# Add legend
#ax_global.legend(loc='upper left')

# Add grid
ax_global.grid(True, linestyle='--', alpha=0.5)
yield_inv = []
for i in range(len(yield_invest)):
    yield_inv.append(yield_invest[i]*100)

ax_yield = plt.subplot2grid((3, 4), (2, 0),colspan=3) 

ax_yield.plot(total_times_list,
             yield_inv,
             "--", 
             linewidth=1.5,
             label="yield",
             color = "g",
             alpha=0.8)
years = mdates.YearLocator()   # every year
months = mdates.MonthLocator()  # every month
years_fmt = mdates.DateFormatter('%Y')
ax_yield.xaxis.set_major_locator(years)
ax_yield.xaxis.set_major_formatter(years_fmt)
ax_yield.xaxis.set_minor_locator(months)
ax_yield.grid(True, linestyle='--', alpha=0.5)
ax_yield.set_ylim(top=20)  # adjust the top leaving bottom unchanged
ax_yield.axhline(0, linewidth=1.5, color='k')
ax_yield.set_ylim(bottom=-10)  # adjust the bottom leaving top unchanged

def pourcent(x, pos):
    return f'{x:1.1f}%'
ax_yield.yaxis.set_major_formatter(pourcent)
plt.show()

#report 
ax_report = plt.subplot2grid((3, 4), (1, 3)) 

ax_report.text(0, 0.8, f'gain : {gain[-1]:1.2f}€')
ax_report.text(0, 0.65, f'yield : {yield_inv[-1]:1.2f}%')
ax_report.set_axis_off()

lines = [] 
labels = [] 

for ax in fig.axes: 
    Line, Label = ax.get_legend_handles_labels() 
    # print(Label) 
    lines.extend(Line) 
    labels.extend(Label) 

fig.legend(lines, labels, loc='lower right')
aujourdhui = date.today()
aujourdhui = aujourdhui.strftime("%d/%m/%Y")
titre = f"Investissements à la date du {aujourdhui}"
fig.suptitle(titre, fontsize=16)
plt.show()


"""

fig, ax = plt.subplots()

# Stackplot with custom colors and labels


ax.stackplot(assets_date_list,
             assets_amount[0],
             assets_amount[1],
             assets_amount[2],
             assets_amount[3],
             labels=assets_list, alpha=0.8)

ax.plot(invest_date_list,
             invest_data[0],
             "--", 
             linewidth=1.5,
             label="dividende",
             color = "green",
             alpha=0.8)



ax.plot(assets_date_list,
             yield_invest,
             "--", 
             linewidth=1.5,
             label="yield",
             color = "g",
             alpha=0.8)





ax.plot(invest_date_list,
             invest_data[3],
             "--", 
             linewidth=1.5,
             label="assurance vie",
             color = "red",
             alpha=0.8)



years = mdates.YearLocator()   # every year
months = mdates.MonthLocator()  # every month
years_fmt = mdates.DateFormatter('%Y')
ax.xaxis.set_major_locator(years)
ax.xaxis.set_major_formatter(years_fmt)
ax.xaxis.set_minor_locator(months)
# Add labels and title
ax.set_title('Investissement')

# Add legend
ax.legend(loc='upper left')

# Add grid
ax.grid(True, linestyle='--', alpha=0.5)
#ax.set_ylim(top=0.2)  # adjust the top leaving bottom unchanged
ax.axhline(0, linewidth=1.5, color='k')
ax.set_ylim(bottom=-0.1)  # adjust the bottom leaving top unchanged
# Customize colors
ax.set_facecolor('#f0f0f0')  # Background color
plt.xticks(rotation=45)
# Show the plot





invest_date,invest_data = marge_date_together_invest(invest_time, invest_amount)

fig, ax = plt.subplots()
invest_date_list = [datetime.utcfromtimestamp(timee) for timee in invest_date]
# Stackplot with custom colors and labels
ax.stackplot(invest_date_list,
             invest_data[0],
             invest_data[1],
             invest_data[2],
             labels=invest_list, alpha=0.8)
"""
