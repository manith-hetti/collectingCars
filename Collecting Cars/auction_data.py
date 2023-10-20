import requests
from bs4 import BeautifulSoup
import car_objects
import numpy as np

headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"}

def create_url(year, make, des, model, submodel, sold):
    if sold == 0:
        sold = ''
    sold = str(sold)
    url = f"https://collectingcars.com/for-sale/{year}-{make}-{des}-{model}-{submodel}-{sold}"
    url = url.replace('--', '-')
    url = url.replace(' ', '-')
    if url.endswith('-'):
        url = url.rstrip(url[-1])
    return url


def make_soup(url):
    response = requests.get(url, headers=headers)
    data = response.text
    soup = BeautifulSoup(data, 'html.parser')
    return soup

def check_real(soup):
    car_data = soup.find_all('h2', class_ = 'mt-4')
    if not car_data:
        return True
    else:
        return False
    
def check_gb(soup):
    country = soup.find(id="carsAuctionStatus")['data-auction-country-code']
    if country != 'GB':
        return False
    else:
        return True
    
def handle_values(soup):
    ul = soup.find("ul", class_="overviewList list-unstyled")
    car_data = ul.find_all("li")
    values = []
    for value in car_data:
        text = value.text.strip()
        values.append(text)
    if values[0] == 'N/A':
        values[0] = '0 miles'
    arr = values[0].split()
    arr[1] = arr[1].lower()
    if arr[1] == "km":
        mileage = int(arr[0].replace(",", ""))*0.621371
    elif arr[1] == "miles":
        mileage = int(arr[0].replace(",", ""))
    if len(values) != 7:
        if values[1] != 'automatic' and values[1] != 'semi-automatic' and values[1] != 'manual':
            values.insert(1, "none")
        elif values[2] != 'RHD' and values[2] != 'LHD':
            values.insert(2, "none")
    if values[1] != 'manual' and values[1] != "none":
        values[1] = 'automatic'
    price = soup.find(id="carsAuctionStatus")['data-auction-current-bid']
    if price == '':
        price = 0
    else:
        price = int(soup.find(id="carsAuctionStatus")['data-auction-current-bid'])
    transmission = values[1]
    colour = str(values[3])
    engine = values[5]
    vin = values[6][3:]
    return [mileage, transmission, engine, colour, vin, price]


def check_auction(soup):
    format = soup.find(id="carsAuctionStatus")['data-auction-saleformat']
    if format != "auction":
        return False
    else:
        return True


def stage(soup):
    result = soup.find(id="carsAuctionStatus")['data-auction-stage']
    if result == 'unsold':
        return "unsold"
    elif result == 'live':
        return "live"
    elif result == 'comingsoon':
        return 'coming soon'
    else:
        return True
    
def auction_data_sold(soup):
    values = handle_values(soup)
    auction_dict_sold = {
        "price" : int(soup.find(id="carsAuctionStatus")['data-auction-pricesold']),
        "mileage": values[0],
        "year" : int(soup.find(id="carsAuctionStatus")['data-auction-title'].split()[0]),
        "transmission" : values[1],
        "engine" : values[2],
        "date" : str(soup.find(id="carsAuctionStatus")['data-auction-date-sold'].split()[0]),
        "colour" : values[3],
        "views": soup.find(id="carsAuctionStatus")['data-auction-noviews'],
        "bids" : int(soup.find(id="carsAuctionStatus")['data-auction-bids']),
        "reserve_lowered" : int(soup.find(id="carsAuctionStatus")['data-auction-reservelowered']),
        "high_bidder" : soup.find(id="carsAuctionStatus")['data-auction-highbidderid'],
        "seller" : soup.find(id="carsAuctionStatus")['data-auction-vendorid'],
        "auction_tag" : int(soup.find(id="carsAuctionStatus")['data-auction-id']),
        "vin" : values[4]
    }   
    return auction_dict_sold

def auction_data_unsold(soup):
    values = handle_values(soup)
    auction_dict_unsold = {
        "high_bid" : values[5],
        "mileage": values[0],
        "year" : int(soup.find(id="carsAuctionStatus")['data-auction-title'].split()[0]),
        "transmission" : values[1],
        "engine" : values[2],
        "date" : str(soup.find(id="carsAuctionStatus")['data-auction-auction-end'].split()[0]),
        "colour" : values[3],
        "views": soup.find(id="carsAuctionStatus")['data-auction-noviews'],
        "bids" : int(soup.find(id="carsAuctionStatus")['data-auction-bids']),
        "reserve_lowered" : int(soup.find(id="carsAuctionStatus")['data-auction-reservelowered']),
        "high_bidder" : soup.find(id="carsAuctionStatus")['data-auction-highbidderid'],
        "seller" : soup.find(id="carsAuctionStatus")['data-auction-vendorid'],
        "auction_tag" : int(soup.find(id="carsAuctionStatus")['data-auction-id']),
        "vin": values[4]
    }   
    return auction_dict_unsold

