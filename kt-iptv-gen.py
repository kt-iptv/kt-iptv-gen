from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
import time
import logging

log_fmt = "%(asctime)-15s %(levelname)-8s %(lineno)03d %(message)s"
formatter = logging.Formatter(log_fmt, datefmt='%Y/%m/%d %H:%M:%S')

log = logging.getLogger(__name__)
consolehandler = logging.StreamHandler()
consolehandler.setFormatter(formatter)
log.addHandler(consolehandler)
#log.setLevel(getattr(logging, args['loglevel']))
log.setLevel(logging.DEBUG)


tab_triggers_text = [] # 상품 대분류 텍스트
sub_triggers_text = [] # 상품 중분류 텍스트
chn_triggers_text = [] # 상품 소분류 텍스트
channels_text = []     # 채널 텍스트

chrome_options = Options()
#chrome_options.add_argument('headless')
chrome_options.add_argument("disable-gpu")
#chrome_options.add_argument("--window-size=1000,1000")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
browser = webdriver.Chrome('chromedriver', options=chrome_options)
browser.get('https://tv.kt.com/')

def wait_for_end_of_load():
    WebDriverWait(browser, 10).until(lambda d: d.execute_script("return jQuery.active == 0"))

def get_tab_triggers():
    return browser.find_elements_by_xpath('//div[@class="tabs half"]/ul[@class="channel_content"]/li/a[@class]')

def get_sub_triggers():
    return browser.find_elements_by_xpath('//div[@class]/a[starts-with(@class,"sub-trigger")]')

def get_chn_triggers():
    return browser.find_elements_by_xpath('//div[@class="channel_triggers"]/ul[@class]/li/a[starts-with(@class,"trigger")]')

def get_channels():
    return browser.find_elements_by_xpath('//div[@class="channel_lists"]/ul[@class]/li/a[starts-with(@id,"linkChannel")]')

def build_triggers_text(get_triggers_fn, triggers_text, prefix):
    triggers = get_triggers_fn()
    triggers_text.clear()
    for trigger in triggers:
        if trigger.text and not trigger.get_attribute('title'):
            text = trigger.text
            triggers_text.append(text)
    log.debug(f'{prefix}: {triggers_text}')

def select_trigger(get_triggers_fn, text, link):
    triggers = get_triggers_fn()
    for tab in triggers:
        if text == tab.text:
            fn = tab.get_attribute(link)
            browser.execute_script(fn)
            break
    wait_for_end_of_load()

def build_tab_triggers_text():
    build_triggers_text(get_tab_triggers, tab_triggers_text, "TAB")

def select_tab_trigger(text):
    select_trigger(get_tab_triggers, text, 'href')

def build_sub_triggers_text():
    build_triggers_text(get_sub_triggers, sub_triggers_text, "SUB")

def select_sub_trigger(text):
    select_trigger(get_sub_triggers, text, 'onclick')

def build_chn_triggers_text():
    build_triggers_text(get_chn_triggers, chn_triggers_text, "CHT")

def select_chn_trigger(text):
    select_trigger(get_chn_triggers, text, 'onclick')

def build_channels_text():
    build_triggers_text(get_channels, channels_text, "CHN")    

def select_channel(text):
    select_trigger(get_channels, text, 'href')

def print_tag_sub_chn_all():
    build_tab_triggers_text()
    for tab, tab_text in enumerate(tab_triggers_text, start=1):
        print(tab, tab_text)
        select_tab_trigger(tab_text)

        build_sub_triggers_text()
        for sub, sub_text in enumerate(sub_triggers_text, start=1):
            print(' '*4, tab, sub, sub_text)
            select_sub_trigger(sub_text)

            build_chn_triggers_text()
            for chn, chn_text in enumerate(chn_triggers_text, start=1):
                print(' '*8, tab, sub, chn, chn_text)

def print_channel_list(atab, asub, achn):
    build_tab_triggers_text()
    for tab, tab_text in enumerate(tab_triggers_text, start=1):
        if atab == tab:
            print(tab, tab_text)
            select_tab_trigger(tab_text)

            build_sub_triggers_text()
            for sub, sub_text in enumerate(sub_triggers_text, start=1):
                if asub == sub:
                    print(' '*4, tab, sub, sub_text)
                    select_sub_trigger(sub_text)

                    build_chn_triggers_text()
                    for chn, chn_text in enumerate(chn_triggers_text, start=1):
                        if achn == chn:
                            print(' '*8, tab, sub, chn, chn_text)
                            select_chn_trigger(chn_text)

                            build_channels_text()
                            for num, channel_text in enumerate(channels_text, start=0):
                                print(' '*12, tab, sub, chn, num, channel_text)

def select_tab_sub_chn(atab, asub, achn):
    build_tab_triggers_text()
    for tab, tab_text in enumerate(tab_triggers_text, start=1):
        if atab == tab:
            select_tab_trigger(tab_text)

            build_sub_triggers_text()
            for sub, sub_text in enumerate(sub_triggers_text, start=1):
                if asub == sub:
                    select_sub_trigger(sub_text)

                    build_chn_triggers_text()
                    for chn, chn_text in enumerate(chn_triggers_text, start=1):
                        if achn == chn:
                            select_chn_trigger(chn_text)


#print_tag_sub_chn_all()

#print_channel_list(2, 2, 2)

select_tab_sub_chn(2, 2, 2)
build_channels_text()

udp_iptv = 'udp://@239.255.42.42:5004'
m3u_filename = './kt-iptv.m3u8'
m3u = open(m3u_filename, 'w', encoding="utf-8", newline='\n')
m3u.write('#EXTM3U\n\n')
for channel in channels_text:
    list = channel.split(' ', maxsplit=1)
    m3u.write(f'#EXTINF: tvg-id="{list[0]}", {list[1]}\n')
    m3u.write(f'{udp_iptv}?channel={list[0]}\n\n')
m3u.close()

print(channels_text[100])
select_channel(channels_text[100])

guide = browser.find_elements_by_xpath('//div[@class="tbl_area"]/table/tbody/tr/td')
pos = 0
for a in guide:
    if a.get_attribute('class') == 'time':
        if 0 == pos:
            print(a.text + 'h')
            pos = 1
        else:
            print(a.text.replace('\n', 'm ') + 'm')
    elif a.get_attribute('class') == 'program':
            if 1 == pos:
                pass
            print('>' + a.text + '<')
            pos = 0
            
time.sleep(5)
browser.quit()
