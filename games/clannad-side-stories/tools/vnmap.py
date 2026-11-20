import unicodedata
BASE='aăâeêioôơuưy'
TONES=['','́','̀','̉','̃','̣']
def letters():
    lo=[]
    for b in BASE:
        for t in TONES:
            ch=unicodedata.normalize('NFC',b+t)
            if ch not in 'aeiouy': lo.append(ch)
    lo.append('đ')
    up=[c.upper() for c in lo]
    return lo,up
