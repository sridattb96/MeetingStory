import string
import re
datastring = "asdfi,,,,,adsf....asdfsda"
puc = re.compile(r'[,.?!]')
datastring = puc.sub(" ",datastring)
print datastring
