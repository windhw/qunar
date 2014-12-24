#-*- coding: utf-8 -*-
import tornado.ioloop
import tornado.web
import tornado.gen
import time
import fetch
import json
import os,sys
from tornado.escape import json_encode



class MainHandler(tornado.web.RequestHandler):
    def get(self):
        query_data={}
        try:
            query_data["DepartureAirport"]  =self.get_argument('Departure_Airport')
            query_data["ArrivalAirport"] = self.get_argument('Arrival_Airport')
            query_data["DepartureTime"] = self.get_argument('Flight_Date')
            query_data["Domain"] = self.get_argument('Domain')
        except:
            self.write("""<h3>Query Format Not Valid</h3></br>
                          Example: <a href="/qunarweb?Domain=qunarweb&Departure_Airport=NAY&Arrival_Airport=PVG&Flight_Date=2014-12-09">NAY->PVG</a>
""" )
            self.finish()
            return
        try:
            rt = fetch.get_price(query_data)
        except Exception, e:
            rt = { "info"   :  {  "data" : [],
                                  "Excute_Result" : "FAILED" ,
                                  "Reason" : "%s" % e } }
        #t2 = yield tornado.gen.Task(tornado.ioloop.IOLoop.instance().add_timeout, time.time() + t)
        self.write(json.dumps(rt,  indent=4, separators=(',', ':') , ensure_ascii=False).encode("utf-8") )
        self.finish()
    #def get_price(self):
 
if __name__ == '__main__':

    try:
        if os.fork() > 0:
            os._exit(0) # exit father
    except OSError, error:
        print 'fork #1 failed: %d (%s) '%  (error.errno, error.strerror)
        os._exit(1)
    #signal.signal(signal.SIGCHLD, signal.SIG_IGN)
    os.chdir("/")
    os.setsid()
    os.umask(0)

    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

    si = file("/dev/null", 'r')
    so = file("/tmp/tmp_1234.log", 'a+', 0)
    #se = file("/tmp/tmp_1234.log", 'a+', 0)
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(so.fileno(), sys.stderr.fileno())

    #log_name = "smth.log"
    #p = Process(target = write_result , args=(log_name,result_q))
    #p.daemon = True
    #p.start()
    #signal.signal(signal.SIGCHLD, signal.SIG_IGN)

    #log_name = "smth.log"
    #p = Process(target = write_result , args=(log_name,result_q))
    #p.daemon = True
    #p.start()

    application = tornado.web.Application([ (r"/qunarweb/?", MainHandler), ])
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
