import string, random, os, _thread, zbarlight, re, httplib2
from PIL import Image

THREAD_AMOUNT = 64
NONE_WORKING = [0, 503, 5082, 4939, 4940, 4941, 12003, 5556]

def check_image(url, filename):
    try:
        img = Image.open(filename).convert('RGBA')
        img.load()
        qr_codes = zbarlight.scan_codes('qrcode', img)
    except:
        return

    if qr_codes:
        with open('valid_qr_codes.txt', 'a') as valid_qr:
            for qr_code in qr_codes:
                qr_data = qr_code.decode('ascii', errors='replace')

                print("{} - {}\n".format(qr_data, url))
                valid_qr.write("{} - {}\n".format(qr_data, url))

                if ((re.match(r'5(H|J|K).{49}$', qr_data) or      # match private key (WIF, uncompressed pubkey) with length 51
                   re.match(r'(K|L).{51}$', qr_data) or           # match private key (WIF, compressed pubkey) with length 52
                   re.match(r'S(.{21}|.{29})$', qr_data)) and     # match mini private key with length 22 (deprecated) or 30
                   re.match(r'[1-9A-HJ-NP-Za-km-z]+', qr_data)):  # match only BASE58
                    print('^^^ Possibly Satoshi Nakamoto ^^^')
                    valid_qr.write('^^^ Possibly Satoshi Nakamoto ^^^\n')

def scrape_pictures(thread):
        while True:
            url = 'http://img.prntscr.com/img?url=http://i.imgur.com/'
            #url = 'http://i.imgur.com/'
            length = random.choice((5, 6))
            if length == 5:
                url += ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(5))
            else:
                url += ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(3))
                url += ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(3))
            url += '.jpg'

            filename = url.rsplit('/', 1)[-1]
        
            h = httplib2.Http('.cache' + thread)
            response, content = h.request(url)
            out = open(filename, 'wb')
            out.write(content)
            out.close()

            file_size = os.path.getsize(filename)
            if file_size in NONE_WORKING:
                os.remove(filename)
            else:
                check_image(url, filename)
                os.remove(filename)

print('Welcome to imgur-qr-btc scraper!')
for thread in range(1, THREAD_AMOUNT + 1):
    thread = str(thread)
    try:
        _thread.start_new_thread(scrape_pictures, (thread,))
    except:
        print('Error starting thread ' + thread)
print('Succesfully started ' + thread + ' threads, enjoy!')

while True:
    pass