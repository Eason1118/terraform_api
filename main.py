#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2023/2/22 16:43
# @Author  : harilou
# @Describe:
from flask import Flask, abort
from flask import request
from libs import json_response, JsonParser, Argument, JobData
from settings import TOKEN_LIST, INTERNET_CHARGE_TYPE_LIST, CSP_LIST, VM, CREATE, DELETE, \
    INSTANCE_CHARGE_TYPE_LIST, UPDATE
from libs.logger import logger
from worker import async_job_exec
import json

app = Flask(__name__)
app.config["SECRET_KEY"] = "D7XepGC0Xhy02djanqZ3R7K0NuLyNC2McGxkcZQg"


@app.before_request
def init_request():
    ip = request.remote_addr
    logger.info("The IP of requestment is %s", ip)
    headers = request.headers
    req_json = request.json
    if headers.get("token"):
        token = headers.get("token")
    elif req_json.get("token"):
        token = req_json.get("token")
        req_data = req_json
    else:
        token = request.args.get("token")
        req_data = request.args
    logger.info("request data %s", req_data)
    if token not in TOKEN_LIST:
        logger.error("The IP %s don't have the permission to access the service", ip)
        abort(403)
    return


@app.after_request
def after_request(response):
    return response


@app.route('/terraform/vm', methods=['GET', 'POST', 'PUT', 'DELETE'])
def recovery_job():
    logger.info(f"requests:{request.json}")
    if request.method == "GET":
        job_data = JobData()
        data = job_data.read()
        return json_response(data=data)

    if request.method == "POST":
        form, error = JsonParser(
            Argument('job_id', handler=str.strip, help='缺少Job ID'),
            Argument('data', type=dict, help='缺少data'),
            Argument('csp', filter=lambda x: x in CSP_LIST, help='厂商类型错误'),
            Argument('callback', required=False),
        ).parse(request.json)
        if error:
            return json_response(error=error)
        form_data, from_error = JsonParser(
            Argument('region', handler=str.strip, help='地区参数错误'),
            Argument('instance_name', handler=str.strip, help='缺少实例名称'),
            Argument('instance_type', help='机型错误'),
            Argument('cpu', type=int, required=False, help='CPU'),
            Argument('memory', type=int, required=False, help='内存'),
            Argument('availability_zone', handler=str.strip, help='缺少可用区'),
            Argument('system_disk_size', type=int, help='缺少系统磁盘大小'),
            Argument('system_disk_type', handler=str.strip, help='缺少系统磁盘类型'),
            Argument('vpc_id', handler=str.strip, help='缺少私有网络ID'),
            Argument('subnet_id', help='缺少子网ID'),
            Argument('internet_max_bandwidth_out', type=int, required=False, help='缺少带宽限制数量'),
            Argument('instance_charge_type', filter=lambda x: x in INSTANCE_CHARGE_TYPE_LIST, required=False,
                     help='实例计费类型'),
            Argument('internet_charge_type', filter=lambda x: x in INTERNET_CHARGE_TYPE_LIST, required=False,
                     help='网络计费类型'),
            Argument('count', type=int, help='缺少实例数量'),
            Argument('image_id', handler=str.strip, help='缺少镜像模板ID'),
            Argument('status', required=False, handler=str.strip, help='实例状态'),
            Argument('security_groups', type=list, filter=lambda x: len(x), required=False),
            Argument('tags', type=dict, required=False),
            Argument('image_passwd', required=False),
            Argument('public_key', required=False),
            Argument('password', required=False),
        ).parse(request.json.get("data"))
        if from_error is None:
            form_data.security_groups = json.dumps(form_data.security_groups) if form_data.security_groups else None
            async_job_exec.apply_async(args=(VM, CREATE, form, form_data,))
            return json_response(data="创建VM任务下发成功!")
        return json_response(error=from_error)

    if request.method == "PUT":
        form, error = JsonParser(
            Argument('job_id', handler=str.strip, help='缺少Job ID'),
            Argument('data', type=dict, help='缺少data'),
            Argument('csp', filter=lambda x: x in CSP_LIST, help='厂商类型错误'),
            Argument('callback', required=False),
        ).parse(request.json)
        if error:
            return json_response(error=error)
        form_data, from_error = JsonParser(
            Argument('instance_id', handler=str.strip, help='实例ID错误'),
            Argument('region', handler=str.strip, help='地区参数错误'),
            Argument('instance_name', handler=str.strip, help='缺少实例名称'),
            Argument('instance_type', help='机型错误'),
            Argument('cpu', type=int, required=False, help='CPU'),
            Argument('memory', type=int, required=False, help='内存'),
            Argument('availability_zone', handler=str.strip, help='缺少可用区'),
            Argument('system_disk_size', type=int, help='缺少系统磁盘大小'),
            Argument('system_disk_type', handler=str.strip, help='缺少系统磁盘类型'),
            Argument('vpc_id', handler=str.strip, help='缺少私有网络ID'),
            Argument('subnet_id', help='缺少子网ID'),
            Argument('internet_max_bandwidth_out', type=int, required=False, help='缺少带宽限制数量'),
            Argument('instance_charge_type', filter=lambda x: x in INSTANCE_CHARGE_TYPE_LIST, required=False,
                     help='实例计费类型'),
            Argument('internet_charge_type', filter=lambda x: x in INTERNET_CHARGE_TYPE_LIST, required=False,
                     help='网络计费类型'),
            Argument('count', type=int, help='缺少实例数量'),
            Argument('image_id', handler=str.strip, help='缺少镜像模板ID'),
            Argument('status', required=False, handler=str.strip, help='实例状态'),
            Argument('security_groups', type=list, filter=lambda x: len(x), required=False),
            Argument('tags', type=dict, required=False),
            Argument('image_passwd', required=False),
            Argument('public_key', required=False),
            Argument('password', required=False),
        ).parse(request.json.get("data"))
        if from_error is None:
            form_data.security_groups = json.dumps(form_data.security_groups) if form_data.security_groups else None
            async_job_exec.apply_async(args=(VM, UPDATE, form, form_data,))
            return json_response(data="更新VM任务下发成功!")
        return json_response(error=from_error)

    if request.method == "DELETE":
        form, error = JsonParser(
            Argument('job_id', handler=str.strip, help='缺少Job ID'),
            Argument('data', type=dict, help='缺少data'),
            Argument('csp', filter=lambda x: x in CSP_LIST, help='厂商类型错误'),
            Argument('callback', required=False),
        ).parse(request.json)
        if error:
            return json_response(error=error)
        form_data, from_error = JsonParser(
            Argument('region', handler=str.strip, help='地区参数错误'),
            Argument('instance_ids', type=list, filter=lambda x: len(x), help='实例ID参数错误'),
        ).parse(request.json.get("data"))
        if from_error is None:
            async_job_exec.apply_async(args=(VM, DELETE, form, form_data,))
            return json_response(data="删除VM任务下发成功!")
        return json_response(error=from_error)


if __name__ == "__main__":
    app.run()
