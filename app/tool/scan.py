#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import Queue
import sys
import threading
import time

import dns.resolver

from app import config


class DNSBrute:
    def __init__(self, target, ignore_intranet, threads_num):
        self.target = target.strip()
        print self.target
        self.ignore_intranet = ignore_intranet
        self.thread_count = self.threads_num = threads_num
        self.scan_count = self.found_count = 0
        self.lock = threading.Lock()
        self.resolvers = [dns.resolver.Resolver() for _ in range(threads_num)]
        self._load_dns_servers()
        self._load_sub_names()
        self._load_next_sub()
        outfile = scan_dir + 'log/' + target + '.txt'
        self.outfile = open(outfile, 'w')  # won't close manually
        self.ip_dict = {}
        self.STOP_ME = False

    def _load_dns_servers(self):
        dns_servers = []
        with open(scan_dir + 'dict/dns_servers.txt') as f:
            for line in f:
                server = line.strip()
                if server.count('.') == 3 and server not in dns_servers:
                    dns_servers.append(server)
        self.dns_servers = dns_servers
        self.dns_count = len(dns_servers)

    def _load_sub_names(self):
        self.queue = Queue.Queue()
        file = scan_dir + 'dict/subnames_largest.txt'
        with open(file) as f:
            for line in f:
                sub = line.strip()
                if sub: self.queue.put(sub)

    def _load_next_sub(self):
        next_subs = []
        with open(scan_dir + 'dict/next_sub.txt') as f:
            for line in f:
                sub = line.strip()
                if sub and sub not in next_subs:
                    next_subs.append(sub)
        self.next_subs = next_subs

    def _update_scan_count(self):
        self.lock.acquire()
        self.scan_count += 1
        self.lock.release()

    @staticmethod
    def is_intranet(ip):
        ret = ip.split('.')
        if not len(ret) == 4:
            return True
        if ret[0] == '10':
            return True
        if ret[0] == '172' and 16 <= int(ret[1]) <= 32:
            return True
        if ret[0] == '192' and ret[1] == '168':
            return True
        return False

    def _scan(self):
        thread_id = int(threading.currentThread().getName())
        self.resolvers[thread_id].nameservers.insert(0, self.dns_servers[thread_id % self.dns_count])
        self.resolvers[thread_id].lifetime = self.resolvers[thread_id].timeout = 10.0
        while self.queue.qsize() > 0 and not self.STOP_ME and self.found_count < 4000:  # limit found count to 4000
            sub = self.queue.get(timeout=1.0)
            for _ in range(6):
                try:
                    cur_sub_domain = sub + '.' + self.target
                    answers = d.resolvers[thread_id].query(cur_sub_domain)
                    is_wildcard_record = False
                    if answers:
                        for answer in answers:
                            self.lock.acquire()
                            if answer.address not in self.ip_dict:
                                self.ip_dict[answer.address] = 1
                            else:
                                self.ip_dict[answer.address] += 1
                                if self.ip_dict[answer.address] > 2:  # a wildcard DNS record
                                    is_wildcard_record = True
                            self.lock.release()
                        if is_wildcard_record:
                            self._update_scan_count()

                            continue

                        if (not self.ignore_intranet) or (not DNSBrute.is_intranet(answers[0].address)):
                            self.lock.acquire()
                            self.found_count += 1
                            self.outfile.write(cur_sub_domain + '\n')
                            domain_db.sadd(self.target, cur_sub_domain)
                            log_db.set(self.target,0)
                            self.lock.release()
                            for i in self.next_subs:
                                self.queue.put(i + '.' + sub)
                        break
                except dns.resolver.NoNameservers, e:
                    break
                except Exception, e:
                    pass
            self._update_scan_count()

        self.lock.acquire()
        self.thread_count -= 1
        self.lock.release()

    def run(self):
        self.start_time = time.time()
        for i in range(self.threads_num):
            t = threading.Thread(target=self._scan, name=str(i))
            t.setDaemon(True)
            t.start()
        while self.thread_count > 1:
            try:
                time.sleep(1.0)
            except KeyboardInterrupt, e:
                self.STOP_ME = True


if __name__ == '__main__':
    scan_dir = config.scan_dir
    domain_db = config.domain_db
    log_db = config.log_db
    d = DNSBrute(target=sys.argv[1],
                 ignore_intranet=False,
                 threads_num=255,
                 )
    d.run()

