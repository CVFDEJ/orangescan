#!/usr/bin/python3
# -*- coding: utf-8 -*-

from flask import request
from flask import render_template
from app import app
from app import config
import os
import re
import psutil


@app.route('/')
def index():
    return render_template('index.html', title='首页')


@app.route('/about')
def about():
    return render_template('about.html', title='关于')


@app.route('/domain')
def domain():
    return render_template('domain.html', title='子域名查询', action='/domain/search', domain='请输入企业一级域名，如：site.com, 支持模糊搜索')


@app.route('/domain/search', methods=['POST', 'GET'])
@app.route('/search', methods=['POST', 'GET'])
def query_domain():
    q = request.args.get('q', '')
    qtype = 'domain'
    if search(q):
        domain, subdomains, code = search(q)
        return render_template('domain.html', subdomains=subdomains, title='查询结果 : %s' % domain,
                               action='/domain/search',
                               domain=domain, code=code)
    elif regExp(q, qtype):
        domain = q
        return render_template('domain.html', title='查询结果 : %s' % domain,
                               result='%s还未扫描, 当前cpu占用' % domain + str(psutil.cpu_percent()) + "%",
                               action='/domain/search',
                               domain=q, code='404')
    else:
        return render_template('domain.html', title='子域名查询',
                               action='/domain/search')


@app.route('/create/domain', methods=['POST', 'GET'])
def new_task():
    domain = request.args.get('q', '')
    if config.domain_db.exists(domain):
        return render_template('task.html', result='任务已完成,点击查看', domain=domain)
    elif regExp(domain, 'domain'):
        config.queue_db.set(domain, '0')
        config.log_db.set(domain, -1)
        os.system('python /usr/local/share/subDomains-Xscan/run.py %s&' % domain)
        return render_template('task.html', result='任务添加成功', domain=domain)
    else:
        return render_template('task.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


def search(q):
    domaindb = config.domain_db
    infodb = config.info_db
    logdb = config.log_db

    if logdb.keys('*%s*' % q):
        domain = str(logdb.keys('*%s*' % q)[0], 'utf-8')
        if infodb.exists(domain):
            subdomains = choosedb(infodb, domain)
            os.system('python /root/scan/info.py %s&' % domain)
            code = '200'
        else:
            subdomains = choosedb(domaindb, domain)
            os.system('python /root/scan/info.py %s&' % domain)
            code = '302'
        return domain, subdomains, code
    else:
        return False


def choosedb(db, q):
    subdomains = [str(i, 'utf-8') for i in db.smembers(q)]
    return subdomains


def regExp(q, qtype):
    if qtype == 'domain':
        return re.match(
            '(^(?=^.{3,255}$)[a-zA-Z0-9][-a-zA-Z0-9]{0,62}(\.(com\.cn|tw|com|cn|net|cc|me|jp){0,65})+$)',
            q) and re.match('^(?=^.{3,255}$)[a-zA-Z0-9][-a-zA-Z0-9]{0,62}(\.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})+$', q)
    else:
        return False


def getSubdomain():
    for task in config.queue_db.keys():
        if not config.log_db.exists(task):
            config.log_db.set(task, -1)
        elif config.log_db.get(task) == '-1':
            if int(os.popen('ps -h|grep subDomains-Xscan|wc -l').read()) < 6:
                os.system('python /usr/local/share/subDomains-Xscan/run.py %s&' % str(task, 'utf-8'))
            else:
                pass
        elif config.log_db.get(task) == '0':
            config.queue_db.delete(task)
        elif config.log_db.get(task) == '1':
            config.queue_db.delete(task)
        else:
            pass
