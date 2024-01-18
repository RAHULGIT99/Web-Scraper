# library imports
from bs4 import BeautifulSoup
import requests
import json
from concurrent import futures
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import re
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


#all function definitions in this section
def main(category_from_web,user_input_from_web): # imported in app.py (flask app) for passing arguments into main function
    def link_constructor(category): #
        category_keys = list(x[category].keys()) # x variable holds the content loaded from json file
        z = input_from_web.strip().split(" ")
        constructed_links = []
        for i in category_keys:
            y = x[category][i]["base_search_url"] # reference in json
            count = 0
            for i in z:
                y += i
                count += 1
                if count < len(z):
                    y += "+"
            constructed_links.append(y)
        return constructed_links,category_keys
    
    def croma_constructor(category):
        y = x[category]['croma']['base_search_url']
        z = input_from_web.strip().split(" ")
        count = 0
        for i in z:
            y += i
            count += 1
            if count < len(z):
                y += "%20"
        y += "%3Arelevance&text="
        count = 0
        for i in z:
            y += i
            count += 1
            if count < len(z):
                y += "%20"
        return y

    def main_parser_executer(): #starts execution of parsing data from the given websites
        with futures.ThreadPoolExecutor() as executor: #used to reduce time complexity by running functions parallelly on different threads (multi-threading)
            result = {}
            future1 = executor.submit(amazon_parser,constructed_links,category_keys,input_from_web)
            future2 = executor.submit(flipkart_parser,constructed_links,category_keys)
            future3 = executor.submit(reliance_parser,constructed_links,category_keys)
            # future4 = executor.submit(croma_parser,constructed_links,category_keys)
            # future5 = executor.submit(jiomart_parser,constructed_links,category_keys)
            # croma_constructor()
            futures.wait([future1,future2,future3]) #waits for response from all threads
            Amazon = future1.result()
            Flipkart = future2.result()
            Reliance = future3.result()
            # Croma = future4.result()
            result["Amazon"] = Amazon
            result["Flipkart"] = Flipkart
            if Reliance == None:
                pass
            else:
                result["Reliance"] = Reliance
            # if Croma == None:
            #     pass
            # else:
            #     result["Croma"] = Croma
        return result
    def separate_numbers_and_alphabets(input_string):
        parts = re.split(r'(\d+)([a-zA-Z]+)', input_string)
        result = ''.join([f"{part} " if i % 3 == 1 else part for i, part in enumerate(parts)]).strip()
        return result

    count1 = 0
    def amazon_parser(constructed_links,category_keys,input_from_web): #fetches the required data from amazon.in
        count1 = 0
        try:
            if "amazon" in category_keys:
                index = category_keys.index("amazon")
                search_url = constructed_links[index]
                response = requests.get(search_url,headers=header)            
                # print(str(response))
                # def resp()
                # if str(response) == "<Response [503]>":
                #     count1 += 1
                #     print(count1)
                #     if count1 == 5:
                #         exit()
                #     else:
                #         amazon_parser(constructed_links,category_keys,input_from_web)
                #     # amazon_parser(constructed_links,category_keys,input_from_web)
                #     # time.sleep(1)
                raw_html = response.text
                content_from_website = BeautifulSoup(raw_html,"lxml")
                container = content_from_website.find("div",class_="sg-col-20-of-24 s-matching-dir sg-col-16-of-20 sg-col sg-col-8-of-12 sg-col-12-of-16")
                common_1 = "sg-col-20-of-24 s-result-item s-asin sg-col-0-of-12 sg-col-16-of-20 sg-col s-widget-spacing-small sg-col-12-of-16"
                common_2 = "sg-col-4-of-24 sg-col-4-of-12 s-result-item s-asin sg-col-4-of-16 sg-col s-widget-spacing-small sg-col-4-of-20"
                # common_3 = "sg-col-20-of-24 s-result-item s-asin sg-col-0-of-12 sg-col-16-of-20 sg-col s-widget-spacing-small sg-col-12-of-16"
                if common_1 in str(container): # for macbook air m1
                    prod = 0
                    amazon = {}
                    internal_container = container.find_all('div',class_="sg-col-20-of-24 s-result-item s-asin sg-col-0-of-12 sg-col-16-of-20 sg-col s-widget-spacing-small sg-col-12-of-16")
                    for i in internal_container:
                        price_element = i.find('span', class_='a-offscreen')
                        if price_element == None:
                            price = "price not found"
                        else:
                            price = price_element.text
                            # print(price_element)
                        image_element = i.find("img",class_="s-image")
                        if image_element == None:
                            image = 'image not found'
                            title_element = 'title not found'
                        else:
                            image = image_element['src']
                            title_element = image_element['alt']
                        link = i.find('a',class_='a-link-normal s-no-outline')
                        hyper_link = x[category]['amazon']["base_url"] + link['href']
                        # print(hyper_link)
                        # image = image_element['src']
                        final_title = title_element.replace(",", " ")
                        final_title = final_title.replace("|", " ")
                        final_title = final_title.replace("[", " ")
                        final_title = final_title.replace("]", " ")
                        final_title = final_title.replace("(", " ")
                        final_title = final_title.replace(")", " ")
                        final_title = final_title.replace("-", " ")
                        final_title = final_title.replace("/", " ")
                        final_title = final_title.replace(";", " ")
                        final_title = final_title.replace(".", " ")
                        final_title = separate_numbers_and_alphabets(final_title)
                        count = 0
                        for k in input_from_web.strip().lower().split(" "):
                            if k in final_title.lower().split(" "):
                                count += 1
                        
                        if count >= len(input_from_web.strip().lower().split(" ")):
                            amazon[f"product_{prod+1}"] = {
                                                                "title" : title_element,
                                                                "price" : price,
                                                                "image" : image,
                                                                "link" : hyper_link
                                                            }
                            prod += 1
                            if prod == 4:
                                break
                    if amazon == {}:
                        print(amazon)
                        return None
                    else:
                        print(amazon)
                        return amazon

                if common_2 in str(container): #eg for kissan jam()
                    prod = 0
                    amazon = {}
                    internal_container = container.find_all('div',class_="sg-col-4-of-24 sg-col-4-of-12 s-result-item s-asin sg-col-4-of-16 sg-col s-widget-spacing-small sg-col-4-of-20")
                    for i in internal_container:
                        price_element = i.find('span', class_='a-offscreen')
                        title_element = i.find('img', class_='s-image')
                        if price_element == None:
                            price = 'price not found'
                        else:
                            price = price_element.text
                        if title_element == None:
                            title = 'Title not found'
                            image = 'Image not found'
                        else:
                            image = title_element['src']
                            title = title_element['alt']
                        link = i.find('a',class_='a-link-normal s-no-outline')
                        hyper_link = x[category]["amazon"]["base_url"] + link['href']
                        # print(hyper_link)
                            # print(title)
                            # print(image)
                            # print(price)

                        final_title = title.replace(",", " ")
                        final_title = final_title.replace("|", " ")
                        final_title = final_title.replace("[", " ")
                        final_title = final_title.replace("]", " ")
                        final_title = final_title.replace("(", " ")
                        final_title = final_title.replace(")", " ")
                        final_title = final_title.replace("-", " ")
                        final_title = final_title.replace("/", " ")
                        final_title = final_title.replace(";", " ")
                        final_title = final_title.replace(".", " ")
                        final_title = separate_numbers_and_alphabets(final_title)

                        count = 0
                        for k in input_from_web.strip().lower().split(" "):
                            if k in final_title.lower().split(" "):
                                count += 1
                        if count == len(input_from_web.strip().lower().split(" ")):
                            amazon[f"product_{prod+1}"] = {
                                                                "title" : title,
                                                                "price" : price,
                                                                "image" : image,
                                                                "link" : hyper_link
                                                            }
                            prod += 1
                            if prod == 4:
                                break
                            # print(amazon)
                    if amazon == {}:
                        return None
                    else:
                        return amazon  
                    
        except requests.exceptions.RequestException as e:
            print("Error making the request to Amazon:", e)
            return None
        except Exception as e:
            print("Error while parsing Amazon data:", e)
            return None

    def flipkart_parser(constructed_links,category_keys):
        try:
            if "flipkart" in category_keys:
                index = category_keys.index("flipkart")
                search_url = constructed_links[index]
                response = requests.get(search_url,headers=header)
                raw_html = response.text
                print(response)
                content_from_website = BeautifulSoup(raw_html,"lxml")
                container = content_from_website.find_all("div",class_="_13oc-S")
                # print(len(container))

                #approved for launch
                if "s1Q9rs" in str(container): #test for jam
                    prod = 0
                    flipkart = {}
                    for i in container:
                        title_element = i.find_all('a', class_='s1Q9rs')
                        price_element = i.find_all('div', class_='_30jeq3')
                        image = i.find_all("img",class_="_396cs4")
                        # link = i.find('a',class_='a-link-normal s-no-outline')

                        for j in range(len(title_element)):
                            hyper_link = x[category]["flipkart"]["base_url"] + title_element[j]['href']
                            final_title = title_element[j].text.replace(",", " ")
                            final_title = final_title.replace("|", " ")
                            final_title = final_title.replace("[", " ")
                            final_title = final_title.replace("]", " ")
                            final_title = final_title.replace("(", " ")
                            final_title = final_title.replace(")", " ")
                            final_title = final_title.replace("-", " ")
                            final_title = final_title.replace("/", " ")
                            final_title = final_title.replace(";", " ")
                            final_title = final_title.replace(".", " ")
                            final_title = separate_numbers_and_alphabets(final_title)
                            count = 0
                            IMAGE = image[j]['src']
                            for k in input_from_web.strip().lower().split(" "):
                                if k in final_title.lower().split(" "):
                                    count += 1
                            if count >= len(input_from_web.strip().lower().split(" ")):
                                flipkart[f"product_{prod+1}"] = {
                                                                    "title" : final_title,
                                                                    "price" : price_element[j].text,
                                                                    "image" : IMAGE,
                                                                    "link": hyper_link
                                                                }
                        prod += 1
                        if prod == 4:
                            break
                    if flipkart == {}:
                        return None
                    else:
                        return flipkart
                
                # ready for launch
                elif "IRpwTa" in str(container): # fossil gen 6
                    prod = 0
                    flipkart = {}
                    internal_container = content_from_website.find_all('div','_1xHGtK _373qXS')
                    # print(len(internal_container))
                    for i in internal_container:
                        title_element1 = i.find('a', class_='IRpwTa')
                        title_element2 = i.find('div', class_='_3eWWd-')
                        title_element3 = i.find('div', class_='_2WkVRV')
                        if '_2WkVRV' in str(internal_container):
                            title = title_element3.text + ' ' + title_element1.text
                        else:
                            title = title_element1.text + ' ' + title_element2.text
                        price_element = i.find('div', class_='_30jeq3')
                        image = i.find("img",class_="_2r_T1I")
                        hyper_link = x[category]["flipkart"]["base_url"] + title_element1['href']
                        
                        final_title = title.replace(",", " ")
                        final_title = final_title.replace("|", " ")
                        final_title = final_title.replace("[", " ")
                        final_title = final_title.replace("]", " ")
                        final_title = final_title.replace("(", " ")
                        final_title = final_title.replace(")", " ")
                        final_title = final_title.replace("-", " ")
                        final_title = final_title.replace("/", " ")
                        final_title = final_title.replace(";", " ")
                        final_title = final_title.replace(".", " ")
                        final_title = separate_numbers_and_alphabets(final_title)
                        count = 0
                        IMAGE = image['src']
                        for k in input_from_web.strip().lower().split(" "):
                            if k in final_title.lower().split(" ") :
                                count += 1
                        if count >= len(input_from_web.strip().lower().split(" ")):
                            flipkart[f"product_{prod+1}"] = {
                                                                "title" : final_title,
                                                                "price" : price_element.text,
                                                                "image" : IMAGE,
                                                                "link": hyper_link
                                                            }
                        prod += 1
                        if prod == 4:
                            break
                    if flipkart == {}:
                        return None
                    else:
                        return flipkart
            
                #approved for launch
                else:
                    prod = 0
                    flipkart = {}
                    for i in container:
                        title_element = i.find('div', class_='_4rR01T')
                        price_element = i.find('div', class_='_30jeq3 _1_WHN1')
                        image_element = i.find('img', class_='_396cs4')
                        link = i.find('a', class_='_1fQZEK')
                        hyper_link = x[category]["flipkart"]["base_url"] + link['href']
                        final_title = title_element.text.replace(",", " ")
                        final_title = final_title.replace("|", " ")
                        final_title = final_title.replace("[", " ")
                        final_title = final_title.replace("]", " ")
                        final_title = final_title.replace("(", " ")
                        final_title = final_title.replace(")", " ")
                        final_title = final_title.replace("-", " ")
                        final_title = final_title.replace("/", " ")
                        final_title = final_title.replace(";", " ")
                        final_title = final_title.replace(".", " ")
                        final_title = separate_numbers_and_alphabets(final_title)
                        count = 0
                        for k in input_from_web.strip().lower().split(" "):
                            if k in final_title.lower().split(" "):
                                count += 1
                        if count >= len(input_from_web.strip().lower().split(" ")):
                            flipkart[f"product_{prod+1}"] = {
                                                                "title" : title_element.text,
                                                                "price" : price_element.text,
                                                                "image" : image_element["src"],
                                                                "link": hyper_link
                                                            }
                        prod += 1
                        if prod == 4:
                            break
                    if flipkart == {}:
                        return None
                    else:
                        return flipkart
        except requests.exceptions.RequestException as e:
            print("Error making the request to Flipkart:", e)
            return None
        except Exception as e:
            print("Error while parsing Flipkart data:", e)
            return None        


    def reliance_parser(constructed_links,category_keys):
        try:
            if "reliance digital" in category_keys:
                index = category_keys.index("reliance digital")
                search_url = constructed_links[index]
                response = requests.get(search_url)
                print(response)
                raw_html = response.text
                content_from_website = BeautifulSoup(raw_html,"lxml")
                container = content_from_website.find_all("li",class_="grid pl__container__sp blk__lg__3 blk__md__4 blk__sm__6 blk__xs__6")
                prod = 0
                reliance = {}
                for i in container:
                    image_element = i.find("img")
                    title_element = image_element['alt']
                    link = i.find('a')
                    hyper_link = x[category]["reliance digital"]["base_url"] + link['href']
                    final_title = title_element.replace(",", " ")
                    final_title = final_title.replace("|", " ")
                    final_title = final_title.replace("[", " ")
                    final_title = final_title.replace("]", " ")
                    final_title = final_title.replace("(", " ")
                    final_title = final_title.replace(")", " ")
                    final_title = final_title.replace("-", " ")
                    final_title = final_title.replace("/", " ")
                    final_title = final_title.replace(";", " ")
                    final_title = final_title.replace(".", " ")
                    final_title = separate_numbers_and_alphabets(final_title)
                    count = 0
                    for k in input_from_web.strip().lower().split(" "):
                        if k in final_title.lower().split(" "):
                            count += 1
                    if count >= len(input_from_web.strip().lower().split(" ")):
                        price_element = i.find('span', class_='TextWeb__Text-sc-1cyx778-0 llZwTv')
                        title_element = image_element['alt']
                        price = price_element.find_all('span')
                        image = x['laptops']['reliance digital']['base_url'] + image_element['data-srcset']
                        # print(title_element,price[1].string,image)
                        reliance[f"product_{prod+1}"] = {
                                                            "title" : final_title,
                                                            "price" : price[1].string,
                                                            "image" : image,
                                                            'link': hyper_link
                                                        }
                        prod += 1
                        if prod == 4:
                            break
                if reliance == {}:
                    return None
                else:
                    return reliance
        except requests.exceptions.RequestException as e:
            print("Error making the request to Reliance Digital:", e)
            return None
        except Exception as e:
            print("Error while parsing Reliance Digital data:", e)
            return None
    def croma_parser(constructed_links,category_keys):
        try:
            if "croma" in category_keys:
                index = category_keys.index("croma")
                search_url = croma_constructor(category)
                print(search_url)
                # chrome_options = Options()
                # chrome_options.add_argument(f"user-agent={user}")
                driver = webdriver.Chrome()
                # driver = webdriver.Chrome(options=chrome_options)
                driver.get(search_url)
                wait = WebDriverWait(driver, 10)
                elements = driver.find_elements(By.CLASS_NAME,"product-item")
                prod = 0
                croma = {}
                for element in elements:
                    price = element.find_element(By.XPATH,".//div/div[2]/div[3]/div/div/span")
                    image = element.find_element(By.XPATH,".//a/img[@src]")
                    anchor = element.find_element(By.XPATH,".//a[@href]")
                    title = element.find_element(By.XPATH,".//div/div[2]/div/h3/a")
                    image_value = image.get_attribute('data-src')
                    href_value = anchor.get_attribute('href')
                    print(title.text)
                    print(href_value)
                    print(image_value)
                    print(price.text)
                    final_title = title.text.replace(",", " ")
                    final_title = final_title.replace("|", " ")
                    final_title = final_title.replace("[", " ")
                    final_title = final_title.replace("]", " ")
                    final_title = final_title.replace("(", " ")
                    final_title = final_title.replace(")", " ")
                    final_title = final_title.replace("-", " ")
                    final_title = final_title.replace("/", " ")
                    final_title = final_title.replace(";", " ")
                    final_title = final_title.replace(".", " ")
                    final_title = separate_numbers_and_alphabets(final_title)
                    count = 0
                    for k in input_from_web.strip().lower().split(" "):
                        if k in final_title.lower().split(" "):
                            count += 1
                    if count >= len(input_from_web.strip().lower().split(" ")):
                        croma[f"product_{prod+1}"] = {
                                                            "title" : title.text,
                                                            "price" : price.text,
                                                            "image" : image_value,
                                                            "link": href_value
                                                        }
                        prod += 1
                        if prod == 4:
                                break
                driver.quit()
            if croma == {}:
                return None
            else:
                return croma
        except requests.exceptions.RequestException as e:
            print("Error making the request to Croma:", e)
            return None
        except Exception as e:
            print("Error while parsing Croma data:", e)
            return None
        
    def jiomart_parser(constructed_links,category_keys):
        try:
            if "jiomart" in category_keys:
                index = category_keys.index("jiomart")
                # search_url = jiomart_constructor(category)
                # print(search_url)
                # chrome_options = Options()
                # chrome_options.add_argument(f"user-agent={user}")
                driver = webdriver.Chrome()
                # driver = webdriver.Chrome(options=chrome_options)
                driver.get("https://www.jiomart.com/search/lg%20washing%20machine")
                wait = WebDriverWait(driver,10)
                elements = driver.find_elements(By.XPATH,'//*[@id="algolia_hits"]/div/div/ol/li')
                # tag_name = "li"
                # class_name = "ais-InfiniteHits-list jm-row jm-mb-massive"
                # elements = driver.find_element(By.CSS_SELECTOR,f'{tag_name}.{class_name}')
                # elements = wait.until(EC.presence_of_element_located((By.CLASS_NAME,"jio-web search-result-page alg_srch_master")))
                print(len(elements))
                prod = 0
                jiomart = {}
                for element in elements:
                    # price = element.find_element(By.XPATH,".//div/div[2]/div[3]/div/div/span")
                    image = element.find_element(By.XPATH,'//*[@id="591053951"]/div[2]/div[1]/div/div[1]/img')
                    anchor = element.find_element(By.XPATH,".//a[@href]")
                    title = element.find_element(By.XPATH,".//a[@title]")
                    # image_value = image.get_attribute('data-src')
                    href_value = anchor.get_attribute('href')
                    title_value = title.get_attribute('title')
                    image_value = title.get_attribute('image')
                    print(title_value)
                    print(href_value)
                    print(image)
                    # print(image_value)
                    # print(price.text)
        #             final_title = title.text.replace(",", " ")
        #             final_title = final_title.replace("|", " ")
        #             final_title = final_title.replace("[", " ")
        #             final_title = final_title.replace("]", " ")
        #             final_title = final_title.replace("(", " ")
        #             final_title = final_title.replace(")", " ")
        #             final_title = final_title.replace("-", " ")
        #             final_title = final_title.replace("/", " ")
        #             final_title = final_title.replace(";", " ")
        #             final_title = final_title.replace(".", " ")
        #             final_title = separate_numbers_and_alphabets(final_title)
        #             count = 0
        #             for k in input_from_web.strip().lower().split(" "):
        #                 if k in final_title.lower().split(" "):
        #                     count += 1
        #             if count >= len(input_from_web.strip().lower().split(" ")):
        #                 jiomart[f"product_{prod+1}"] = {
        #                                                     "title" : title.text,
        #                                                     "price" : price.text,
        #                                                     "image" : image_value,
        #                                                     "link": href_value
        #                                                 }
        #                 prod += 1
        #                 if prod == 4:
        #                         break
        #         driver.quit()
        #     if jiomart == {}:
        #         return None
        #     else:
        #         return jiomart
        except requests.exceptions.RequestException as e:
            print("Error making the request to Croma:", e)
            return None
        except Exception as e:
            print("Error while parsing Croma data:", e)
            return None

    def generator():
        import random
        user_agents = [
            # "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
            # "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
            # "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
            # "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
            # "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:90.0) Gecko/20100101 Firefox/90.0",
            # "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:90.0) Gecko/20100101 Firefox/90.0",
            # "Mozilla/5.0 (X11; Linux i686; rv:90.0) Gecko/20100101 Firefox/90.0",
            # "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15",
            # "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
            # "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59",
            # "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59",
            # "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59",
            # "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36 OPR/76.0.4017.177",
            # "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36 OPR/76.0.4017.177",
            # "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36 OPR/76.0.4017.177",
            # "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",
            # "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
            "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:90.0) Gecko/20100101 Firefox/90.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:90.0) Gecko/20100101 Firefox/90.0",
            "Mozilla/5.0 (X11; Linux i686; rv:90.0) Gecko/20100101 Firefox/90.0"]
        return random.choice(user_agents)
    
    category = category_from_web #"laptops" #will be updated once we figure out how to pass arguments from website to python
    input_from_web = user_input_from_web
    user = generator()
    header={
                "User-Agent":user
            }
    # print(header)
    file = open("C:/Users/masge/Downloads/hello.json","r")
    x = json.load(file)
    constructed_links,category_keys = link_constructor(category)
    result = main_parser_executer()
    file.close()
    return result
