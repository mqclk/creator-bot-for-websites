import os, random, json
from multiprocessing import Process
import zipfile
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By

with open('Config.json', 'r') as openfile:
    # Reading from json file
    json_object = json.load(openfile)


link = json_object['url']
py = json_object['proxy']
port = json_object['port']
user = json_object['user']
passw = json_object['passw']
thread = int(json_object['thread'])


PROXY_HOST = py  
PROXY_PORT = port
PROXY_USER = user
PROXY_PASS = passw


manifest_json = """
{
    "version": "1.0.0",
    "manifest_version": 2,
    "name": "Chrome Proxy",
    "permissions": [
        "proxy",
        "tabs",
        "unlimitedStorage",
        "storage",
        "<all_urls>",
        "webRequest",
        "webRequestBlocking"
    ],
    "background": {
        "scripts": ["background.js"]
    },
    "minimum_chrome_version":"22.0.0"
}
"""

background_js = """
var config = {
        mode: "fixed_servers",
        rules: {
          singleProxy: {
            scheme: "http",
            host: "%s",
            port: parseInt(%s)
          },
          bypassList: ["localhost"]
        }
      };

chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

function callbackFn(details) {
    return {
        authCredentials: {
            username: "%s",
            password: "%s"
        }
    };
}

chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {urls: ["<all_urls>"]},
            ['blocking']
);
""" % (PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)


def get_chromedriver(use_proxy=False, user_agent=None):
    path = os.path.dirname(os.path.abspath(__file__))
    chrome_options = webdriver.ChromeOptions()
    if use_proxy:
        pluginfile = 'proxy_auth_plugin.zip'

        with zipfile.ZipFile(pluginfile, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)
        chrome_options.add_extension(pluginfile)
        chrome_options.add_argument("--log-level=3")
        prefs = {"profile.managed_default_content_settings.images": 1}
        chrome_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(
        os.path.join(path, 'chromedriver'),
        options=chrome_options)
    return driver

def main():
    
    while True:
        li_element = []
        try:
            driver = get_chromedriver(use_proxy=True)
            driver.maximize_window()
            driver.get(link)
            driver.implicitly_wait(10)
            
            li_element = driver.find_element(By.CLASS_NAME,"social").find_element(By.CLASS_NAME,'social-icons').find_elements(By.TAG_NAME,"a")
            social_share = driver.find_element(By.CLASS_NAME,"social").find_element(By.TAG_NAME,"a")
            sleep(1)
            

        except Exception as e:
            pass
        main_window = driver.current_window_handle

        # click on favorite button 
        try:
            driver.execute_script("document.querySelector('.token-name').querySelector('a').click();")
        except:
            pass

        #___________________________________________ Click on  website
        for url in li_element:
            try:
                driver.execute_script("arguments[0].click();", url)
                sleep(10)
                new_window = driver.window_handles[1]
                driver.switch_to.window(new_window)
                sleep(10)
                driver.close()
                driver.switch_to.window(main_window)
            except Exception as e:
                pass
        
        
        # _________________________________________share button click and open model window
        try:
            driver.execute_script("arguments[0].click();", social_share)
            sleep(2)
            model_content = driver.find_element(By.CLASS_NAME,"modal-content")


            # ______________________________________ looping over each social site
            try:
                social_link = model_content.find_elements(By.TAG_NAME,"a")
                # for _ in random.randint(0,2):
                driver.execute_script("arguments[0].click();", social_link[random.randint(0,2)])
                sleep(10)
                new_window = driver.window_handles[1]
                driver.switch_to.window(new_window)
                driver.close()
                driver.switch_to.window(main_window)
            except Exception as e:
                pass
        except Exception as e:
            pass

        # _______________________________________________________ Close model window
        try:
            driver.execute_script("document.querySelector('.modal-content').querySelector('button').click();")
        except Exception as e:
            pass

        driver.delete_all_cookies()
        driver.quit()



if __name__=='__main__':
    for _ in range(thread):
        process_obj = Process(target=main)
        process_obj.start()

    for __ in range(thread):
        process_obj.join()
