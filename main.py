from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import datetime

LINK = "https://booking.lib.buffalo.edu/reserve/silverman"
datesXPath = '//*[@id="eq-time-grid"]/div[2]/div/table/thead/tr/td[3]/div/div/div/table/tbody/tr'
slotsXPath = '//*[@id="eq-time-grid"]/div[2]/div/table/tbody/tr/td[3]/div/div/div/table/tbody'
fName = "Sebastian"
lName = "Richel"
email = "sjrichel@buffalo.edu"

targetDateTime = datetime.datetime(2021, 10, 22, 4, 0, 0)

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

options = Options()
# options.add_argument("--headless")  # makes chrome window not show
options.add_argument("log-level=3")  # surpresses warnings
driver = webdriver.Chrome('./chromedriver', options=options)

driver.get(LINK)

dates = driver.find_elements_by_xpath(datesXPath)
startDateArr = dates[0].find_elements_by_class_name('fc-timeline-slot-frame')[0].find_element_by_class_name('fc-timeline-slot-cushion').text.split(' ')

startDateMonth = int(datetime.datetime.strptime(startDateArr[1], "%B").month)
startDateDay = int(startDateArr[2][:-1])
startDateYear = int(startDateArr[3])

startDateTime = datetime.datetime(startDateYear, startDateMonth, startDateDay, hour=0, minute=0, second=0)
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
    exit()

avalableElement.click()

waitThenClick('//*[@id="submit_times"]', driver)
waitThenClick('//*[@id="terms_accept"]', driver)

waitThenType('//*[@id="fname"]', fName, driver)
waitThenType('//*[@id="lname"]', lName, driver)
waitThenType('//*[@id="email"]', email, driver)

waitThenClick('//*[@id="btn-form-submit"]', driver)

driver.implicitly_wait(1)


dateStr = targetDateTime.strftime("%H:%M_%m-%d-%Y")
print(dateStr)
driver.save_screenshot(dateStr + "_conformation.png")

driver.quit()