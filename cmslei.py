import os
import requests
from bs4 import BeautifulSoup
from threading import Thread
from queue import Queue

linux = 'clear'
windows = 'cls'
os.system([linux, windows][os.name == 'nt'])

print("""
  _____               _          _ 
 / ____|             | |        (_)
| |     _ __ ___  ___| |     ___ _ 
| |    | '_ ` _ \/ __| |    / _ \ |
| |____| | | | | \__ \ |___|  __/ |______________
 \_____|_| |_| |_|___/______\___|_|FOR WORDPRESS ]
 
[i] Multi scanner fast and powerful for websites that use WordPress CMS!
[@] Telegram: t.me/rahmanralei
""")

filename = input('[?] List Domain File: ')
if not os.path.isfile(filename):
    print(f'[x] File {filename} not found!')
    exit()
num_threads = int(input('[?] Thread: '))
timeout = float(input('[?] Timeout (sec): '))
print("")

def detect_wordpress(url):
    try:
        response = requests.get(url, timeout=timeout)
        soup = BeautifulSoup(response.text, 'html.parser')
        generator_tag = soup.find('meta', attrs={'name': 'generator', 'content': 'WordPress'})
        if generator_tag:
            return True
        style_tag = soup.find('link', attrs={'rel': 'stylesheet', 'href': '/wp-content/'})
        if style_tag:
            return True
        wp_scripts = soup.find_all('script', attrs={'src': lambda x: x and 'wp-includes' in x})
        if wp_scripts:
            return True
        return False
    except requests.exceptions.RequestException:
        return None
    except:
        pass

def worker():
    try:
        while True:
            url = q.get()
            domen = url.replace('http://', '').replace('https://', '')
            is_wordpress = detect_wordpress(url)
            if is_wordpress is None:
                print(f"[!] \033[33m{domen} -> Request Timeout !\033[0m")
            elif is_wordpress:
                print(f'[+] \033[92m{domen} -> WordPress !\033[0m')
                wp_count.put(1)
                with open('wpsite.txt', 'a') as f:
                    f.write(domen + '\n')
            else:
                print(f'[-] \033[91m{domen} -> Not Wordpress !\033[0m')
            q.task_done()
    except:
        pass

with open(filename, 'r') as file:
    listwp = file.read().splitlines()

# Remove duplicates from the list of websites
listwp = list(set(listwp))

q = Queue()
wp_count = Queue()

for url in listwp:
    if not url.startswith('http') and not url.startswith('https'):
        url = 'http://' + url
    elif not url.startswith('https') and not url.startswith('http'):
        url = 'https://' + url
    q.put(url)

for i in range(num_threads):
    t = Thread(target=worker)
    t.daemon = True
    t.start()

q.join()
total_wp = wp_count.qsize()

print(f'\n- Total found WordPress: \033[92m{total_wp}\033[0m')
print(f'- Total not found: \033[91m{len(listwp) - total_wp}\033[0m')
print(f"- Thank For Using, Result Save To (wpsite.txt)")
