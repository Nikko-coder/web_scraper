# Author: Nikola Ticha

import requests
from bs4 import BeautifulSoup as BS
import csv
from tqdm import tqdm
import time

url = "https://volby.cz/pls/ps2017nss/ps3?xjazyk=CZ"
url_pairing = "https://volby.cz/pls/ps2017nss/"


# A) creating soup
def first_soup(url):
    r = requests.get(url)
    try:
        r.raise_for_status()
    except Exception as e:
        print("There was a problem: %s" % e)
    soup = BS(r.text, "lxml")
    return soup


# A) creating url for entering desired location
def get_city(url, url_pairing):
    soup = first_soup(url)
    print("Election results to the Chamber of Deputies - 'VOLBY.CZ'")
    city = input("Enter the desired district (e.g. Praha): ")
    while not check_entry(url, city):
        city = input("Enter the desired district (e.g. Praha): ")
    find_link = soup.find("td", text=city).find_next("td").find_next("td").find("a")
    my_url = url_pairing + find_link["href"]
    return my_url


# testing valid entry
def check_entry(url, city):
    soup = first_soup(url)
    tables = ["t1sa1 t1sb2", "t2sa1 t2sb2", "t3sa1 t3sb2", "t4sa1 t4sb2",
              "t5sa1 t5sb2", "t6sa1 t6sb2", "t7sa1 t7sb2", "t8sa1 t8sb2",
              "t9sa1 t9sb2", "t10sa1 t10sb2", "t11sa1 t11sb2", "t12sa1 t12sb2",
              "t13sa1 t13sb2", "t14sa1 t14sb2"]
    cities = [a.text for a in soup.find_all("td", attrs={"headers": tables})]
    if city in cities:
        return True


# A) creating soup
def get_real_soup(my_url):
    r = requests.get(my_url)
    try:
        r.raise_for_status()
    except Exception as e:
        print("There was a problem: %s" % e)
    soup = BS(r.text, "lxml")
    return soup


# A) making soup for usage
def my_soup():
    soup = get_city(url, url_pairing)
    return get_real_soup(soup)


# B) MPDS main page data scraping - returns codes of all cities in given location
def location_codes(my_url):
    codes = [a.text for a in my_url.find_all("td", attrs={"class": "cislo"})]
    return codes


# B) MPDS - returns names of all cities in given location
def location_names(my_url):
    names = [a.text for a in my_url.find_all("td", attrs={"headers": ("t1sa1 t1sb2", "t2sa1 t2sb2", "t3sa1 t3sb2")}) if a.text != "-"]
    return names


# B) MPDS - returns links of every listed city
def location_links(my_url):
    links = []
    for td in my_url.find_all("td", attrs={"class": "cislo"}):
        x = td.find("a")
        links.append(x["href"])
    return links


# B) MPDS - returns the above functions for writing into rows
def completion_location(my_url):
    return list(zip(location_codes(my_url), location_names(my_url), location_links(my_url)))


# C) NPDS - returns integers of votes for given city (Volici v seznamu, vydane obalky, platne hlasy)
def get_total_votes(next_url):
    total_votes = [int(a.text.replace("\xa0", "")) for a in next_url.find_all("td", attrs={"headers": ("sa2", "sa3", "sa6")}) if a.text != "-"]
    return total_votes


# C) NPDS - returns names of parties
def parties_names(next_url):
    parties = [a.text for a in next_url.find_all("td", attrs={"headers": ("t1sa1 t1sb2", "t2sa1 t2sb2")}) if a.text != "-"]
    return parties


# C) NPDS - returns number of votes for each party for given city
def get_parties_votes(next_url):
    parties_votes = [int(a.text.replace("\xa0", "")) for a in next_url.find_all("td", attrs={"headers": ("t1sa2 t1sb3", "t2sa2 t2sb3")}) if a.text != "-"]
    return parties_votes


# C) NPDS - returns the whole row for csv table
def completion_values(next_url):
    return get_total_votes(next_url) + get_parties_votes(next_url)


# D) CSV - making header
def headline_csv(next_url):
    h1 = ["Code", "City", "Listed voters", "Issued envelopes", "Valid votes"]
    parties = parties_names(next_url)
    return h1 + parties


# D) CSV - writing data into csv file including progress bar
def create_csv(locations):
    filename = input("Enter the name of the to be created csv file: ").strip()
    first_url = url_pairing + locations[0][2]
    soup = get_real_soup(first_url)
    headline = headline_csv(soup)
    with open(f"{filename}.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headline)
        with tqdm(total=len(locations), desc="Adding vote results") as pbar:
            for i in range(len(locations)):
                time.sleep(1)
                pbar.update(1)
            for location in locations:
                url_cities = url_pairing + location[2]
                row_soup = get_real_soup(url_cities)
                row_results = completion_values(row_soup)
                writer.writerow([location[0], location[1]] + row_results)


if __name__ == "__main__":
    create_csv(locations=completion_location(my_soup()))
