#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sys
import threading
import time
from multiprocessing.dummy import Pool

import lxml.html as H
import requests

import config

reload(sys)
sys.setdefaultencoding('utf8')
lock = threading.Lock()
threadpool = Pool(processes=100)
TIMEOUT = 3
scan_results = []


def signal_handler(signal, frame):
    threadpool.terminate()
    threadpool.done = True


def handle_result(host, port, result):
    tm = time.time()
    with lock:
        scan_results.append([host, port, result])


def scan_scan(*kw):
    if len(*kw) == 2:
        host, port = kw[0][0], int(kw[0][1])
    else:
        return
    result = None
    rcode, server, title = 0, "", ""
    target_url = "http://%s:%s" % (host, port)
    try:
        r = requests.get(target_url, timeout=TIMEOUT, allow_redirects=True)

        meta_reg = r"<meta.*?charset=['\"]?([^'\"><]*)?.*?>"
        if r.encoding == 'ISO-8859-1':
            m = re.search(meta_reg, r.text, re.I)
            if m:
                r.encoding = m.group(1)
            else:
                r.encoding = 'utf-8'
        try:
            doc = H.document_fromstring(r.text)
            tag_list = doc.xpath('//%s' % ('title'))

            if tag_list:
                title = tag_list[0].text

        except:
            title = "Null"

        if r.status_code:
            rcode = r.status_code
        if 'Server' in r.headers:
            server = r.headers['Server']

    except KeyboardInterrupt:
        pass

    except requests.exceptions.Timeout, e:
        pass

    except Exception, e:
        pass

    finally:
        result = [target_url, rcode, server, title]

    handle_result(host, port, result)
    return result


def scan_file_check(domains, result_file=None):
    port_list = [80]

    scan_list = []
    for subdomain in domaindb.smembers(domains):
        host = unicode(subdomain.strip(), 'utf-8')
        for port in port_list:
            scan_list.append([host, port])

    task = threadpool.map(scan_scan, scan_list)

    threadpool.close()
    threadpool.join()

    vul_results = []
    for x in scan_results:
        if x[2][1]:
            vul_results.append(x)

    if result_file:
        with open(result_file, 'w') as f:
            for x in vul_results:
                h, p, r = x
                rs = ""
                tu, rcode, server, title = r
                if title:
                    title = title.replace("\r\n", "").replace("\n", "").replace("\r", "").replace("\t", "").replace(":",
                                                                                                                    "")
                    title = title.encode('utf-8')
                if server:
                    server = server.replace(":", "/")

                rs = "%s\t%s\t%s\t%s" % (tu, rcode, server, title)
                domain = tu.replace("http://", "").replace(":80", "")
                try:
                    if len(server) == 0: server = "Null"
                    if len(title) == 0: title = "Null"
                except:
                    server = "Null"
                    title = "Null"
                result = "%s:%s:%s:%s" % (domain, server, rcode, title)
                infodb.sadd(domains, result)
                f.write("%s\n" % rs)


if __name__ == '__main__':
    domaindb = config.domain_db
    infodb = config.info_db
    logdb = config.log_db
    logdir = config.log_dir
    domains = sys.argv[1]
    output_file = "%s/%s.txt" % (sys.argv[1], logdir)
    scan_file_check(domains, output_file)
