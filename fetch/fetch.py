#-*- coding: utf-8 -*-

import urllib2
import urllib
import cookielib
import zlib
import re
import datetime
import time
import random
import sys
import os
import xlwt

import qncfg
import util_js
import kaptcha
import cityCode
import util_common
from  util_common import log, log_to_file, parse_from_excel, parse_from_excel, query_data_list

#定义需要返回的字段名称
k_Departure_Airport='Departure_Airport'
k_Arrival_Airport='Arrival_Airport'
k_Cabin='Cabin'
k_Flight_No='Flight_No'
k_Departure_Date = 'Flight_Departure_Date'
k_Arrival_Date = 'Flight_Arrival_Date'
k_Departure_Time = 'Flight_Departure_Time'
k_Arrival_Time = 'Flight_Arrival_Time'
k_Price='Ticket_Price'
k_Rount_Type='Rount_Type'
k_Refresh_Time='Refresh_Time'
k_Is_Apply='Is_Apply'
k_Cabin_Count='Cabin_Count'
k_Product_Type = 'Product_Type'
k_Other_Info = 'Other_Info'
k_Domain='Domain'

k_Date='Date'
k_Carrier_Id='Carrier_Id'
k_Agent='Agent'
k_Agent_Name = 'Agent_Name'
k_Share='Share'
k_Apply='Apply'
k_Bonus_Type='Bonus_Type'

#航班相关字段
flight_info_lst = [k_Flight_No,
                   k_Departure_Airport, 
                   k_Arrival_Airport, 
                   k_Departure_Date, 
                   k_Arrival_Date, 
                   k_Departure_Time, 
                   k_Arrival_Time,
                   k_Domain]

#代理价格相关字段
agent_info_lst =  [k_Price, 
                   k_Cabin, 
                   k_Agent,
                   k_Agent_Name,
                   k_Rount_Type, 
                   k_Refresh_Time, 
                   k_Is_Apply, 
                   k_Cabin_Count, 
                   k_Product_Type, 
                   k_Other_Info ]

#所有字段
rt_lst = flight_info_lst + agent_info_lst

gui_update = False

#检测是否需要停止，gui程序中使用
def detect_stop():
    if qncfg.gui and util_common.thread_obj and  util_common.thread_obj.stop :
        raise ValueError("stop")

#抓取价格的主函数
#输入: 出发到达三字码和航班日期
def get_price(query_data):
    #Timer 
    tm_total = time.time()
    req_time = 0
    
    #产生CookieJar
    cj = cookielib.MozillaCookieJar(qncfg.cookie_path)
    cookie_hdl = urllib2.HTTPCookieProcessor(cj)
    qn_opener =  urllib2.build_opener(cookie_hdl)

    #三字码转城市名
    query_data["ArrivalCity"]    = cityCode.code_map.get( query_data["ArrivalAirport"])
    query_data["DepartureCity"] = cityCode.code_map.get( query_data["DepartureAirport"] )
    log ( "Fetch %s --> %s | %s " % (  query_data["DepartureAirport"],     
                                                          query_data["ArrivalAirport"],    
                                                          query_data["DepartureTime"]) )
    #如果配置为保持cookie则尝试读取本地存在的cookie文件
    if(qncfg.cookie_preserve and os.path.exists(qncfg.cookie_path)):
        cj.load()
    #构建请求参数
    req_params = {
    "searchDepartureAirport" : query_data["DepartureCity"].encode("utf-8") , 
    "searchArrivalAirport"    : query_data["ArrivalCity"].encode("utf-8"),
    "searchDepartureTime"      : query_data["DepartureTime"],
    "searchArrivalTime"         :  query_data["DepartureTime"],
    "nextNDays" : "0",
    "startSearch" : "true",
    "from" : "fi_dom_search",
    }
    flight_host ="flight.qunar.com"
    #构建请求地址
    req_url = "http://%s/site/oneway_list.htm?" % flight_host 
    req_url += urllib.urlencode(req_params)
    req = urllib2.Request(req_url,None,qncfg.htmReq_headers)
    #发出请求 
    timer_req = time.time()
    r1 = qn_opener.open(req,data=None,timeout=16)
    f1 = r1.read()
    r1.close()
    req_time +=( time.time() - timer_req  )
    
    #如果返回数据为压缩格式，进行解压缩
    if (r1.headers.has_key("Content-Encoding") ):
        html =zlib.decompress(f1, 16+zlib.MAX_WBITS)
    else:
        html = f1

    #从返回页面html中解析出 验证js地址，SERVER_TIME等数据
    js_url = re.findall(r'\"(http://flight\.qunar\.com/twell/searchrt_ui/js/\d+)"',html)[0]
    lwv_str =  re.findall(r"SERVER_TIME\s=\snew\sDate\(Date\.parse\('([\s\d\w:]+)'\)",html)[0]
    lwv_dt = datetime.datetime.strptime(lwv_str,"%B %d %Y %H:%M:%S")
    lwv  = "f" + str(int(time.mktime(lwv_dt.timetuple())*1000))

    #准备获取 验证js代码
    req_js = urllib2.Request(js_url,None,qncfg.htmReq_headers)
    req_js.add_header("Referer",req_url )
    
    timer_req = time.time()
    r_js= qn_opener.open(req_js,data=None,timeout=16)
    f_js = r_js.read()
    r_js.close()
    req_time +=( time.time() - timer_req  )

    #如果返回数据为压缩格式，进行解压缩
    if(r_js.headers.has_key("Content-Encoding") ):
        js_source =zlib.decompress(f_js, 16+zlib.MAX_WBITS)
    else:
        js_source = f_js

    #访问allocateCookie页面，更新cookie
    req2 = urllib2.Request("http://www.qunar.com/twell/cookie/allocateCookie.jsp",
                                    None,qncfg.htmReq_headers)
    req2.add_header("Referer",req_url )
    
    timer_req = time.time()
    r2 = qn_opener.open(req2,data=None,timeout=16)
    f2 = r2.read()
    r2.close()
    req_time +=( time.time() - timer_req  )


    #开始调用js引擎来运行获取的js代码，得到UADATA
    if len(js_source) < 6 :
        UADATA = ""
    else:
        UADATA  = util_js.runJS(js_source, cj)

    #准备访问longwell，获取航班基本信息和代理商列表等信息
    rand_str = "%.13f" % (random.random())
    req3_url ="""flight.qunar.com/twell/longwell?"""
    req3_params = {
    "http://www.travelco.com/searchArrivalAirport":query_data["ArrivalCity"].encode("utf-8") ,
    "http://www.travelco.com/searchDepartureAirport":query_data["DepartureCity"].encode("utf-8") ,
    "http://www.travelco.com/searchDepartureTime":query_data["DepartureTime"],
    "http://www.travelco.com/searchReturnTime":query_data["DepartureTime"],
    "locale":"zh",
    "nextNDays":"0",
    "searchLangs":"zh",
    "searchType":"OneWayFlight",
    "tags":"1",
    "mergeFlag":"0",
    "xd": lwv,
    "wyf": UADATA,
    "from" : "fi_dom_search",
    "_token" : rand_str[10:],}

    req3_url = "http://%s/twell/longwell?" % flight_host 
    req3_url += urllib.urlencode(req3_params)
    req3 = urllib2.Request(req3_url, None,qncfg.htmReq_headers)
    req3.add_header("Referer",req_url )
    timer_req = time.time()
    #发出longwell请求
    r3 = qn_opener.open(req3,data=None,timeout=16)
    f3 = r3.read()
    r3.close()
    req_time +=( time.time() - timer_req  )
    #如果返回数据为压缩格式，进行解压缩
    if(r3.headers.has_key("Content-Encoding")):
        html3 =zlib.decompress(f3, 16+zlib.MAX_WBITS)
    else:
        html3 = f3

    log_to_file(html3,"%s/data.txt"  % qncfg.dbg_dir)
    #如果遇到验证码，调用验证码模块
    if "isLimit" in html3:
        kaptcha.kaptcha_pass()
        raise ValueError("isLimit")
        return
    #从longwell返回的数据中解析出接下来一系列请求必需的参数
    html3_dict = util_js.dict_from_js(html3)
    queryID = html3_dict["queryID"]
    req4_serverIP = html3_dict["serverIP"]
    queryID_spl_idx =  queryID.index(":")
    queryID_base = queryID[:queryID_spl_idx+1]
    queryID_secret = queryID[queryID_spl_idx+1:]
    queryID_secret_list = list(queryID_secret)
    queryID_secret_list.reverse()
    req4_queryID = queryID_base + "".join([chr(ord(x)-1) for x in queryID_secret_list])




    #接下来的一系列请求的公共参数
    req4_params = {
        "arrivalCity":query_data["ArrivalCity"].encode("utf-8") ,
        "departureCity":query_data["DepartureCity"].encode("utf-8") ,
        "departureDate":query_data["DepartureTime"],
        "returnDate":query_data["DepartureTime"],
        "locale":"zh",
        "nextNDays":"0",
        "searchLangs":"zh",
        "searchType":"OneWayFlight",
        "from" : "fi_dom_search",
        "deduce" : "true",
        "serverIP" : req4_serverIP,
        "queryID" : req4_queryID,}

    #初始化变量
    fetch_cnt = 0
    flight_cnt = 0
    html4_dict ={}

    price_info = {}
    stage = "price"
    resultDic = {}
    returnDic = {}

    #开始主循环
    #包含两个阶段：price 和booking
    #price阶段通过数次请求不断更新航班信息和航班最低价，对应的是首页价格
    #booking阶段每个航班发一次请求获取所有代理商价格信息，对应的时点击预订按钮
    #price阶段完成后如果fetch_mode > 0则转入booking阶段，否则结束主循环
    while True:
        detect_stop()
        if stage == "price" :
            #产生price阶段的地址
            log ( "Get flight list(loop %d)" % ( fetch_cnt) )
            if fetch_cnt :
                req4_status  = str(html4_dict["status"])
                req4_url = "http://%s/twell/flight/tags/onewayflight_groupdata.jsp?" % flight_host 
            else:
                req4_status  = str(html3_dict["oneway_data"]["status"])
                req4_url = "http://%s/twell/flight/tags/deduceonewayflight_groupdata.jsp?" % flight_host 
                # req4_url = "http://%s/twell/flight/tags/OneWayFlight_data_more.jsp?" % flight_host 
        elif stage == "booking":
            #产生booking阶段的地址
            req4_url = "http://flight.qunar.com/twell/flight/tags/onewayflight_groupinfo.jsp?"
        if stage == "booking": 
            #在booking阶段每次从flightCode_lst中取出一个航班， 进行抓取
            if flightCode_lst :
                flightCode  = flightCode_lst.pop()
                log ( "[%3d/%3s] fetch price for  %s, [%4d]" % (fetch_cnt+1,totalFlightNum, 
                                                               flightCode.ljust(20),
                                                               resultDic[flightCode]["priceInfo"]["lowpr"]) )
            #如果flightCode_lst为空，说明所有航班抓取完毕，退出主循环
            else:
                break
            #booking阶段的请求需要一些特殊参数
            UADATA2 = util_js.runJS(js_source, cj)
            req4_params["flightCode"] = flightCode
            req4_params["label"] = "all"
            req4_params["wyf"] = UADATA2
            req4_params["d"] =  resultDic[flightCode]["priceInfo"]["d"]
            req4_params["k"] =  resultDic[flightCode]["priceInfo"]["k"]
        
        #准备发出请求
        rand_str = "%.13f" % (random.random())
        req4_params["status"] =  req4_status
        req4_params["_token"]  = rand_str[10:]
        req4_url += urllib.urlencode(req4_params)
        
        req4 = urllib2.Request(req4_url, None,qncfg.htmReq_headers)
        req4.add_header("Referer",req_url )
        timer_req = time.time()
        r4 = qn_opener.open(req4,data=None,timeout=16)
        #log("1-->%f" % (time.time()-timer_req) )
        timer_req4 = time.time()
        f4 = r4.read()
        #log("2-->%f" % (time.time()-timer_req) )
        r4.close()
        #log("3-->%f" % (time.time()-timer_req) )
        req_time +=( time.time() - timer_req  )
        req4_time =( time.time() - timer_req4  )
        #如果返回数据为压缩格式，进行解压缩
        if(r4.headers.has_key("Content-Encoding")):
            html4 =zlib.decompress(f4, 16+zlib.MAX_WBITS)
        else:
            html4 = f4
        #logging
        if(stage == "price"):
            log_to_file(html4,"%s/data_%s_%d.txt" % (  qncfg.dbg_dir, stage,  fetch_cnt )  )
        else:
            log_to_file(html4,"%s/data_%s%d_%d.txt" % ( qncfg.dbg_dir, stage, flight_cnt, fetch_cnt )  )

        #如果遇到验证码，调用验证码模块
        if "isLimit" in html4:
            kaptcha.kaptcha_pass()
            raise ValueError("isLimit")
            break
        html4_dict = util_js.dict_from_js(html4)
        if stage == "price" :
            #price阶段，每次请求之后更新航班信息
            updateFlight(query_data, html4_dict, resultDic)
            #判断price阶段是否结束
            dataCompleted = fetch_cnt != 0  and (html4_dict["dataCompleted"] or ( (not r4.headers.has_key("Content-Encoding") ) and qncfg.price_fast) )
            if  dataCompleted :
                #转入booking
                stage = "booking"
                fetch_cnt = 0
                #删除不需要的航班信息
                for x in resultDic.keys():
                    if resultDic[x].get("ignore") :
                        del resultDic[x]
                    else:
                        #del resultDic[x]["priceInfo"]
                        del resultDic[x]["flightInfo"]
                        #如果fetch_mode = 0直接处理k_Price
                        if qncfg.fetch_mode == 0 :
                            resultDic[x][k_Price] = resultDic[x]["priceInfo"]["lowpr"]
                            resultDic[x][k_Cabin] = resultDic[x]["priceInfo"]["cabin"]
                            resultDic[x][k_Refresh_Time] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())

                #准备构建flighCode_lst航班列表，供booking阶段使用
                flightCode_lst = []
                #按照航班最低价 从低到高排序
		for s in sorted(resultDic.items(), key=lambda d: int(d[1]["priceInfo"]["lowpr"]) ): 
                    if qncfg.fetch_mode == 0 :
                       log("%-20s, [%4d]" % ( s[0] , s[1]["priceInfo"]["lowpr"] ) )
                    flightCode_lst.insert(0,s[0])
                totalFlightNum = len(flightCode_lst )

                #如果只抓首页，退出主循环
                if qncfg.fetch_mode == 0 :
                    break
            else:
                fetch_cnt += 1
            #计算需要sleep的时间
            invokeInterval = html4_dict.get("invokeInterval")
            if invokeInterval :
                invokeInterval = float(invokeInterval ) / 1000.0
            else:
                invokeInterval = 2.0
            time.sleep(3 )
            #time.sleep( invokeInterval )
            #log (  "sleep %f s" % invokeInterval ) 
        elif stage == "booking" :
            #更新代理商价格信息
            updateBook(flightCode,html3_dict,  html4_dict, resultDic)

            #判断booking阶段是否结束
            if not flightCode_lst:
                #return wrap_result(resultDic, tm_total ,  req_time)
                break
            else:
                #没有结束，计算需要sleep的时间
                if fetch_cnt:
                    if req4_time < qncfg.booking_sleep :
                        time.sleep(qncfg.booking_sleep-req4_time)
                else:
                    time.sleep(2)
                flight_cnt += 1
                fetch_cnt += 1

        #保存本次cookie，或者删除cookie
        if( qncfg.cookie_preserve ):
            cj.save()
        elif os.path.exists(qncfg.cookie_path):
            try:
                os.remove(qncfg.cookie_path)
            except:
                pass

    #返回wrap之后的数据
    return wrap_result(resultDic, tm_total ,  req_time)

#更新航班信息，包括最低价
def updateFlight(query_data, html4_dict, resultDic):
    if html4_dict.has_key("flightInfo"):
                #更新航班基本信息
                for (n, v) in html4_dict["flightInfo"].items():
                    resultDic.setdefault(n,{})
                    #对于出发或到达机场和查询值不一致的航班，用ignore标识
                    if v['da'] != query_data["DepartureAirport"] or v['aa'] != query_data["ArrivalAirport"] :
                         resultDic[n]["ignore"] = True
                         continue
                    #获取航班基本信息
                    resultDic[n].setdefault("flightInfo", v)
                    resultDic[n][k_Flight_No] = n.split("|")[0]
                    resultDic[n][k_Departure_Airport]=v['da']
                    resultDic[n][k_Departure_Date]=v['dd']
                    resultDic[n][k_Departure_Time]=v['dt']
                    resultDic[n][k_Arrival_Airport]=v['aa']
                    resultDic[n][k_Arrival_Time]=v['at']
                    #返回数据中没有到达日期，通过出发日期，时间和到达时间来判断（假定航班时间小于24小时）
                    #resultDic[n][k_Arrival_Date]=v['ad']
                    d_datetime =  datetime.datetime.strptime("%s %s" % (v['dd'],v['dt'] ), "%Y-%m-%d %H:%M")
                    a_datetime =  datetime.datetime.strptime("%s %s" % (v['dd'],v['at'] ), "%Y-%m-%d %H:%M")
                    if a_datetime < d_datetime:
                        a_datetime   += datetime.timedelta(days=1)
                    resultDic[n][k_Arrival_Date]=a_datetime.strftime('%Y-%m-%d')
                    resultDic[n][k_Rount_Type]="S"
                    resultDic[n][k_Domain]="qunarweb"
    #更新航班最低价信息
    if html4_dict.has_key("priceInfo"):
                for (n, v) in html4_dict["priceInfo"].items():
                    resultDic.setdefault(n,{})
                    if resultDic[n].get("ignore"):
                        continue
                    #保留原来的最低价
                    p =  resultDic[n].get("priceInfo")
                    if p:
                         old_lowpr = p["lowpr"]
                    resultDic[n]["priceInfo"] = v
                    #如果本次最低价高于已有最低价，恢复已有最低价
                    #似乎更新值总比已有值要低，本逻辑弃用
                    #if p and resultDic[n]["priceInfo"]["lowpr"] > old_lowpr:
                    #    resultDic[n]["priceInfo"]["lowpr"] = old_lowpr

            
#更新代理商信息
def updateBook(flightCode ,  html3_dict,  html4_dict, resultDic):
            priceDic =  html4_dict["priceData"][flightCode]
            #调用parseAgentPrice计算非申请不含保险的最低价
            parseAgentPrice(flightCode,priceDic,resultDic, html3_dict)
            del resultDic[flightCode]["priceInfo"]
            
            vender_price = resultDic[flightCode][k_Price]
            vender_code = resultDic[flightCode][k_Agent]
            if (vender_code == "unKnown"):
                vender_name = "unKnown"
            else:
                vender_name =  html3_dict["vendors"][vender_code.split("_")[0]]["name"] 
            

#计算非申请不含保险的最低价
def parseAgentPrice(flightID,priceDic,resultDic,  html3_dict = {}) :

    #本航班的首页显示最低价
    lowPr = resultDic[flightID]['priceInfo']['lowpr']

    #初始化
    maxPrice = 10000
    minPr = maxPrice
    nonApplyMinBpr=maxPrice
    NonApplyLowPr = maxPrice
    lowAgent="unKnown"

    #遍历booking数据里的所有代理商价格（包括含保险，不含保险，申请，非申请等价格），获取最低价，从而求出首页价格和booking数据之间的价差
    for agentID,agentDic in priceDic.items():
        if agentDic["pr"] < 0 or agentDic["afee"] == 0 :
            agentDic["pr"] = agentDic["bpr"] 
        if  agentDic["pr"] < minPr:
            minPr = agentDic["pr"]
    if minPr == maxPrice:
        return
    elif minPr < 0 :
        return
    else:
        #价差
        prGap = lowPr - minPr

    #遍历booking数据，找出非申请的不含保险最低价
    for agentID,agentDic in priceDic.items():
        # type= tn 特惠：立减
        #ttsgnd01204 自由人
        #vt > 0 自由行
        #type = a 表明是申请票
        if agentDic["bpr"]>0 and agentDic["bpr"] < nonApplyMinBpr and agentDic["type"]!="a":
            nonApplyMinBpr=agentDic["bpr"]
            lowAgent=agentID
        #如果fetch_mode = 2 保存所有代理信息
        if qncfg.fetch_mode == 2:
            resultDic[flightID].setdefault("agentInfo",{})
            resultDic[flightID]["agentInfo"][agentID] = agentDic
    
    if nonApplyMinBpr==maxPrice:
        resultDic[flightID][k_Price]=maxPrice
        resultDic[flightID][k_Agent] = "unKnown"
        return

    #补偿上价差，得到实际价格
    NonApplyLowPr=nonApplyMinBpr+prGap
    #返回字段赋值
    resultDic[flightID][k_Price]=str(NonApplyLowPr)
    resultDic[flightID][k_Agent]=lowAgent
    resultDic[flightID][k_Agent_Name] =html3_dict["vendors"][lowAgent.split("_")[0]]["name"] 
    resultDic[flightID][k_Cabin] = priceDic[lowAgent]["cabin"]
    resultDic[flightID][k_Cabin_Count]  = None
    resultDic[flightID][k_Other_Info] = priceDic[lowAgent].get("tgq")
    agent_type  = priceDic[lowAgent].get("type")
    if  priceDic[lowAgent].get("fx"):
        resultDic[flightID][k_Product_Type]= "Cash_Back"
    elif  agent_type and agent_type[0] == "t" :
        resultDic[flightID][k_Product_Type]= "Li Jian"
    else:
        resultDic[flightID][k_Product_Type] = None
    resultDic[flightID][k_Is_Apply]='N'
    resultDic[flightID][k_Refresh_Time]=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
    if qncfg.fetch_mode == 2:
        #如果需要返回所有代理商信息，依次给每个代理商进行字段赋值
        for (agent_id, agent_info) in resultDic[flightID]["agentInfo"].items() :
            agent_info[k_Price]= agent_info["bpr"] + prGap
            agent_info[k_Agent]=lowAgent
            agent_info[k_Agent_Name] =html3_dict["vendors"][agent_id.split("_")[0]]["name"] 
            agent_info[k_Cabin] = agent_info["cabin"]
            agent_info[k_Cabin_Count]  = None
            agent_info[k_Other_Info] = agent_info.get("tgq")
            agent_type  = agent_info.get("type")
            if  agent_info.get("fx"):
                agent_info[k_Product_Type]= "Cash_Back"
            elif  agent_type and agent_type[0] == "t" :
                agent_info[k_Product_Type]= "Li Jian"
            else:
                agent_info[k_Product_Type]= None
            if agent_type == "a":
                agent_info[k_Is_Apply]='Y'
            else:
                agent_info[k_Is_Apply]='N'
            agent_info[k_Refresh_Time]=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
    return resultDic


#遍历query_data_list依次调用get_price获得价格信息 
def do_fetch(th_obj = None):
    #if util_common.detect_network() :
    #    log("Network not OK")
    #    if qncfg.gui:
    #        util_common.send_gui_cmd("fetch_finish")
    #    return
    if th_obj :
        util_common.thread_obj = th_obj
    #读取配置
    util_common.read_config()
    #读取输入excel
    parse_from_excel()
    if not query_data_list:
        log( "Query List is Empty" )
        return

    wb = xlwt.Workbook()

    ip_cnt=120
    query_cnt = 0
    retry_cnt = 0

    #主循环
    while(query_data_list and query_cnt < len(query_data_list) ) :
        #当前要抓的
        query_data  = query_data_list[query_cnt]

        #如果需要，增加一个随机的XFF Header
        #############Change IP :-) ############
        ip1 = int(random.random()*255.0)
        ip2 = int(random.random()*255.0*255.0)%255
        ip3 = int(random.random()*255.0*255.0*255.0)%255
        ip4 = int(random.random()*255.0*255.0*255.0*255.0) %255
        random_ip =  "%d.%d.%d.%d" % ( ip1,ip2,ip3,ip4)
        if qncfg.header_xff:
            log("random ip %s:" % random_ip)
            qncfg.htmReq_headers["X-ForWarded-For"] = random_ip
        #######################################

        log("Query[%3d/%3d]" % (query_cnt+1,len(query_data_list)))
        #如果需要，开始ADSL切换
        if qncfg.adsl_on and ( retry_cnt >0 or (query_cnt % qncfg.adsl_freq == 0) ):
            if util_common.adsl() :
                log("ADSL failed")
            else:
                log("ADSL success")
        if retry_cnt > 0:
            log("Retry [%2d /%2d]" % ( retry_cnt, qncfg.retry_max )  )
        try:
            detect_stop()
            res = get_price(query_data)
        #尝试捕获验证码Exception
        except ValueError, e:
            if e.message == "stop" and qncfg.gui:
                util_common.send_gui_cmd("fetch_finish")
                log("Thread is stop")
                return
            #如果出现验证码Exception , 重试
            elif e.message == "isLimit" and   retry_cnt < qncfg.retry_max :
                log("Meet verify code, wait to retry again..."  )
                time.sleep( 8 + retry_cnt )
                retry_cnt += 1
                #qncfg.cookie_preserve = False
                #qncfg.header_xff = True
                #qncfg.price_fast = False
                continue
            #超出重试最大次数或其他ValueError：抓下一次
            else:
                log("Get Unexpected ValueError: %s" % e )
                query_cnt += 1
                retry_cnt = 0
                #qncfg.cookie_preserve = False
                #qncfg.header_xff = True
                #qncfg.price_fast = False
                continue
        #出现未知异常，直接抓下一次
        except Exception, e:
            log("Get Unexpected Exception: %s" % e )
            res = None
            query_cnt += 1
            retry_cnt = 0
            #qncfg.cookie_preserve = True
            #qncfg.header_xff = False
            #qncfg.price_fast = True
            continue
        else:
            query_cnt += 1
            retry_cnt = 0
            #qncfg.cookie_preserve = True
            #qncfg.header_xff = False
            #qncfg.price_fast = True

        #写入Excel表格
        ws = wb.add_sheet('%s-%s-%s' % (query_data["DepartureAirport"],
                                        query_data["ArrivalAirport"],
                                        query_data["DepartureTime"]) )
        #Keys
        row_cnt = 0
        col_cnt = 0
        for c in  rt_lst :
            ws.write(row_cnt, col_cnt, c)
            col_cnt += 1
        row_cnt = 1
        col_cnt = 0
        if not res:
            continue
        if qncfg.fetch_mode == 2:
            for v in res["info"]["data"]:
                for (agent_id , agent_info) in sorted( v["agentInfo"].items(), key= lambda x:int(x[1][k_Price]) ):
                    col_cnt =0
                    for c in  flight_info_lst:
                        entry = v.get(c)
                        if not entry : entry  = ""
                        ws.write(row_cnt, col_cnt, entry)
                        col_cnt +=1
                    for c in  agent_info_lst:
                        entry = agent_info.get(c)
                        if not entry : entry  = ""
                        ws.write(row_cnt, col_cnt, entry)
                        col_cnt +=1
                    row_cnt +=1
        else:
            for v in res["info"]["data"]:
                col_cnt =0
                for c in  rt_lst:
                    if not v.get(c):
                        v[c] = ""
                    ws.write(row_cnt, col_cnt, v[c])
                    col_cnt +=1
                row_cnt +=1

        time.sleep(5)

    try:
        wb.save(qncfg.result_file_path)
    except Exception, e:
        log("Failed to write result to file : %s, reason: %s" % (qncfg.result_file_path, e) )
        log("Do you open the excel file? close it and run again" )
    else:
        log("Write result file to %s successfully." % (qncfg.result_file_path) )
    log("Fetch Complete!")
    if qncfg.gui:
        util_common.send_gui_cmd("fetch_finish")
    

def wrap_result(resultDic, tm_total ,  req_time):
    lst = sorted(resultDic.values(),key= lambda x: int(x[k_Price]))
    return  { "info" : {
                            "data" :lst ,  
                            "Total_Time" : time.time()-tm_total, 
                            "Network_Time" : req_time, 
                            "Excute_Result" : "SUCCESS"
                    }
                }
