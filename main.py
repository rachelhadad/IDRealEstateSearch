import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.action_chains import ActionChains
import json
import time


# Doesn't account for acreage

DRIVER_PATH = os.environ.get("chrome_driver_path")
MAX_PRICE = 500
ZIP_CODES = ["83406", "83402", "83401", "83404", "83442"]
FLAG_PHRASE = ["investor special", "needs some work", "needs work", "tlc"]

with open("listings.json", "r+") as json_file:
    json_listings_dict = json.load(json_file)


def get_listings():
    all_listings_info = []

    # Enter search criteria
    driver = webdriver.Chrome(executable_path=DRIVER_PATH)
    action = ActionChains(driver)
    driver.get("https://www.snakerivermls.com/default.asp?content=search&menu_id=19710")
    max_price_input = driver.find_element_by_id("item2a")
    max_price_input.send_keys(MAX_PRICE)
    single_family_checkbox = driver.find_element_by_id("item5RR")
    single_family_checkbox.click()
    condo_twnhm_twin_checkbox = driver.find_element_by_id("item5RN")
    condo_twnhm_twin_checkbox.click()
    zip_dropdown = Select(driver.find_element_by_id("item12"))
    action.key_down(Keys.CONTROL)
    for each in ZIP_CODES:
        zip_dropdown.select_by_value(each)
    action.key_up(Keys.CONTROL)
    sort_by_dropdown = Select(driver.find_element_by_id("sortBy"))
    sort_by_dropdown.select_by_value("1")
    driver.find_element_by_xpath("/html/body/div[2]/div[6]/div[2]/div/div[2]/div/div[3]/div/div/button").click()

    # Go into each listing, then find the price/sq ft. or if description contains flag phrases
    first_listing = driver.find_element_by_xpath("/html/body/div[2]/div[6]/div[2]/div/div[2]/div/section/div/div[1]/div[1]/div/a/img")
    first_listing.click()
    for n in range(30):
        try:
            list_price = driver.find_element_by_xpath("/html/body/div[2]/div[6]/div[2]/div/div[2]/div/div[7]/div[1]/div[1]/span[2]").text
            if list_price:
                num = 7
        except:
            num = 9
        finally:
            list_price = driver.find_element_by_xpath(f"/html/body/div[2]/div[6]/div[2]/div/div[2]/div/div[{num}]/div[1]/div[1]/span[2]").text
            sq_ft = int(driver.find_element_by_xpath(
                f"/html/body/div[2]/div[6]/div[2]/div/div[2]/div/div[{num}]/div[2]/div[3]/span[2]").text)
            # Get mls in order to use in if statement later
            mls = driver.find_element_by_xpath(
                f"/html/body/div[2]/div[6]/div[2]/div/div[2]/div/div[{num}]/div[1]/div[14]/span[2]").text
            # Get listing description and search for flag phrases
            listing_description = driver.find_element_by_xpath(
                f"/html/body/div[2]/div[6]/div[2]/div/div[2]/div/div[{num}]/div[2]/div[6]/span[2]").text
            # convert list_price from str to int
            list_price_split = list_price.split("$")[1]
            list_price_int = int(list_price_split.replace(",", ""))
            # Calculate price per square foot
            price_per_sqft = round(list_price_int / sq_ft, 2)

        for phrase in FLAG_PHRASE:
            if phrase in listing_description:
                flag_phrase = "yes"
                print(flag_phrase)
            else:
                flag_phrase = "no"
        # Send info to all_listings_info
        info_dict = {
            "mls": mls,
            "url": driver.current_url,
            "img": driver.find_element_by_id("main_photo").get_attribute("src"),
            "price": list_price,
            "bedrooms": driver.find_element_by_xpath(f"/html/body/div[2]/div[6]/div[2]/div/div[2]/div/div[{num}]/div[1]/div[2]/span[2]").text,
            "bathrooms": driver.find_element_by_xpath(f"/html/body/div[2]/div[6]/div[2]/div/div[2]/div/div[{num}]/div[1]/div[3]/span[2]").text,
            "street": driver.find_element_by_xpath(f"/html/body/div[2]/div[6]/div[2]/div/div[2]/div/div[{num}]/div[2]/div[15]/span[2]").text,
            "city": driver.find_element_by_xpath(f"/html/body/div[2]/div[6]/div[2]/div/div[2]/div/div[{num}]/div[1]/div[15]/span[2]").text,
            "state": driver.find_element_by_xpath(f"/html/body/div[2]/div[6]/div[2]/div/div[2]/div/div[{num}]/div[1]/div[16]/span[2]").text,
            "zip": driver.find_element_by_xpath(f"/html/body/div[2]/div[6]/div[2]/div/div[2]/div/div[{num}]/div[2]/div[11]/span[2]").text,
            "acres": driver.find_element_by_xpath(f"/html/body/div[2]/div[6]/div[2]/div/div[2]/div/div[{num}]/div[2]/div[2]/span[2]").text,
            "sqft": driver.find_element_by_xpath(f"/html/body/div[2]/div[6]/div[2]/div/div[2]/div/div[{num}]/div[2]/div[3]/span[2]").text,
            "ppsqft": price_per_sqft,
            "flag_phrase": flag_phrase
        }
        # if listing has desirable price/sq ft or any flag phrases, include in all_listings_info list
        if price_per_sqft < 115 or flag_phrase == "yes":
            # Check if MLS is in current listings.json file (i.e. was already sent in email)
            if len(json_listings_dict) > 0:
                for num in range(len(json_listings_dict)):
                    if mls == json_listings_dict[num]["mls"]:
                        print("MLS in current JSON file. Not added to listings list.")
                    else:
                        all_listings_info.append(info_dict)
                        print("Property added to listings list.")
            else:
                all_listings_info.append(info_dict)
                print("Property added to listings list.")
        else:
            print("Property does not meet criteria and was not added to listings list.")
        next_listing_link = driver.find_element_by_xpath("/html/body/div[2]/div[6]/div[2]/div/div[2]/div/div[1]/div/div[2]/a")
        next_listing_link.click()
        with open("listings.json", "w") as listings_file:
            json_object = json.dumps(all_listings_info, indent=4)
            listings_file.write(json_object)
    print(all_listings_info)
    return all_listings_info