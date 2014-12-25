#-*- coding: utf-8 -*-
import xlrd
import xlwt
import time
import time
import subprocess
from   subprocess import Popen, PIPE
import ConfigParser
import os
import sys
import urllib2
import datetime

try:
    from wx.lib.pubsub import pub
    import wx
except:
    pass


import qncfg

query_data_list = []
thread_obj = None

def send_gui_cmd(cmd):
    if qncfg.gui:
        wx.CallAfter(pub.sendMessage, "update",  message = {
              "type" : "cmd", 
              "data" :  cmd} )  

def log(content):
    if  qncfg.logging :
        f = file(qncfg.log_path ,"a")
        stamp = time.strftime('%Y/%m/%d %H:%M:%S',time.localtime())
        f.write("[%s] %s" % (stamp, content.encode("utf-8") ) )
        f.write("\n")
        f.close()
    if qncfg.gui:
        wx.CallAfter(pub.sendMessage, "update",  message = {
              "type" : "msg", 
              "data" :  content + "\n"})  
    elif qncfg.verbose :
        print content

def log_to_file(content, fname):
    if not qncfg.debug :
        return
    a = file(fname,"w")
    a.write(content)
    a.close()


def clear_cfg(query_data_list):
    while(query_data_list):
        query_data_list.pop()

def parse_from_txt():
    clear_cfg(query_data_list)
    f = open(qncfg.fcfg_path, "r")
    for line in f.readlines():
        line = line.strip()
        if (not line )  or line[0] == "#" :
            continue
        try:
            parse_lst  = filter(lambda x:x,line.split(" "))
            if(len(parse_lst)  <3):
                log( "format error for this line in  cfg file:")
                log(  line)
        except Exception,  e:
            log( "Get Exception: %s "  % e )
            continue
        get = 0
        try:
            query_data = {
            "DepartureAirport"  : parse_lst[0].decode("utf-8"),
            "ArrivalAirport" :    parse_lst[1].decode("utf-8"),
            "DepartureTime" :     parse_lst[2], }
            query_data_list.append(query_data)
            get = 1
        except Exception, e:
            pass
        if(get):
            continue
        try:
            query_data = {
            "DepartureAirport"  : parse_lst[0].decode("gbk"),
            "ArrivalAirport" :    parse_lst[1].decode("gbk"),
            "DepartureTime" :     parse_lst[2], }
            query_data_list.append(query_data)
            get = 1
        except Exception, e:
            log( "Get Exception: %s "  % e )
            print "Coding error"
            continue
    f.close()

def parse_from_excel ():
    log( "This program will read data from %s. " % qncfg.input_data_path )
    clear_cfg(query_data_list)
    try:
        book = xlrd.open_workbook(qncfg.input_data_path)
    except Exception,e :
        log( "Cannot open excel file to proces, \ndetail: %s" % e )
        return
    for i in range(book.nsheets):
        sh = book.sheet_by_index(i)
        #print sh.name, sh.nrows, sh.ncols
        for j in range(sh.nrows):
            row_entry = sh.row(j)
            try:
                da = row_entry[0].value
                aa = row_entry[1].value
                if row_entry[2].ctype != 0 :
                    dt = "%04d-%02d-%02d" % xlrd.xldate_as_tuple( row_entry[2].value,0)[:3]
                else:
                    dt = str(row_entry[2].value)
                query_data = {"DepartureAirport"  : da, 
                                        "ArrivalAirport" :   aa, 
                                        "DepartureTime" :    dt}
                query_data_list.append(query_data)
            except Exception,  e:
                log("Parse error :", e )
                continue

def adsl():

    if "win" in sys.platform :
        adsl_conn_cmd = ["rasdial",qncfg.adsl_entryname,qncfg.adsl_username,qncfg.adsl_passwd]
        adsl_disc_cmd = ["rasdial","/DISCONNECT"]
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
    else:
        adsl_conn_cmd = ["pon", qncfg.adsl_entryname]
        adsl_disc_cmd = ["poff"]
        startupinfo = None
    ##Disconnect
    log("Begin to disconnect ADSL")
    retry_cnt = 0
    p_ras = Popen(adsl_disc_cmd, stdout=PIPE,stderr=PIPE,startupinfo=startupinfo )
    p_ras.wait()
    p_ras.stdout.read()
    p_ras.stderr.read()
    while(p_ras.returncode and retry_cnt <3) :
        log("ADSL disconnect Fail")
        retry_cnt += 1
        p_ras = Popen(adsl_disc_cmd, stdout=PIPE,stderr=PIPE ,startupinfo=startupinfo)
        p_ras.wait()
        p_ras.stdout.read()
        p_ras.stderr.read()
    if p_ras.returncode:
        return 1
    time.sleep(3)
    log("Begin to reconnect ADSL")
    ##Reconnect
    retry_cnt = 0
    p_ras = Popen(adsl_conn_cmd, stdout=PIPE ,stderr=PIPE,startupinfo=startupinfo, shell=False)
    p_ras.wait()
    p_ras.stdout.read()
    p_ras.stderr.read()
    while(p_ras.returncode and retry_cnt <3) :
        log("ADSL connect Fail")
        if p_ras.returncode == 623 :
            log("cannot find specified ADSL entryname in system! ")
            return 2
        retry_cnt += 1
        p_ras = Popen(adsl_conn_cmd, stdout=PIPE ,stderr = PIPE,startupinfo=startupinfo, shell=False)
        p_ras.wait()
        p_ras.stdout.read()
        p_ras.stderr.read()
    if p_ras.returncode:
        return 2
    else:
        return 0

def read_config():
    if not     os.path.exists(qncfg.fcfg_path) :
        return 1
    config = ConfigParser.SafeConfigParser()
    try:
        config.read(qncfg.fcfg_path)
        qncfg.fetch_mode = int(config.get('fetch', 'fetch_mode'))
        qncfg.adsl_on         = int(config.get('adsl', 'adsl_on')) > 0 
        qncfg.adsl_freq       = int(config.get('adsl', 'adsl_freq'))
        if qncfg.adsl_freq < 1:
            qncfg.adsl_freq  = 1
        qncfg.adsl_entryname = config.get('adsl', 'adsl_entryname').strip()
        qncfg.adsl_username = config.get('adsl', 'adsl_username').strip()
        qncfg.adsl_passwd = config.get('adsl', 'adsl_passwd').strip()
    except Exception, e:
        log("read configuration from %s failed: %s" % (qncfg.fcfg_path, e) )
        qncfg.fetch_mode = 1
        qncfg.adsl_on = False
    else:
        log("Read configuration from %s successfully:" % qncfg.fcfg_path)
        log("fetch_mod:%d" % qncfg.fetch_mode)
        log("adsl_on  :%d" % qncfg.adsl_on)
        if qncfg.adsl_on :
            log("adsl_entryname : %s" % qncfg.adsl_entryname )
            log("adsl_freq : %d" % qncfg.adsl_freq )
            log("adsl_username  : %s" % qncfg.adsl_username )
            log("adsl_passwd    : %s" % ("*"*len(qncfg.adsl_passwd)) )
def detect_network():
    try:
        r1 = urllib2.urlopen(qncfg.access_control,timeout=6)
        f1 = r1.read()
        r1.close()
        if "access" in f1:
            return 0
        else:
            return 1
    except Exception, e:
        if datetime.datetime.now() < datetime.datetime.strptime("2014-12-21","%Y-%m-%d") : 
            return 0
        else:
            return 1
if __name__ == "__main__":
    qncfg.verbose = True
    read_config()
    parse_from_excel()
    detect_network()
    adsl()
