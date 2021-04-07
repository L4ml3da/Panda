# coding=utf-8
import datetime
import threading
import re
import json
import os
import Queue
import urllib2
import socket
from optparse import OptionParser
import xlwt
import xlrd
from xlutils.copy import copy

masscan_path = "masscan.exe"
final_domains = []
default_ports = "80,81,82,443,7001-7003,8000-8100,8181,8282,8383,8585,8686,8787,8888,8989"
default_speed = "10000"
default_thread = 10
default_timeout = 5
res = {}
tasks = Queue.Queue()
threads = []
url_q = Queue.Queue(100000)
web_q = Queue.Queue(100000)

def portscan(target, speed, ports):
    cmdline = masscan_path + ' ' + target + ' -p'+ports + ' -oJ masscan.json --rate ' + speed
    print "[+] masscan commandline:" + cmdline
    os.system(cmdline)
    with open('masscan.json', 'r') as f:
        for line in f:
            if line.startswith('{ '):
                temp = json.loads(line[:-2])
                temp1 = temp["ports"][0]
                ip = temp["ip"]
                if ip not in res:
                    res[ip] = []
                res[ip].append(str(temp1["port"]))
                #print "put " + "http://%s:%s" % (ip, str(temp1["port"]))
                url_q.put("http://%s:%s" % (ip, str(temp1["port"])))
                #print res[ip]
    #for k in res:
        #if len(res[k]) > 50 or len(res[k]) == 0:
            #del res[ip]
    return res

def get_code(header, html):
    try:
        m = re.search(r'<meta.*?charset\=(.*?)"(>| |\/)', html, flags=re.I)
        if m:
            return m.group(1).replace('"', '')
    except:
        pass
    try:
        if header.has_key('Content-Type'):
            Content_Type = header['Content-Type']
            m = re.search(r'.*?charset\=(.*?)(;|$)', Content_Type, flags=re.I)
            if m: return m.group(1)
    except:
        pass

def work_thread():
    url = ""
    while True:
        try:
            url = url_q.get(timeout=10)
            get_title(url)
        except:
            if url_q.empty():
                return
            else:
                continue

def get_title(url):
    try:
        info = urllib2.urlopen(url)
        html = info.read()
        header = info.headers
    except urllib2.HTTPError, e:
        header = e.headers
    except Exception, e:
        pass
        #print 'str(Exception):\t', str(Exception)
        #print 'str(e):\t\t', str(e)
    # if not header: return False, False
    try:
        html_code = get_code(header, html).strip()
        if html_code and len(html_code) < 12:
            html = html.decode(html_code).encode('utf-8')
    except:
        pass
    try:
        title = re.search(r'<title>(.*?)</title>', html, flags=re.I | re.M)
        if title: title_str = title.group(1)
        web_q.put((url, title_str.decode("utf-8")), timeout=10)
    except Exception, e:
        pass

def SaveResult(u, t):
    path = "./panda.xls"
    if os.path.exists(path):
        book = xlrd.open_workbook(path)
        origin = book.sheet_by_index(0)
        rows = origin.nrows
        wr = copy(book)
        xls_w =  wr.get_sheet(0)
        xls_w.write(rows, 0, u)
        xls_w.write(rows, 1, t)
        rows += 1
        wr.save(path)
    else:
        book = xlwt.Workbook()
        sheet = book.add_sheet('data', cell_overwrite_ok=False)
        sheet.write(0, 0, 'target')
        sheet.write(0, 1, 'title')
        sheet.write(1, 0, u)
        sheet.write(1, 1, t)
        book.save(path)


def GetCmdOpt():
    opt = OptionParser('Panda (Web sevice scanner) Version 1.0')
    opt.add_option('-n', '--hosts', dest = 'hosts', type = 'string', help = 'The hosts network, like 192.168.23.0/16')
    opt.add_option('-t', '--threads', dest = 'number', type = 'int', default = default_thread , help = 'Number of scan thread (default:10)')
    opt.add_option('-p', '--ports', dest = 'ports', type = 'string', default = default_ports, help = 'Web ports (default:80,81,82,443,7001-7003,8000-8100,8181,8282,8383,8585,8686,8787,8888,8989)')
    opt.add_option('-s', '--speed', dest = 'speed', type = 'string', default = default_speed, help = 'masscan speed(default:10000)')
    opt.add_option('-i', '--timeout', dest = 'timeout', type = 'int', default = default_timeout, help = 'http timeout(default:5)')
    option, args = opt.parse_args()
    return option

if __name__ == '__main__':
    print "    ____                  __     "
    print "   / __ \____ _____  ____/ /___ _"
    print "  / /_/ / __ `/ __ \/ __  / __ `/"
    print " / ____/ /_/ / / / / /_/ / /_/ /"
    print "/_/    \__,_/_/ /_/\__,_/\__,_/"

    print "                                    Web service scanner version 1.0\n"
    opt = GetCmdOpt()
    socket.setdefaulttimeout(opt.timeout)
    portscan(opt.hosts, opt.speed, opt.ports)
    for i in range(opt.number):
        threads.append(threading.Thread(target=work_thread))
    for t in threads:
        t.setDaemon(True)
        t.start()

    start_time = datetime.datetime.now()
    while True:
        try:
            u, t = web_q.get(timeout=2)
            print "[+] Found Web URL: " + u  + " title:" + t
            SaveResult(u, t)
        except Exception,e:
            #print 'main loop str(Exception):\t', str(Exception)
            #print 'main loop str(e):\t\t', str(e)
            if web_q.empty():
                all_finish = True
                for t in threads:
                    if t.is_alive():
                        all_finish = False
                        break
            else:
                continue
            if all_finish:
                print "[+] all thread exit"
                break
    end_time = datetime.datetime.now()
    print "[+] Spend time " + str(end_time-start_time)
