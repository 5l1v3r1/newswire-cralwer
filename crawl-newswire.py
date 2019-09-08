#!/usr/bin/python3
import json, mmap, smtplib, re
from hashlib import sha512
from requests import get as rget
from email.mime.text import MIMEText as mtext

def no_hash(rhash, rfile):
    rhash = sha512(str(rhash).encode('utf-8')).hexdigest()
    
    try:
        f = open(rfile, 'rb', 0)
        m = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        nohash = True if m.find(rhash.encode()) == -1 else False
    except (ValueError, FileNotFoundError):
        nohash = True
        
    if nohash:
        with open(rfile, 'a') as f:
            f.write(rhash + '\n')
    
    return nohash

data = rget('https://www.rockstargames.com/newswire/tags.json?tags=702')
page = data.json()
regx = re.compile('GTA\$[1-10]')

mail_list = [ 'email@email.com' ]

for post in page['posts']:
    blurb = post['blurb']
    title = post['title']
    hash_file = '/home/admin/bin/blurb_hashes.txt'
    
    if (regx.search(blurb) or regx.search(title)) and no_hash(title, hash_file):
        msg = mtext(blurb, 'html')
        msg['Subject'] = re.sub('<[^<]+?>', '', post['title'])
        msg['From'] = 'email@email.com'
        
        for to_email in mail_list:
            msg['To'] = to_email
            mailer = smtplib.SMTP('localhost')
            mailer.sendmail('email@email.com', to_email, msg.as_string())
            mailer.quit()
