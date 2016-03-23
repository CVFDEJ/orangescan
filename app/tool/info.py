#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import os
import sys
import threading
from multiprocessing.dummy import Pool
import lxml.html as H
import requests
import config


def handle_result(host, port, result):
    with lock:
        scan_results.append([host, port, result])


def scan_scan(*kw):
    if len(*kw) == 2:
        host, port = kw[0][0], int(kw[0][1])
    else:
        return
    result = None
    httpcode, server, title = 0, "", ""
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
            title = ""

        if r.status_code:
            httpcode = r.status_code
        if 'Server' in r.headers:
            server = r.headers['Server']

    except KeyboardInterrupt:
        pass

    except requests.exceptions.Timeout:
        pass

    except:
        pass

    finally:
        result = [target_url, httpcode, server, title]

    handle_result(host, port, result)
    return result


def scan_file_check(domain):
    port_list = [80]
    scan_list = []
    for subdomains in domain_db.smembers(domain):
        host = str(subdomains.strip(), 'utf-8')
        for port in port_list:
            scan_list.append([host, port])

    task = threadpool.map(scan_scan, scan_list)

    threadpool.close()
    threadpool.join()

    vul_results = []
    for x in scan_results:
        if x[2][1]:
            vul_results.append(x)

    for x in vul_results:
        h, p, r = x
        tu, httpcode, server, title = r
        if title:
            title = title.replace("\r\n", "") \
                .replace("\n", "") \
                .replace("\r", "") \
                .replace("\t", "") \
                .replace(":", "")
        if server:
            server = server.replace(":", "/")
        target = tu.replace("http://", "").replace(":80", "")
        if server is None:
            server = ""
        if title is None:
            title = ""
        result = "%s:%s:%s:%s" % (target, server, httpcode, title)
        info_db.sadd(domain, result)
        log_db.set(domain, 1)


if __name__ == '__main__':
    lock = threading.Lock()
    threadpool = Pool(processes=100)
    TIMEOUT = 3
    scan_results = []

    domain_db = config.domain_db
    info_db = config.info_db
    log_db = config.log_db

    domain = sys.argv[1]
    scan_file_check(domain)
