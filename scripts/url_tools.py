#!/usr/bin/env python2
# -*- coding: utf-8 -*-

######################################################
#
# Utility functions 
#
# Author: Aniket Adnaik (aniket.adnaik@huawei.com)
######################################################
#!/usr/bin/env python
import os
import requests
import urllib
from urlparse import urlparse
from urlparse import urljoin

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

def path2url(path):
    return urljoin('file:', urllib.pathname2url(path))

def validate_url(url):
    try:
         res = urlparse(url)
         return all([res.scheme, res.netloc, res.path])
    except:
         return False

def download_image(url, target_path):
    if (validate_url(url)):
        if (os.path.exists(target_path)):
            print('Image {} already exists. Overwriting...'.format(target_path))
        urllib.urlretrieve(url, target_path)         
        return True
    else:
        print('Invalid url ...')
        return False
