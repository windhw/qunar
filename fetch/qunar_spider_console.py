#-*- coding: utf-8 -*-
#----------------------------------------------------------------------
# A very simple wxPython example.  Just a wx.Frame, wx.Panel,
# wx.StaticText, wx.Button, and a wx.BoxSizer, but it shows the basic
# structure of any wxPython application.
#----------------------------------------------------------------------
import fetch
import qncfg
if __name__ == "__main__" :
    qncfg.verbose = True
    while True:
        fetch.do_fetch()
        print u"R+Return"
        a = raw_input()
        try:
            if a.lower() == "r" :
                continue   
            else:
                print "EXIT!"
                break
        except Exception,  e :
            print e
            break
