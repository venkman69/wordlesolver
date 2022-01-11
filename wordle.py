from random import randint
from nltk.corpus import words
import copy
from itertools import product
from wordfreq import word_frequency
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By as BY
from selenium.webdriver.common.keys import Keys
import sys
import nltk
import time

nltk.download('words')
 
fullcharset={x:None for x in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" }
WORDLEN=5
print(fullcharset)
print(len(fullcharset))
WORDSET=set()
musthave=set()
for x in words.words():
    if len(x) == WORDLEN:
        # if len(set(x)) != len(x):
            #some repeated alphabets - ignore
            # continue
        if x[0].isupper():
            continue
        WORDSET.add(x.upper())

wordset=copy.deepcopy(WORDSET)
def allpossiblewords():
    global wordset
    charlistcombo=[list(chars.keys()) for x,chars in charmap.items()]
    newwordset=set()
    for x in wordset:
        x = x.upper()
        for char,charset in zip(x.upper(),charlistcombo):
            if not char in charset:
                break
        else:
            checkmusthave=set(x.upper()).intersection(musthave)
            if len(checkmusthave) == len(musthave):
                newwordset.add(x)
    wordset = newwordset
    wordfreq={ word_frequency(x,"en"):x for x in newwordset }
    wordf_sorted=sorted(wordfreq.items(), key=lambda item: item[0], reverse=True)
    return(wordf_sorted)

def sel_wait_for(elemPath, bywhat):
    try:
        element = WebDriverWait(webdriver, 10).until(
        EC.presence_of_element_located((bywhat, elemPath))
        )
        return element
    except:
        browser.quit()
        print("webdriver could not find element:%s"%elemPath)
        sys.exit()
    
charmap={x:copy.deepcopy(fullcharset) for x in range(5) }
topwords = allpossiblewords()
chr_opt = webdriver.ChromeOptions()
chr_opt.add_argument(f'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36')
# chr_opt.add_argument("--headless")

browser_svc = Service(executable_path="./chromedriver")
browser = webdriver.Chrome(service=browser_svc,chrome_options=chr_opt)
browser.get("https://www.powerlanguage.co.uk/wordle/")
time.sleep(2)
body_element=browser.find_element(BY.TAG_NAME,"body")
body_element.click()
# browser.find_element(BY.XPATH,'//*[@id="game"]/game-modal//div/div/div').click()
attempt=1
rowcol='document.querySelector("body > game-app").shadowRoot.querySelector("#board > game-row:nth-child(%s)").shadowRoot.querySelector("div > game-tile:nth-child(%s)")'
solved=False
currentword = topwords[randint(1,100)][1]
while not solved:
    body_element.send_keys(currentword)
    body_element.send_keys(Keys.ENTER)
    time.sleep(2)
    # analyse response
    for col in range(5): 
        currentchar = currentword[col]
        elem=browser.execute_script('return '+rowcol%(attempt,col+1))
        v=elem.get_attribute("evaluation")
        if v == "absent":
            # delete the char from all 5 
            for char in charmap:
                try:
                    del(charmap[char][currentchar])
                except:
                    pass
        if v == "correct":
            charmap[col]={currentchar:None}
            musthave.add(currentchar)
        if v == "present":
            del(charmap[col][currentchar])
            musthave.add(currentchar)
        for c,v in charmap.items():
            if len(v)>1:
                break
        else:
            print("solved: "+currentword)
            solved=True
    topwords=allpossiblewords()
    currentword = topwords[0][1]
    attempt+=1
input("hit enter to close")
browser.close()



