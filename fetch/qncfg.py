#-*- coding: utf-8 -*-
import sys
import os
import xlrd
from datetime import datetime

try_own_dir = os.path.dirname(os.path.realpath(__file__))

if (".exe" == try_own_dir[-4:]) :
    try_own_dir = os.path.dirname(try_own_dir)
try:
    own_dir = try_own_dir.decode("utf-8")
except:
    own_dir = try_own_dir.decode("gbk")

cookie_path      = own_dir + "/local/qn_cookie.txt"
icon_path      = own_dir + "/local/spider.ico"
fcfg_path        = own_dir + "/fetch.conf"
if "win" in sys.platform :
    tess_path        = own_dir + "/local/tesseract.exe"
else :
    tess_path        = own_dir + "/local/tesseract"
kpic_path        = own_dir + "/local/dl.jpg"
krec_path        = own_dir + "/local/qn_rec.txt"
kcfg_path        = own_dir + "/local/qn_kcfg.txt"
log_path         = own_dir + "/fetch.log"
dbg_dir          = own_dir + "/"
window_init_js   = own_dir +"/local/window_init.js"
input_data_path  = own_dir + "/flights.xlsx"
result_file_path = own_dir + "/result.xls"
result_files_path = own_dir + "/result_%s.xls"



if "win" in sys.platform :
    js_engine = "v8"
else:
    js_engine = "spidermonkey"

price_fast = False

# header_xff : Add a random X-Forwarded-For header
header_xff = False

#cookie_preserve: Try to use a same cookie(more like a browser's behaivor)
cookie_preserve = False

#logging: Write information to a log file
logging = True

#debug : Record retrived pages to *.txt
debug   = False

verbose = False
gui     = False

adsl_on = True
adsl_freq = 1
adsl_entryname = "ADSL"
adsl_username  = "0000"
adsl_passwd    = "0000"

retry_max = 3
booking_sleep = 2.0
htmReq_headers = {
"Accept" :
    "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8" ,
"Accept-Encoding" :
    "gzip,deflate,sdch",
"Accept-Language" :
    "zh-CN,zh;q=0.8,en;q=0.6",
"Cache-Control" :
    "max-age=0",
"Connection" :
    "keep-alive",
"User-Agent" :
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.101 Safari/537.36",
}

detect_url = "http://www.baidu.com"
