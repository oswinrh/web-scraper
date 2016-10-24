from selenium import webdriver
import os
import time
import csv
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
import datetime

pathcd = "" #directory of your chrome driver
pathsave = "" #directory of your saved output file

allcity = ['Bali']
citytoscrap = []

#At the begining the program will ask how many city you want to scrap
choice = raw_input("Ingin Proses 34 Kota Sekaligus ?(Y/N) : ")
if choice == 'Y' or choice=='y':
    citytoscrap = allcity
else:
    print
    choice2 = raw_input("Masukan Sesuai urutan pada list ?(Y/N) : ")
    if choice2 == 'Y' or choice2=='y':
        print "Harap tulis nama kota sesuai dengan yang tersedia pada list"
        dari = raw_input("Dari : ")
        sampai = raw_input("Sampai : ")
        citytoscrap = allcity[allcity.index(dari):allcity.index(sampai)+1]
    else:
        print
        n = int(raw_input("Masukan Jumlah Kota : "))
        i=0
        while len(citytoscrap)<n:
            k = raw_input("Masukan kota/provinsi ke-"+str(i+1)+" :")
            citytoscrap.append(k)
            i+=1

#asking when is the date
print
print ("Format tanggal: DD/MM/YYYY, Contoh :  17/08/1945 ")
dat = raw_input("Masukkan Tanggal Check-In: ")

#And asking what is the output name
print
outname = raw_input("Masukan nama output file (.csv) : ")

BEXname = []
BEXlocation = []
BEXprice = []
BEXstar = []
BEXpromo = []
BEXrating = []
BEXkota = []


#The program will ask which currency do you prefer
print "Pilih Referensi Mata Uang Anda : "
print "[1] IDR"
print "[2] USD"
print "[3] AUD"
currencies = int(raw_input("Input Number : "))

st = datetime.datetime.now().time()
print st.strftime("%H:%M:%S")

# Because we only want to scrape one day only, so the check-out date is the next date of the check-in date
# Using the 1 night only stay option doesn't always working, so this procedure is used for get the next date 
# based on the check-In date as the Input
# Input(curdat) : Check-In date
# Output(return value) : Check-Out date (next date of check-in date)
def nextDate(curdat):
    dat = curdat.split("/")
    year = int(dat[2])
    month = int(dat[1])
    day = int(dat[0])
    try:
        datetime.datetime(year,month,day+1)
        if day+1<10:
            return "0"+str(day+1)+"/"+dat[1]+"/"+str(year)
        else:
            return str(day+1)+"/"+dat[1]+"/"+str(year)
    except Exception,e:
        if e.message == "day is out of range for month":
            try:
                datetime.datetime(year,month+1,1)
                if month+1<10:
                    return "01/0"+str(month+1)+"/"+dat[2]
                else:
                    return "01/"+str(month+1)+"/"+dat[2]
            except Exception,e:
                if e.message == "month must be in 1..12":
                    return "01/01/"+str(year+1)

# The US date format is month/day/year
def USdateFormat(x):
    dat = x.split("/")
    return dat[1]+"/"+dat[0]+"/"+dat[2]
    
# Function to get hotel name, since every hotel should has a name, so if element not found, this program will break and end immidiately
def EXname():
    nama = []
    i = 1
    while True:
        try:
            #print ""+str(i)
            nh = driver.find_element_by_xpath("""//*[@id="resultsContainer"]/section/article["""+str(i)+"""]/div/div/div/div[1]/ul[@class="hotel-info"]/li[@class="hotelTitle show-when-muted"]/h4""").text.encode('utf8')
            nama.append(nh)
            
        except NoSuchElementException:
            #print "masuk exception"
            #print ""+str(i)
            if i==3:
                i+=1
            #print ""+str(i)
            try:
                nh = driver.find_element_by_xpath("""//*[@id="resultsContainer"]/section/article["""+str(i)+"""]/div/div[1]/div[2]/div[1]/ul[@class="hotel-info"]/li[@class="hotelTitle show-when-muted"]/h4""").text.encode('utf8')
                nama.append(nh)           
            except NoSuchElementException:
                break
        i+=1
    #print "selesai satu page"
    return nama

# Function to get hotel location, since every hotel should has a location, so if element not found, this program will break and end immidiately
def EXlocation():
    location = []
    i = 1
    while True:
        try:
            loc = driver.find_element_by_xpath("""//*[@id="resultsContainer"]/section/article["""+str(i)+"""]/div/div/div/div[1]/ul/li[@class="neighborhood show-when-muted secondary"]""").text.encode('utf8')
            #print ""+loc
            location.append(loc)
        except NoSuchElementException:
            if i==3:
                i+=1
            #print ""+str(i)
            try:
                loc = driver.find_element_by_xpath("""//*[@id="resultsContainer"]/section/article["""+str(i)+"""]/div/div/div/div[1]/ul/li[@class="neighborhood show-when-muted secondary"]""").text.encode('utf8')
                location.append(loc)           
            except NoSuchElementException:
                break
        i+=1
    return location

def EXpriceALT(jum):
    price = []
    k = 1
    while len(price)<jum:
        try:
            if k == 3:
                k += 1
            pri1 = driver.find_element_by_xpath("""//*[@id="resultsContainer"]/section/article["""+str(k)+"""]/div/div/div/div[2]/ul[@class="hotel-price"]/li[@class="actualPrice price show-when-muted fakeLink"]""").text.encode('utf8')
            pri2 = pri1.split("\n")
            #pric = pri2[len(pri2)-1]
            if pri1 != "":
                #print "ada harga"
                #print ""+pric
                price.append(pri2[len(pri2)-1])   

        except NoSuchElementException:
            try:
                #soldout
                harga = driver.find_element_by_xpath("""//*[@id="resultsContainer"]/section/article["""+str(k)+"""]/div/div[1]/div[2]/div[2]/li[@class="error errorText secondary"]/span""").text.encode('utf8')
                #harga = driver.find_element_by_xpath("""//*[@id="resultsContainer"]/section/article["""+str(k)+"""]/div/div[1]/div[2]/div[2]/ul[@class="hotel-price"]/li[@class="actualPrice price show-when-muted fakeLink"]""").text.encode('utf8')
                harga2 = harga.split("\n")
                price.append(harga2[len(harga2)-1])
                #harga = driver.find_element_by_xpath("""//*[@id="hotel"""+str(k)+""""]/div[1]/div/div/div[2]/div[2]/li[1]/span""").text.encode('utf8') 
            except NoSuchElementException:
                price.append("")
        
        k+=1
    return price
    
# function to get the star data of the hotel, returned the list,
# not every hotel has stars data, so if there is no star data, this fucntion will fill it with empty space
def EXstarALT(jum):
    star = []
    k = 1
    while len(star)<jum:
        try:
            if k == 3:
                k += 1
            bintang = driver.find_element_by_xpath("""//*[@id="resultsContainer"]/section/article["""+str(k)+"""]/div/div/div/div[1]/ul[1]/li/strong/span""").text.encode('utf8')
            #print ""+bintang
            star.append(bintang)
        except NoSuchElementException:
            #if k==3:
                #k+=1
            #try:
                #bintang = driver.find_element_by_xpath("""//*[@id="resultsContainer"]/section/article["""+str(k)+"""]/div/div/div/div[1]/ul[1]/li/strong/span""").text.encode('utf8')
                #print ""+bintang
                #star.append(bintang)
            #except NoSuchElementException:
            star.append("")
        k+=1
    return star 

# function to get the promo data of the hotel, returned the list,
# not every hotel has promo data, so if there is no star data, this fucntion will fill it with empty space

def EXpromoALT(jum):
    promo = []
    k = 1
    while len(promo)<jum:
        try:
            prom = driver.find_element_by_xpath("""//*[@id="resultsContainer"]/section/article["""+str(k)+"""]/div/div/div/div[1]/ul[1]/li[1]""").text.encode('utf8')
            promo.append(prom)
        except NoSuchElementException:
            promo.append("")
        k+=1
    return promo
    
    
# function to get the rating data of the hotel, returned the list,
# not every hotel has stars data, so if there is no rating data, this fucntion will fill it with empty space    
def EXratingALT(jum):
    rating = []
    k = 1
    while len(rating)<jum:
        try:
            #print "coba ambil rating"
            if k == 3:
                k += 1
            rat = driver.find_element_by_xpath("""//*[@id="resultsContainer"]/section/article["""+str(k)+"""]/div/div/div/div[2]/ul[1]/li[@class="reviewOverall"]/span[2]""").text.encode('utf8')
            print ""+rat
            rating.append(rat)
            
        except NoSuchElementException:
            try:
                if k==3:
                    k+=1
                rat = driver.find_element_by_xpath("""//*[@id="resultsContainer"]/section/article["""+str(k)+"""]//div/div/div/div[2]/ul[1]/li[@class="reviewOverall"]/span[2]""").text.encode('utf8')
                rating.append(rat)
            except NoSuchElementException:
                rating.append("")
        k+=1
    return rating
# function to get the star data of the hotel, returned the list,
# not every hotel has stars data, so if there is no star data, this fucntion will fill it with empty space
# This is the function to click the next button if clickable, if not but it's not the end of the city, it will try again
# this is also a recursive function
def nextPage():
    try:
        #print "masuk next"
        WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, """//*[@id="paginationContainer"]/div/nav/fieldset/div/button[@class="pagination-next"]"""))).click()
        return "OK"
    except TimeoutException:
        return "HABIS"
    except WebDriverException:
        print "WebDriver Exc"
        time.sleep(2.5)
        return nextPage()

# Function to get all the data at store it to different list, EX is refering to expedia, and BEX mean Big list
# this function will store data into small list, as it only one page
# this is a recursive function, it will keep trying until reach its goal
def EXscrap(kota):
    try:
        WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.XPATH, """//*[@id="bcol"]""")))
    #if exception appear, it will try again    
    except TimeoutException:
        print "Too long to Load"
        driver.refresh()
        return EXscrap(kota)
        
    listName = []
    listLocation =[]
    listPrice =[]
    listStar =[]
    listPromo =[]
    listRating =[]
    
    
    try:
        #print "scrap kota"
        listName = EXname()
        listLocation = EXlocation()
        listPrice = EXpriceALT(len(listName))
        listStar = EXstarALT(len(listName))
        listPromo = EXpromoALT(len(listName))
        listRating = EXratingALT(len(listName))

        #pjg = len(listName)
        #print ""+pjg
        for i in range(0,len(listName)):
            BEXkota.extend([kota])
        BEXname.extend(listName)
        BEXlocation.extend(listLocation)
        BEXprice.extend(listPrice)
        BEXstar.extend(listStar)
        BEXpromo.extend(listPromo)
        BEXrating.extend(listRating)
        
        
        
    #if exception appear, it will try again    
    except StaleElementReferenceException:
        print "Retry Scraping"
        driver.refresh()
        time.sleep(2)
        WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.XPATH, """//*[@id="bcol"]""")))
        return EXscrap(kota)
        
        
# This function consist of EXscrap(kota), and nextPage(), this function will get the data and click the next button
# until the end of the search result             
def EXscrapPagin(kota):
    time.sleep(2)   
    while True:
        time.sleep(2)
        EXscrap(kota)
        np = nextPage()
        if np=="HABIS":
            break

# This function will open the chosen one, whether the user choose IDR,USD, or AUD as their reference currency

def EXcurrency(currency,city,dat):
    try:
        if currency == 1:
            driver.get("https://www.expedia.co.id/Hotel-Search?#&destination="+city+", Indonesia&startDate="+dat+"&endDate="+nextDate(dat))
        elif currency ==2:
            driver.get("https://www.expedia.com/Hotel-Search?#&destination="+city+", Indonesia&startDate="+USdateFormat(dat)+"&endDate="+USdateFormat(nextDate(dat)))       
        elif currency==3:
            driver.get("https://www.expedia.com.au/Hotel-Search?#&destination="+city+", Indonesia&startDate="+dat+"&endDate="+nextDate(dat))
    except TimeoutException: 
        print "Kelamaan, Ngulang Dulu"
        return EXcurrency(currency,city,dat)

# This function will write all the data to the external file with .csv as its format, 
# and it will be stored to the chosen directory                                
def EXnulis(pjg,path,nam):
    with open(path+nam+'.csv','ab') as csvfile:
        for j in range(0,pjg):
            ciswriter = csv.writer(csvfile, delimiter=',',quoting=csv.QUOTE_MINIMAL)
            ciswriter.writerow([BEXname[j],BEXstar[j],BEXlocation[j],BEXprice[j],BEXkota[j],BEXrating[j],BEXpromo[j]])

###### MAIN PROGRAM #########
for kota in range(0,len(citytoscrap)):
    BEXname = []
    BEXkota = []
    BEXprice = []
    BEXlocation = []
    BEXstar = []
    BEXpromo = []
    BEXrating = []
  
    
    cd = pathcd
    os.environ["webdriver.chrome.driver"] = cd
    driver = webdriver.Chrome(cd)
    
    EXcurrency(currencies,citytoscrap[kota],dat)
    EXscrapPagin(citytoscrap[kota])
    
    
    print "Total hotel di "+citytoscrap[kota]+ " : " +str(len(BEXname)) +" ------ ",
    nt = datetime.datetime.now().time()
    print nt.strftime("%H:%M:%S") 
    driver.quit()   
    EXnulis(len(BEXname),pathsave,outname)
      

et = datetime.datetime.now().time()
print (et.strftime("%H:%M:%S"))

