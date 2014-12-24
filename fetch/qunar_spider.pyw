#-*- coding: utf-8 -*-
#----------------------------------------------------------------------
# A very simple wxPython example.  Just a wx.Frame, wx.Panel,
# wx.StaticText, wx.Button, and a wx.BoxSizer, but it shows the basic
# structure of any wxPython application.
#----------------------------------------------------------------------

import wx
import threading
import PyV8
from wx.lib.pubsub import pub
import time

import fetch
import qncfg
from util_common import log


class LogDialog(wx.Dialog):
    def __init__(self, *args, **kwds):
        wx.Dialog.__init__(self, *args, **kwds)
        self.sizer_13_staticbox = wx.StaticBox(self, -1, _(u"登录"))
        self.sizer_10_staticbox = wx.StaticBox(self, -1, _(u"路径设置"))
        self.label_1 = wx.StaticText(self, -1, _(u"设置默认下载文件夹"))
        self.txtSetDownPath = wx.TextCtrl(self, -1, "")
        self.btnSetDownPath = wx.Button(self, -1, _("......"))
        self.label_2 = wx.StaticText(self, -1, _(u"设置打印文件夹      "))
        self.txtSetPrintPath = wx.TextCtrl(self, -1, "")
        self.btnSetPrintPath = wx.Button(self, -1, _("......"))
        self.btnSaveSet = wx.Button(self, -1, _(u"保存以上设置"))
        self.btnExitSet = wx.Button(self,wx.ID_CANCEL, _(u"退出设置    "))
        self.label_3 = wx.StaticText(self, -1, _(u"用户名"))
        self.txtUserid = wx.TextCtrl(self, -1, "")
        self.label_4 = wx.StaticText(self, -1, _(u"密码   "))
        self.txtUserpass = wx.TextCtrl(self, -1, "", style=wx.TE_PASSWORD)
        self.autoSaved = wx.CheckBox(self, -1, _(u"记住我，下次自动登录"))
        self.btnLogin = wx.Button(self, -1, _(u"登录"))
        self.btnExitLogin = wx.Button(self, wx.ID_CANCEL, _(u"退出"))

class MyThread(threading.Thread):
    def __init__(self,keyw=()):
        threading.Thread.__init__(self, name ="hw")
        self.stop = False
    def run(self):
        fetch.do_fetch(self)

class MyFrame(wx.Frame):
    """
    This is MyFrame.  It just shows a few controls on a wxPanel,
    and has a simple menu.
    """
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, -1, title,
                          pos=(150, 150), size=(500, 600))

        # Create the menubar
        menuBar = wx.MenuBar()

        # and a menu 
        menu = wx.Menu()
        ico = wx.Icon(qncfg.icon_path, wx.BITMAP_TYPE_ICO)

        self.SetIcon(ico)

        # add an item to the menu, using \tKeyName automatically
        # creates an accelerator, the third param is some help text
        # that will show up in the statusbar
        menu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Exit this program")

        # bind the menu event to an event handler
        self.Bind(wx.EVT_MENU, self.OnTimeToClose, id=wx.ID_EXIT)

        # and put the menu on the menubar
        menuBar.Append(menu, "&File")
        self.SetMenuBar(menuBar)

        self.CreateStatusBar()
        

        # Now create the Panel to put the other controls on.
        panel = wx.Panel(self)

        # and a few controls
        text = wx.StaticText(panel, -1, "Fetch qunar data")
        text.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
        text.SetSize(text.GetBestSize())
        self.funbtn = wx.Button(panel, -1, "Fetch")
        self.btn = wx.Button(panel, -1, "Close")
        self.log  = wx.TextCtrl(panel, -1, "" , size=(470, 360),  
                                       style= wx.TE_RICH | wx.TE_MULTILINE | wx.TE_READONLY)

        # bind the button events to handlers
        self.Bind(wx.EVT_BUTTON, self.OnTimeToClose, self.btn)
        self.Bind(wx.EVT_BUTTON, self.OnFunButton, self.funbtn)

        # Use a sizer to layout the controls, stacked vertically and with
        # a 10 pixel border around each
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(text, 0, wx.ALL, 10)
        sizer.Add(self.funbtn, 0, wx.ALL, 10)
        sizer.Add(self.btn, 0, wx.ALL, 10)
        sizer.Add(self.log, 0, wx.ALL, 10)
        panel.SetSizer(sizer)
        panel.Layout()
        self.SetMinSize((500,600))

        # And also use a sizer to manage the size of the panel such
        # that it fills the frame
        sizer = wx.BoxSizer()
        sizer.Add(panel, 1, wx.EXPAND)
        self.SetSizer(sizer)


        self.theThread = None
        pub.subscribe(self.updateDisplay, "update")  
        qncfg.gui = True
        

    def OnTimeToClose(self, evt):
        """Event handler for the button click."""
        #print "See ya later!"
        self.Close()

    def OnFunButton(self, evt):
        """Event handler for the button click."""
        #print "Having fun yet?"
        #self.funbtn.SetLabel("running...")
        if self.funbtn.GetLabel() == "Stop" :
            log("Wait thread stop")
            self.funbtn.SetLabel("Fetch")
            if self.theThread:
                if self.theThread.is_alive() :
                    self.funbtn.Disable()
                else:
                    self.funbtn.Enable()
            self.theThread.stop = True 
        else:
            if self.theThread  and self.theThread.is_alive() :
                log("A fetch thread is on-going !!")
                return
            else:
                self.funbtn.SetLabel("Stop")
                with PyV8.JSLocker():
                    self.theThread = MyThread()
                    self.theThread.setDaemon(True)
                    self.theThread.start()
        
    def updateDisplay(self, message):  
        if(message["type"] == "msg"):
            self.log.AppendText(message["data"])
        elif(message["type"] == "cmd"):
            if message["data"]  == "fetch_finish":
                self.funbtn.SetLabel("Fetch")
                self.funbtn.Enable()
                
class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None, "Fetch App")
        self.SetTopWindow(frame)
        frame.Show(True)
        return True
        
app = MyApp(redirect=False)
app.MainLoop()

