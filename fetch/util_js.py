import qncfg
import json
import cStringIO
import time
import threading


import cookielib

if qncfg.js_engine == "v8" :
    import PyV8
else:
    import spidermonkey
    ct = spidermonkey.Runtime().new_context()

def _load_js(fpath):
    fd=open(fpath)
    js = fd.read()
    fd.close()
    return js

def _gen_doc_cookie(cj):
    cookie_str = "; ".join(["%s=%s"%(c.name,c.value) for c in cj])
    #print cookie_str
    return "window.document.cookie='%s';" % cookie_str

def runJS(js_source, cj):
    js = _load_js(qncfg.window_init_js)
    js += _gen_doc_cookie(cj)
    js += js_source + ";"
    js += """
    //window.UA_obj.reloadUA(new Date());
    window.UA_obj.reloadUA();
    window.UA_obj.UADATA;
    """
    rt = ""
    if qncfg.js_engine == "v8" :
        with PyV8.JSContext() as ctxt :
            rt = ctxt.eval(js)
    else:
        rt = ct.execute(js)
    return rt

def dict_from_js(js):
    a = js.find("({")
    b = js.find("})")
    js = js[a+1:b+1]
    rt_dict = json.loads(js)
    return rt_dict

