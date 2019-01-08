import time, string, random, os, _thread, zbarlight, re
import urllib.request as urllib
from PIL import Image

THREAD_AMOUNT = 128
NONE_WORKING = [0, 503, 5082, 4939, 4940, 4941, 12003, 5556]

valid_qr = 0
valid_img = 0
invalid_img = 0
invalid_url = 0

def check_image(url, filename):
    global invalid_img
    global valid_img
    global valid_qr

    try:
        with Image.open(filename).convert('RGBA') as img:
            img.load()
            qr_codes = zbarlight.scan_codes('qrcode', img)
    except:
        invalid_img += 1
        return
    valid_img += 1
    if qr_codes:
        valid_qr += 1
        with open('valid_qr_codes.txt', 'a') as qr_file:
            for qr_code in qr_codes:
                try:
                    qr_data = qr_code.decode('ascii', errors='replace')
                except:
                    pass

                print("{} - {}".format(qr_data, url))
                qr_file.write("{} - {}\n".format(qr_data, url))

                if ((re.match(r'5(H|J|K).{49}$', qr_data) or      # match private key (WIF, uncompressed pubkey) with length 51
                   re.match(r'(K|L).{51}$', qr_data) or           # match private key (WIF, compressed pubkey) with length 52
                   re.match(r'S(.{21}|.{29})$', qr_data)) and     # match mini private key with length 22 (deprecated) or 30
                   re.match(r'[1-9A-HJ-NP-Za-km-z]+', qr_data)):  # match only BASE58
                    print('^^^ Possibly Satoshi Nakamoto ^^^')
                    qr_file.write('^^^ Possibly Satoshi Nakamoto ^^^\n')

def scrape_pictures():
        global invalid_url
        while True:
            url = 'http://i.imgur.com/'
            length = random.choice((5, 6))
            if length == 5:
                url += ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(5))
            else:
                url += ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(3))
                url += ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(3))
            url += '.jpg'

            filename = url.rsplit('/', 1)[-1]
            
            try:
                urllib.urlretrieve(url, filename)
            except:
                invalid_url += 1
                continue
            file_size = os.path.getsize(filename)

            if file_size in NONE_WORKING:
                invalid_url += 1
                os.remove(filename)
            else:
                check_image(url, filename)
                os.remove(filename)

def stats():
    while True:
        time.sleep(120)
        print('---STATISTICS---')
        print('valid_qr = ' + str(valid_qr))
        print('valid_img = ' + str(valid_img))
        print('invalid_img = ' + str(invalid_img))
        print('invalid_url = ' + str(invalid_url))
        print('total_processed = ' + str(valid_img + invalid_img + invalid_url))


print('Welcome to imgur-qr-btc scraper!')
for thread in range(1, THREAD_AMOUNT + 1):
    thread = str(thread)
    try:
        _thread.start_new_thread(scrape_pictures, ())
    except:
        print('Error starting thread ' + thread)
_thread.start_new_thread(stats, ())
print('Succesfully started ' + thread + ' threads, enjoy!')

while True:
    time.sleep(1)