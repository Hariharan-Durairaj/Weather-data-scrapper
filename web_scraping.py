from bs4 import BeautifulSoup as BS
from selenium import webdriver
import pandas as pd
import time
import html
import re
from unicodedata import normalize
import warnings
warnings.filterwarnings("ignore")

df=pd.DataFrame()
from selenium.webdriver.chrome.options import Options
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')

def collect_weather_data(url="https://weather.com/en-IN/weather/today/l/ba484457443c15089496e4a694f025f897b92bdbad047a2a796d641205d69e10"):
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    time.sleep(5)
    r = driver.page_source
    driver.quit()
    soup = BS(r, "html.parser",)

    weather={}
    collect=[]
    try:
        section=soup.find("div", class_=re.search(r"\"Card--content--.{3,7}\"",str(soup))[0][1:-1])
        wea=[]
        for i in section.find_all('span'):
            trial = i.get_text()
            wea.append(normalize('NFKD', trial))
        
        for i in wea:  
            try:
                f=re.search(r"([0-9]+\:[0-9]+)",i)
                collect.append(f[1])
            except Exception:
                pass
        if len(collect)==1:
            weather["weather time"]=collect[0]
        collect=[]
        for i in wea:  
            try:
                f=re.search(r"(([0-9.]+)[ ]*\°)|((-)-)",i)
                collect.append(f[2])
            except Exception:
                pass
        if len(collect)==3:
            weather["temp"]=collect[0]
            weather["high"]=collect[1]
            weather["low"]=collect[2]
        else:
            print("error data incomplete")
            print(wea)
    except:
        print("in exception")
        section2=soup.find("div", class_="removeIfEmpty",id="todayDetails")
        wea=[]
        for i in section2.find_all('span'):
            trial = i.get_text()
            wea.append(normalize('NFKD', trial))
        weather={}
        collect=[]
        for i in wea:  
            try:
                f=re.search(r"(([0-9.]+)[ ]*\°)|((-)-)",i)
                if f[2]!=None:
                    collect.append(f[2])
                else:
                    collect.append(f[4])
            except Exception:
                pass
        if len(collect)==5:
            weather["weather time"]="unavailable"
            weather["temp"]=collect[0]
            weather["low"]=collect[2]
            weather["high"]=collect[3]
        else:
            print("error data incomplete in exception")
            print(wea)

    section2=soup.find("div", class_="removeIfEmpty",id="todayDetails")
    wea=[]
    for i in section2.find_all('span'):
        trial = i.get_text()
        wea.append(normalize('NFKD', trial))
    collect=[]
    for i in wea:  
        try:
            f=re.search(r"(([0-9.]+)[ ]*\°)|((-)-)",i)
            if f[2]!=None:
                collect.append(f[2])
            else:
                collect.append(f[4])
        except Exception:
            pass
    if len(collect)==5:
        weather["dew"]=collect[4]
    else:
        print("error data incomplete")
        print(wea)
    collect=[]
    for i in wea:
        try:
            f=re.search(r"([0-9.]+)[ ]*km\/h",i)
            collect.append(f[1])
        except Exception:
            pass
    if len(collect)==1:
        weather["wind"]=collect[0]
    collect=[]
    for i in wea:
        try:
            f=re.search(r"([0-9.]+)[ ]*\%",i)
            collect.append(f[1])
        except Exception:
            pass
    if len(collect)==1:
        weather["humidity"]=collect[0]
    collect=[]
    for i in wea:
        try:
            f=re.search(r"([0-9.]+)[ ]*mb",i)
            collect.append(f[1])
        except Exception:
            pass
    if len(collect)==1:
        weather["pressure"]=collect[0]
    collect=[]
    for i in wea:
        try:
            f=re.search(r"(([0-9.]+)[ ]*of[ ]*([0-9.]+))|(Extreme)",i)
            if f[2]!=None:
                collect.append(f[2])
                collect.append(f[3])
            elif f[4]!=None:
                collect.append(f[4])
            
        except Exception:
            pass
    if len(collect)==2:
        weather["index"]=collect[0]
        weather["index(out of)"]=collect[1]
    elif len(collect)==1:
        weather["index"]=collect[0]
        weather["index(out of)"]=""
    else:
        weather["index"]=None
        weather["index(out of)"]=""
    collect=[]
    for i in wea:
        try:
            f=re.search(r"([0-9.]+)[ ]*km$",i)
            collect.append(f[1])
            
        except Exception:
            pass
    if len(collect)==1:
        weather["visibility"]=collect[0]

    section=soup.find("div", class_="Card--content--1GQMr")
    for i in section.find_all('title'):
        trial = i.get_text()
        weather["cloud"]=trial

    winddir=soup.find("svg", attrs={'name': 'wind-direction','set': 'current-conditions'})
    deg=f=re.search(r"([0-9.]+)[ ]*deg",winddir['style'])[1]
    def deg_to_dir(deg):
        deg=int(deg)
        if deg>= 0 and deg<= 22.5 :
            return "south"
        elif deg>=22.5 and deg<=67.5 :
            return "south west"
        elif deg>=67.5 and deg<=112.5 :
            return "west"
        elif deg>=112.5 and deg<=157.5 :
            return "north west"
        elif deg>=157.5 and deg<=202.5 :
            return "north"
        elif deg>=202.5 and deg<=247.5 :
            return "north east"   
        elif deg>=247.5 and deg<=292.5 :
            return "east"           
        elif deg>=292.5 and deg<=337.5 :
            return "south east"
        elif deg>=337.5 and deg<=360:
            return "south"
    weather["wind dir"]=deg_to_dir(deg)
    return weather

weather=collect_weather_data()
print(weather)