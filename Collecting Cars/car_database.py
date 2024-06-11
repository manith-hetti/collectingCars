import psycopg
import numpy as np
import time
import pandas as pd
import matplotlib.pyplot as plt

import auction_data as ad


def find_car(make, model, des, submodel):
    cur = conn.cursor()

    if submodel == '' and des == '':
        cur.execute("SELECT * FROM car_list WHERE make=%s AND model=%s", [make, model])
        row = cur.fetchone()
    elif des == '':
        cur.execute("SELECT * FROM car_list WHERE make=%s AND model=%s AND submodel=%s", (make, model, submodel))
        row = cur.fetchone()
    elif submodel == '':
        cur.execute("SELECT * FROM car_list WHERE make=%s AND model=%s AND designation=%s", (make, model, des))
        row = cur.fetchone()
    else:
        cur.execute("SELECT * FROM car_list WHERE make=%s AND model=%s AND designation=%s AND submodel=%s", (make, model, des, submodel))
        row = cur.fetchone()
    cur.close()
    conn.close()
    return row[0]

def find_auction(auction_tag):
    conn = psycopg.connect("dbname=cars user=postgres password=Sanuth0128")
    cur = conn.cursor()
    cur.execute("SELECT * FROM auction_data WHERE auction_tag=%s", [auction_tag])
    row = cur.fetchone()
    return row[0]

def insert_car(car_id, price, mileage, year, transmission, engine, date, colour, sold, auction_tag, vin, web_ref):
    conn = psycopg.connect("dbname=cars user=postgres password=Sanuth0128")
    cur = conn.cursor()
    cur.execute("INSERT INTO auction_data(car_id, price, mileage, year, transmission, engine, date, colour, sold, auction_tag, vin, web_ref) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (car_id, price, mileage, year, transmission, engine, date, colour, sold, auction_tag, vin, web_ref))
    conn.commit()
    cur.close()
    conn.close()
    return 1

def insert_meta(auction_id, views, bids, reserve_lowered, seller, high_bidder):
    conn = psycopg.connect("dbname=cars user=postgres password=Sanuth0128")
    cur = conn.cursor()
    cur.execute("INSERT INTO auction_meta(auction_id, views, bids, reserve_lowered, seller, high_bidder) VALUES(%s, %s, %s, %s, %s, %s)", (auction_id, views, bids, reserve_lowered, seller, high_bidder))
    conn.commit()
    cur.close()
    conn.close()

def find_missing(car_id, year):
    conn = psycopg.connect("dbname=cars user=postgres password=Sanuth0128")
    cur = conn.cursor()

    cur.execute("SELECT MAX(web_ref) FROM auction_data WHERE car_id=%s AND year=%s", [car_id, year])
    results = cur.fetchone()

    cur.close()
    conn.close()
    if results[0] == None:
        return 0
    else:
        return results[0]
    
def find_years(car_id):
    conn = psycopg.connect("dbname=cars user=postgres password=Sanuth0128")
    cur = conn.cursor()
    cur.execute("SELECT * FROM car_list WHERE car_id=%s", [car_id])
    row = cur.fetchone()
    cur.close()
    conn.close()
    return [row[5], row[6]]
    
def insert_to_database(make, model, des, submodel):
    car_id = find_car(make, model, des, submodel)
    start_year = find_years(car_id)[0]
    end_year = find_years(car_id)[1]
    for year in np.arange(start_year, end_year+1):
        real = True
        sold = find_missing(car_id, int(year)) 
        while real == True:
            auction = ad.create_url(year, make, des, model, submodel, sold)
            soup = ad.make_soup(auction)
            if ad.check_real(soup) == False:
                real = False
                print(auction, "not real")
                year+=1
            elif ad.check_auction(soup) == False:
                print(auction, "not auction")
                sold+=1
            elif ad.stage(soup) == "coming soon":
                real= False
                print(auction, "coming soon")
                year+=1
            elif ad.stage(soup) == "live":
                real= False
                print(auction, "not live")
                year+=1
            elif ad.check_gb(soup) == False:
                print(auction, "not british")
                sold+=1
            elif ad.stage(soup) == "unsold":
                print(auction, "not sold")
                auction_data = ad.auction_data_unsold(soup)
                insert_car(
                    car_id, 
                    auction_data["high_bid"], 
                    auction_data["mileage"],
                    auction_data["year"],
                    auction_data["transmission"],
                    auction_data["engine"],
                    auction_data["date"],
                    auction_data["colour"],
                    'unsold',
                    auction_data["auction_tag"],
                    auction_data["vin"],
                    sold
                    )
                auction_id = find_auction(auction_data["auction_tag"])
                insert_meta(
                    auction_id, 
                    auction_data["views"],
                    auction_data["bids"],
                    auction_data["reserve_lowered"],
                    auction_data["seller"],
                    auction_data["high_bidder"]
                )
                sold+=1
            else:
                auction_data = ad.auction_data_sold(soup)
                insert_car(
                    car_id, 
                    auction_data["price"], 
                    auction_data["mileage"],
                    auction_data["year"],
                    auction_data["transmission"],
                    auction_data["engine"],
                    auction_data["date"],
                    auction_data["colour"],
                    'sold',
                    auction_data["auction_tag"],
                    auction_data["vin"],
                    sold
                    )
                auction_id = find_auction(auction_data["auction_tag"])
                insert_meta(
                    auction_id,
                    auction_data["views"],
                    auction_data["bids"],
                    auction_data["reserve_lowered"],
                    auction_data["seller"],
                    auction_data["high_bidder"]
                )

                sold+=1 
            time.sleep(3)

def size(car_id):
    conn = psycopg.connect("dbname=cars user=postgres password=Sanuth0128")
    cur = conn.cursor()   
    cur.execute("SELECT count(*) FROM auction_data WHERE car_id=%s", [car_id])
    data = cur.fetchone()
    cur.close()
    conn.close()
    for r in data:
        return r



def return_data(car_id):
    conn = psycopg.connect("dbname=cars user=postgres password=Sanuth0128")
    cur = conn.cursor()   
    cur.execute("SELECT * FROM auction_data WHERE car_id=%s", [car_id])
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

