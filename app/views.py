#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import re
import time

import psutil
from flask import render_template
from flask import request
from flask import jsonify
from flask import make_response
from flask import send_from_directory

from app import app
from app.config import domain_db, log_db, info_db, scan_py, info_py, redis_dir, queue_db, collection


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico')


@app.route('/')
def index_site():
    return render_template('index.html', title='首页')


@app.route('/domain')
def index_domain():
    return render_template('domain.html',
                           title='子域名查询',
                           action='/domain/search',
                           domain='请输入企业一级域名，如：site.com, 支持模糊搜索')


@app.route('/domain/search', methods=['POST', 'GET'])
@app.route('/search', methods=['POST', 'GET'])
def query_domain():
    q = request.args.get('q', '').lower()
    qtype = 'domain'
    if search(q):
        domain, subdomains, code = search(q)
        return render_template('domain.html',
                               subdomains=subdomains,
                               title='查询结果 : %s' % domain,
                               action='/domain/search',
                               domain=domain,
                               code=code)
    elif reg_exp(q, qtype):
        domain = q
        cpustatus = str(psutil.cpu_percent())
        return render_template('domain.html',
                               title='查询结果 : %s' % domain,
                               result='%s还未扫描, 当前cpu占用%s' % (domain, cpustatus),
                               action='/domain/search',
                               domain=domain, code='404')
    else:
        return render_template('domain.html',
                               title='子域名查询',
                               action='/domain/search')


@app.route('/create/domain', methods=['POST', 'GET'])
@app.route('/domain/create', methods=['POST', 'GET'])
def create_task():
    domain = request.args.get('q', '').lower()
    if log_db.exists(domain):
        return render_template('task.html',
                               result='任务已完成,点击查看',
                               domain=domain)
    elif reg_exp(domain, 'domain'):
        queue_db.set(domain, '0')
        log_db.set(domain, '-1')
        os.system('python %s %s&' % (scan_py, domain))
        return render_template('task.html',
                               result='任务添加成功',
                               domain=domain)
    else:
        return render_template('task.html')


@app.route('/bak')
def bak_rds():
    os.system('cp %s/dump.rdb %s/bak/dump.rdb%d' % (redis_dir, redis_dir, int(time.time())))
    return 'ok'


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# api

@app.route('/api/v1.0/domain/<string:domain_name>', methods=['GET'])
def api_get_domain(domain_name):
    subdomains = []
    if domain_db.exists(domain_name):
        for subdomain in domain_db.smembers(domain_name):
            subdomains.append(str(subdomain, 'utf-8'))
        result = [{
            'domain': domain_name,
            'status': int(log_db.get(domain_name)),
            'count': len(subdomains),
            'subdomains': subdomains,
        }]
        return make_response(jsonify({'result': result, 'reason': 'Success', 'error_code': 200}))
    else:
        return make_response(jsonify({'result': [], 'reason': 'Not found', 'error_code': 404}), 404)


@app.route('/api/v1.0/domain/<string:domain_name>', methods=['POST'])
def api_scan_domain(domain_name):
    if scan_task_domain(domain_name):
        result = [{
            'domain': domain_name,
            'status': int(log_db.get(domain_name)),
        }]
        return jsonify({'result': result, 'reason': 'Success', 'error_code': 200})
    else:
        return make_response(jsonify({'result': [], 'reason': 'Fail', 'error_code': 500}), 500)


@app.route('/api/v1.1/domain/<string:domain_name>', methods=['GET'])
def api_get_domain_v1_1(domain_name):
    """

    :param domain_name:
    :return: {'result': '', 'reason': '', 'error_code': ''}
    """

    subdomain_col = collection.subdomain
    try:
        result = subdomain_col.find({"domain": domain_name})
        if result:
            return jsonify({'result': result[0], 'reason': 'Success', 'error_code': 200})
        else:
            return make_response(jsonify({'result': [], 'reason': 'Not found', 'error_code': 404}), 404)
    except:
        return make_response(jsonify({'result': [], 'reason': 'Not found', 'error_code': 404}), 404)


def search(q):
    if log_db.keys('%s*' % q):
        domain = str(log_db.keys('%s*' % q)[0], 'utf-8')
        if info_db.exists(domain):
            subdomains = choose_db(info_db, domain)
            os.system('python3 %s %s&' % (info_py, domain))
            code = '200'
        else:
            subdomains = choose_db(domain_db, domain)
            os.system('python3 %s %s&' % (info_py, domain))
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
    for task in queue_db.keys():
        if not log_db.exists(task):
            log_db.set(task, -1)
        elif log_db.get(task) == '-1':
            if int(os.popen('ps -h|grep scan.py|wc -l').read()) < 60:
                os.system('python %s %s&' % (scan_py, str(task, 'utf-8')))
            else:
                pass
        elif log_db.get(task) == '0':
            queue_db.delete(task)
        elif log_db.get(task) == '1':
            queue_db.delete(task)
        else:
            pass


def scan_task_domain(domain):
    task_count = int(os.popen('ps -h|grep scan.py|wc -l').read())

    if reg_exp(domain, 'domain'):
        if log_db.exists(domain):
            return True
        elif task_count < 50:
            log_db.set(domain, -1)
            os.system('python %s %s&' % (scan_py, domain))
            return True
        else:
            return False
    else:
        return False


def task_queue():
    return None
