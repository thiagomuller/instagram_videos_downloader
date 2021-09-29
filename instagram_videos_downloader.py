from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
import os
import argparse
from stem import Signal
from stem.control import Controller
import random
import time
from ast import literal_eval
import requests

user_agent_list = [
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
'Mozilla/5.0 (Linux; Android 7.0; SM-G930VC Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/58.0.3029.83 Mobile Safari/537.36',
'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A5370a Safari/604.1'
]

ap = argparse.ArgumentParser()

ap.add_argument("-url", "--url", required=True,
   help="URL of the video to be downloaded")
ap.add_argument("-filename", "--filename", required=True,
help="Name of the video file")

proxies = {
    'http': 'socks5://127.0.0.1:9050',
    'https': 'socks5://127.0.0.1:9050'
}

def change_ip():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate(password=os.environ['TOR_PASSWORD'])
        controller.signal(Signal.NEWNYM)

def request_will_be_sent(**kwargs):
    request = kwargs.get('request')
    if kwargs.get('type') == 'Media':
        cURL = ''
        cURL += "curl --output moskito.mp4 '" + request['url'] + "' "
        for header in request['headers']:
            cURL += " -H '" + header + ":" + request['headers'][header] + "' "
        cURL += "--compressed"
        os.system(cURL)   

def treat_chrome_msg(msg):
    msg = msg.strip()
    msg = msg.replace('false', 'False')
    msg = msg.replace('true', 'True')
    return msg


def find_video_request(logs, filename):
    for log in logs:
        print('\n\n\n')
        try:
            if log['message'] and 'responseReceived' in log['message']:
                if type(log['message']) is str:
                    msg = literal_eval(treat_chrome_msg(log['message']))
                    if 'video/mp4' in msg['message']['params']['response']['headers']['content-type']:
                        video = requests.get(msg['message']['params']['response']['url'], proxies = proxies, stream=True)
                        with open(filename, 'wb') as vd:
                            for chunk in video.iter_content(chunk_size=1024):
                                vd.write(chunk)
        except:
            continue 

args = vars(ap.parse_args())

if not args['url'] or not args['filename']:
    print('usage: ' + os.environ['APP_NAME'] + ' -url <video_url> -filename <filename>')
else:
    print(requests.get('https://ident.me', proxies=proxies).text)
    change_ip()
    print(requests.get('https://ident.me', proxies=proxies).text)
    url = args['url']
    filename = args['filename']
    print(url)
    capabilities = DesiredCapabilities.CHROME
    capabilities["goog:loggingPrefs"] = {"performance": "ALL"} 
    options = webdriver.ChromeOptions()
    options.add_argument("--remote-debugging-port=9225")
    options.add_experimental_option('w3c', False)
    options.add_argument("User-Agent:" + random.choice(user_agent_list))
    options.add_argument("--proxy-server=%s" % proxies['https'])
    driver = webdriver.Chrome(executable_path="./chromedriver", options=options, desired_capabilities=capabilities)
    driver.execute_cdp_cmd('Network.enable', {})
    driver.get(url)
    try:
        playBtn = WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.XPATH, "//div[@role='button']")))
        playBtn.click()
    except NoSuchElementException:
        print('Play button not found!')
    except TimeoutException:
        print('Exception occured when waiting for page to load')
    logs = driver.get_log("performance")
    find_video_request(logs, filename)
    
    driver.close()
