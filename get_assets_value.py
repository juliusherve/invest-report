#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 16 22:56:10 2023

@author: julius
"""


#used librairy
import requests                                                                #used for api requests
import csv                                                                     #used for saving history in a csv
import time                                                                    #used to set history timestamp
from datetime import datetime, timedelta

#bitcoin api
url_blockchain = "https://blockchain.info"
bitcoin_address = "" #your bitcoin address here

#stocks api
url_t212 = "https://live.trading212.com/api/v0/" 
t212_api_key = "" #your api key here


#save data
history_path = 'history_assets.csv' #history of investment value
invested_path = 'history_investment.csv'#history of investment made




def convert_to_date(timestmp):
    struct_time = time.localtime(timestmp)
    date = struct_time.tm_year, struct_time.tm_mon, struct_time.tm_mday
    str_date = "{}-{}-{}".format(date[2],date[1],date[0])
    return str_date



#bitcoin querry
def get_bitcoin_amount():
    api = "/balance?active="
    response = requests.get(url_blockchain + api + bitcoin_address)
    data = response.json()
    nbr_bitcoin = float(data[bitcoin_address]['final_balance']) * 1e-08
    return nbr_bitcoin

def get_bitcoin_value():
    global data
    api = "/ticker"
    response = requests.get(url_blockchain + api)
    data = response.json()
    prix = float(data["EUR"]["last"])
    return prix
    

def get_bitcoin_assets():
    nbr_btc = get_bitcoin_amount()
    one_btc_value = get_bitcoin_value()
    wallet_value = nbr_btc * one_btc_value
    btc_value = {"value_btc" : wallet_value,
                 "amount_btc" : nbr_btc
                 }
    
    return btc_value
    

def get_bitcoin_price_at_date(date):
    #date as : "dd-mm-yyyy"
    url = f"https://api.coingecko.com/api/v3/coins/bitcoin/history?date={date}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        price = data['market_data']['current_price']['usd']
        return price

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None


#check for new investement
def is_new_bitcoin_buy(bitcoin):
    with open(history_path, 'r', newline='') as file:
        reader = csv.reader(file)
        lines = list(reader)
    file.close()
    if lines:
        last_line = lines[-1]
        history_btc = float(last_line[2])
        if history_btc != bitcoin:
            date = convert_to_date(float(last_line[0]))
            price = get_bitcoin_price_at_date(date)
            timestamp = last_line[0]
            transfert_value = price * (bitcoin - history_btc)
            save_investment(timestamp,"bitcoin",transfert_value)


#stocks querry
def get_t212_value():
    api = "equity/account/cash"
    url = url_t212 + api
    headers = {"Authorization": t212_api_key}
    response = requests.get(url, headers=headers)
    data = response.json()
    total = float(data["total"])
    free = float(data["free"])
    stock_value = total - free
    
    t212_value = {"value_stocks" : stock_value,
                  "not_invested" : free,
                  "total" : total
                  }
    
    return t212_value



def get_t212_dividends():
    liste_timestamp = []
    liste_montant = []
    api = "history/dividends"
    url = url_t212 + api
    headers = {"Authorization": t212_api_key}
    response = requests.get(url, headers=headers)
    data = response.json()
    for div in data["items"]:
        # Parse the string into a datetime object
        dt = datetime.strptime(div["paidOn"], "%Y-%m-%dT%H:%M:%S.%f%z")
        timestamp = time.mktime(dt.timetuple())
        liste_timestamp.append(timestamp)
        liste_montant.append(float(div["amountInEuro"]))
    return liste_timestamp , liste_montant


def get_t212_bank():
   liste_timestamp = []
   liste_montant = []
   api = "history/transactions" 
   url = url_t212 + api
   query = {
      "limit": "18"
    }
   headers = {"Authorization": t212_api_key}
   response = requests.get(url, headers=headers, params=query)
   data = response.json()
   for transactions in data["items"]:
       # Parse the string into a datetime object
       dt = datetime.strptime(transactions["dateTime"],
                              "%Y-%m-%dT%H:%M:%S.%f%z")
       timestamp = time.mktime(dt.timetuple())
       liste_timestamp.append(timestamp)
       liste_montant.append(float(transactions["amount"]))
   return liste_timestamp , liste_montant


#save value in histry folder
def save_data(line_to_add):
    with open(history_path, 'a', newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(line_to_add)
    file.close()
    
def is_invest_already_save(timestamp,type_inv, amount):
    with open(invested_path, 'r', newline='') as file:
        reader = csv.reader(file)
        lines = list(reader)
    file.close()
    for line in lines[1:len(lines)]:
        if timestamp == float(line[0]) and float(amount) == float(line[2]):
            return True
    return False 



def save_investment(timestamp,type_inv, transfert_value):
    line_to_add = [timestamp,
                   type_inv,
                   transfert_value,
                   ]
    already_present = is_invest_already_save(timestamp,
                                             type_inv,
                                             transfert_value)
    if not already_present:
        with open(invested_path, 'a', newline='') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow(line_to_add)
        file.close()

def get_last_insurance_value():
    with open(history_path, 'r', newline='') as file:
        reader = csv.reader(file)
        lines = list(reader)
    file.close()
    
    return float(lines[-1][6])

def assurance_vie():
    if convert_to_date(time.time())[0:1] == "5" :
        save_investment(time.time(),"assurance vie", 155)
        value_life_insurance = get_last_insurance_value() + 155
    else : 
        value_life_insurance = get_last_insurance_value()
    return value_life_insurance


        
        
    


liste_timestamp212 , liste_montant212 = get_t212_dividends()
for i in range(len(liste_timestamp212)):
    save_investment(liste_timestamp212[i],"div",liste_montant212[i])

liste_timestamp212 , liste_montant212 = get_t212_bank()
for i in range(len(liste_timestamp212)):
    save_investment(liste_timestamp212[i],"bank",liste_montant212[i])
    
t212 = get_t212_value()
btc = get_bitcoin_assets()
assu_vie = assurance_vie()
timestamp = time.time()
line_to_add = [timestamp,
               btc["value_btc"],
               btc["amount_btc"],
               t212["value_stocks"],
               t212["not_invested"],
               t212["total"],
               assu_vie
               ]

save_data(line_to_add)
is_new_bitcoin_buy(btc["amount_btc"])

