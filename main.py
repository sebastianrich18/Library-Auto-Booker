import json
import datetime
from time import sleep
from secret import *
from selenium import webdriver
from twilio.rest import Client
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC

LINK = "https://booking.lib.buffalo.edu/reserve/silverman"
datesXPath = '//*[@id="eq-time-grid"]/div[2]/div/table/thead/tr/td[3]/div/div/div/table/tbody/tr'
slotsXPath = '//*[@id="eq-time-grid"]/div[2]/div/table/tbody/tr/td[3]/div/div/div/table/tbody'


def sendConfirm(phoneNumber, url):
    client = Client(twilioSID, twilioAuthToken)
    client.messages.create(to=phoneNumber, from_='+15407128016', body='Booking Made! Check your email for verfication. If you do not verify within 2 hours of this text, your booking will be cancled', media_url=[url])


def waitThenType(path, text, driver):  # wait for element to load then type
    try:
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, path)))
        driver.find_element_by_xpath(path).send_keys(text)
    except TimeoutException:
        print("Failed to load", path)

def waitThenClick(path, driver):
    try:
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, path)))
        driver.find_element_by_xpath(path).click()
    except TimeoutException:
        print("Failed to load", path)

def tryToBook(fName, lName, email, targetDateTime):
    print(fName, lName, email, targetDateTime)
    options = Options()
    options.add_argument("--headless")  # makes chrome window not show
    options.add_argument("log-level=3")  # surpresses warnings
    driver = webdriver.Chrome('public/booker/chromedriver', options=options)

    driver.get(LINK)

    rows = driver.find_element_by_xpath(slotsXPath).find_elements_by_tag_name("tr")
    avalableElement = None

    print("searching for avalability")
    for row in rows:
        cols = row.find_element_by_tag_name("td").find_element_by_class_name("fc-timeline-lane-frame").find_element_by_class_name("fc-scrollgrid-sync-inner").find_elements_by_class_name("fc-timeline-event-harness")
        for col in cols:
            elm = col.find_element_by_tag_name("a")
            str = elm.get_attribute("title") # title: 5:00am Thursday, October 21, 2021 - Room 04 - Unavailable/Padding
            arr = str.split(" ") 
            hour = int(arr[0].split(":")[0])
            if (arr[0].split("00")[1] == 'am' and hour == 12):
                hour = 0
            elif (arr[0].split("00")[1] == 'pm' and hour != 12):
                hour += 12
            # print(hour, str)
            date = int(arr[3][:-1])
            month = int(datetime.datetime.strptime(arr[2], "%B").month)
            year = int(arr[4])
            # print(year, month, date, hour)
            currentTime = datetime.datetime(year, month, date, hour=hour, minute=0, second=0)
            if (currentTime == targetDateTime and arr[-1] == "Available"):
                # print("found current time", arr[-1] and arr[-1] == "Available")
                avalableElement = elm
                break

    if avalableElement is not None:
        print("found avalable booking")
        print(avalableElement.get_attribute("title"))
    else:
        print("no bookings avalable for that time")
        return False

    avalableElement.click()

    waitThenClick('//*[@id="submit_times"]', driver)
    waitThenClick('//*[@id="terms_accept"]', driver)

    waitThenType('//*[@id="fname"]', fName, driver)
    waitThenType('//*[@id="lname"]', lName, driver)
    waitThenType('//*[@id="email"]', email, driver)

    waitThenClick('//*[@id="btn-form-submit"]', driver)

    sleep(1)

    dateStr = targetDateTime.strftime("%H:%M_%m-%d-%Y")
    filename = "public/booker/screenshots/" + dateStr + "_" + lName + ".png"
    driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.HOME) # scroll to the top
    sleep(1)
    driver.save_screenshot(filename)
    driver.quit()
    url = "https://srichel.com/" + filename[7:]
    return url


if __name__ == '__main__':
    queue = {}
    with open("public/booker/queue.json", 'r') as file:
        queue = json.load(file)
    for i in range(len(queue)):
        dateTime = datetime.datetime.utcfromtimestamp(int(queue[i]['targetDateTime']))
        url = tryToBook(queue[i]['fname'], queue[i]['lname'], queue[i]['email'], dateTime)
        if url is not False:
            print("booking made! confermation url: ", url)
            sendConfirm(queue[i]['phoneNumber'], url)
            queue.pop(i)
    with open("public/booker/queue.json", 'w') as file:
        file.write(json.dumps(queue))
    sendConfirm('+17163450818', url)