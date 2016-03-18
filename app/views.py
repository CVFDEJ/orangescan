#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import re
import time

import psutil
from flask import render_template
from flask import request
from flask import send_from_directory

from app import app
from app import config


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico')


@app.route('/')
def index_site():
    return render_template('index.html', title='首页')


@app.route('/domain')
def index_domain():
    return render_template('domain.html', title='子域名查询', action='/domain/search', domain='请输入企业一级域名，如：site.com, 支持模糊搜索')


@app.route('/domain/search', methods=['POST', 'GET'])
@app.route('/search', methods=['POST', 'GET'])
def query_domain():
    q = request.args.get('q', '').lower()
    qtype = 'domain'
    if search(q):
        domain, subdomains, code = search(q)
        return render_template('domain.html', subdomains=subdomains, title='查询结果 : %s' % domain,
                               action='/domain/search',
                               domain=domain, code=code)
    elif reg_exp(q, qtype):
        domain = q
        return render_template('domain.html', title='查询结果 : %s' % domain,
                               result='%s还未扫描, 当前cpu占用' % domain + str(psutil.cpu_percent()) + "%",
                               action='/domain/search',
                               domain=q, code='404')
    else:
        return render_template('domain.html', title='子域名查询',
                               action='/domain/search')


@app.route('/create/domain', methods=['POST', 'GET'])
def create_task():
    domain = request.args.get('q', '').lower()
    if config.domain_db.exists(domain):
        return render_template('task.html', result='任务已完成,点击查看', domain=domain)
    elif reg_exp(domain, 'domain'):
        config.queue_db.set(domain, '0')
        config.log_db.set(domain, -1)
        os.system('python %s %s&' % (config.scan_py, domain))
        return render_template('task.html', result='任务添加成功', domain=domain)
    else:
        return render_template('task.html')


@app.route('/bak')
def bak_rds():
    os.system('cp %s/dump.rdb %s/bak/dump.rdb%d' % (config.redis_dir, config.redis_dir, int(time.time())))
    return 'ok'


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


def search(q):
    domain_db = config.domain_db
    info_db = config.info_db
    log_db = config.log_db

    if log_db.keys('*%s*' % q):
        domain = str(log_db.keys('*%s*' % q)[0], 'utf-8')
        if info_db.exists(domain):
            subdomains = choose_db(info_db, domain)
            os.system('python %s %s&' % (config.info_py, domain))
            code = '200'
        else:
            subdomains = choose_db(domain_db, domain)
            os.system('python %s %s&' % (config.info_py, domain))
            code = '302'
        return domain, subdomains, code
    else:
        return False


def choose_db(db, q):
    subdomains = [str(i, 'utf-8') for i in db.smembers(q)]
    return subdomains


def reg_exp(q, qtype):
    if qtype == 'domain':
        return re.match(
            '(^(?=^.{3,255}$)[a-z0-9][-a-z0-9]{0,62}(\.(com\.cn|tw|com|cn|net|cc|me|jp){0,65})+$)',
            q) and re.match('^(?=^.{3,255}$)[a-z0-9][-a-zA-Z0-9]{0,62}(\.[a-z0-9][-a-z0-9]{0,62})+$', q)
    else:
        return False


def get_subdomain():
    for task in config.queue_db.keys():
        if not config.log_db.exists(task):
            config.log_db.set(task, -1)
        elif config.log_db.get(task) == '-1':
            if int(os.popen('ps -h|grep scan.py|wc -l').read()) < 6:
                os.system('python %s %s&' % (config.scan_py, str(task, 'utf-8')))
            else:
                pass
        elif config.log_db.get(task) == '0':
            config.queue_db.delete(task)
        elif config.log_db.get(task) == '1':
            config.queue_db.delete(task)
        else:
            pass
