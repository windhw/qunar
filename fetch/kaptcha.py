#-*- coding: utf-8 -*-
import urllib2
import urllib
import os
import sys
import cookielib
import time
import subprocess
from   subprocess import Popen, PIPE
try:
    import Image
except:
    from PIL import Image 

import qncfg
from util_common import log

qncfg.verbose = True
class MyRedirectHandler(urllib2.HTTPRedirectHandler):
    def http_error_301(self, req, fp, code, msg, headers):
        pass
    def http_error_302(self, req, fp, code, msg, headers):
        pass
def kaptcha_pass():
    log(u"开始调用tesseract识别验证码")
    cj = cookielib.MozillaCookieJar(qncfg.cookie_path)
    cookie_hdl = urllib2.HTTPCookieProcessor(cj)
    qn_opener =  urllib2.build_opener(MyRedirectHandler, cookie_hdl)

    if "win" in sys.platform :
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
    else:
        startupinfo = None

    code_success = False
    for try_cnt in range(10):
        r1 = qn_opener.open("http://flight.qunar.com/twell/flight/busy.jsp",data=None,timeout=8)
        f1 = r1.read()
        r1.close()

        r2 = qn_opener.open("http://flight.qunar.com/twell/flight/search/imgi/kaptcha.jpg", data=None, timeout=8)
        f2 = r2.read()
        r2.close()

        fd = open(qncfg.kpic_path, "wb")
        fd.write(f2)
        fd.close()

        ima = Image.open(qncfg.kpic_path)
        size = ima.size
        imb = Image.new('RGB', size)
        a=ima.load()
        b=imb.load()
        for i in range(size[0]):
            for j in range(size[1]):
                if  i<10 or i >size[0] -10 or j < 10 or j > size[1]-10 or  sum(a[i, j]) / 3 > 100  :
                    b[i, j] = (255, 255, 255)
                else:
                    b[i, j] = (0, 0, 0)
        imb.save(qncfg.kpic_path)
        p_tess = Popen([qncfg.tess_path,
                        qncfg.kpic_path,
                        qncfg.krec_path.split(".")[0],
                        "-l", "eng", "-psm", "7",  
                        qncfg.kcfg_path], stdout=PIPE,stderr=PIPE ,startupinfo=startupinfo )
        p_tess.wait()
        p_tess.stdout.read()
        p_tess.stderr.read()
        p_tess.returncode

        fd = open(qncfg.krec_path)
        result = fd.read()
        fd.close()

        code = result.strip()
        if len(code) < 5:
            code = "00000"
        else:
            code = code[:5]
        log(code)
        #captcha=99999
        try:
            r3 = qn_opener.open("http://flight.qunar.com/twell/flight/busy.jsp", data=urllib.urlencode({"captcha":code}), timeout=8)
        except urllib2.URLError as e:
            if hasattr(e, 'code'):
                if e.code == 302 :
                    code_pass = True
                    break
        log("Wait to start again")
        time.sleep(1)
    if code_pass:
        log(u"正确完成验证码识别，使用%d次" % (try_cnt + 1) )
        return True
    else:
        log(u"验证码识别失败（达到了10次）" )
        return False

if __name__ == "__main__":
    qncfg.verbose = True
    kaptcha_pass()
