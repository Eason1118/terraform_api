#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2023/2/22 16:43
# @Author  : harilou
# @Describe:
from libs.parser import AttrDict, DateTimeEncoder
from libs.logger import logger
import json
import requests
import subprocess
from settings import CREATE, DELETE, BASE_DIR
import os
from datetime import datetime


def json_response(data='', error=''):
    content = AttrDict(data=data, error=error)
    if error:
        content.data = ''
    return json.dumps(content, cls=DateTimeEncoder)


def runcmd(command):
    logger.info(f"cmd:{command}")
    ret = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                        stdout=subprocess.PIPE, universal_newlines=True, shell=True, bufsize=1)
    line_list =list()
    # 实时输出
    while True:
        line = ret.stdout.readline()
        if line:
            logger.info(f"stdout:{line}")
            line_list.append(line)
        if subprocess.Popen.poll(ret) == 0:  # 判断子进程是否结束
            break
    output = "\n".join(line_list)
    if ret.returncode != 0:
        return ret.returncode, output
    return ret.returncode, output


def generate_tmp(data):
    """
    将数据进行渲染
    @param data: 需要渲染的数据
    @return: 渲染后的文本内容
    """
    from jinja2 import Template

    notify_tmp = """
{% for item in data %}
**实例ID:**:{{ item.ins_id }}
{% if item.hostname %}   
**主机名**:{{ item.hostname }} 
{% endif %}
{% endfor  %}
        """
    tm = Template(notify_tmp)
    msg = tm.render(data=data)
    # 去除空行
    msg_list = [i for i in msg.split("\n") if ":" in i or "*" in i]
    msg_text = "\n".join(msg_list)
    return msg_text


class CallBack(object):

    def __init__(self, url, action, status, data):
        self.url = url
        self.action = action
        self.status = status
        self.data = data

    def notify_to_fs(self):
        """
        向飞书推送消息
        """
        if self.status:
            title = f"👏 TF通知: {self.action}-成功 👏"
        else:
            title = f"👏 TF通知: {self.action}-失败 👏"
        ins_info = self.get_ins_info()
        content = generate_tmp(ins_info)
        data = {
            "msg_type": "interactive",
            "card": {
                "config": {
                    "wide_screen_mode": True
                },
                "elements": [{
                        "tag": "markdown",
                        "content": content
                    },
                ],
                "header": {
                    "template": "blue",
                    "title": {
                        "content": title,
                        "tag": "plain_text"
                    }
                }
            }
        }

        r = requests.post(self.url, data=json.dumps(data))
        if r.status_code != 200 or r.json().get("StatusCode") != 0:
            logger.error(f" send fail, error:{r.text}")
        else:
            logger.info(f" send text:{r.text}")
        return

    def get_ins_info(self):
        res = list()
        try:
            if isinstance(self.data["data"], list):
                for ins_id in self.data["data"]:
                    res.append({"ins_id": ins_id})
            else:
                for item in self.data["data"]["resources"][0]["instances"]:
                    info = item["attributes"]
                    res.append({"hostname": info["instance_name"], "ins_id": info["id"]})
        except:
            return self.data
        return res

    def run(self):
        if "//open.feishu.cn/" in self.url:
            self.notify_to_fs()
        else:
            r = requests.post(self.url, data=json.dumps(self.data))
            if r.status_code != 200:
                logger.error(f"CallBack send fail, error:{r.text}")
            else:
                logger.info(f"CallBack send text:{r.text}")
        return


def human_datetime(date=None):
    if date:
        assert isinstance(date, datetime)
    else:
        date = datetime.now()
    return date.strftime('%Y-%m-%d %H:%M:%S')


class JobData:

    def __init__(self, action=None, data=None):
        self.tf_data = data
        self.action = action
        self.json_file = os.path.join(BASE_DIR, "tmp", "job_data.json")

    def read(self):
        """
        将存储脚本的任务json文件进行读取
        :return: 文件转换出来的json数据
        """
        if os.path.exists(self.json_file):
            with open(self.json_file, 'r') as f:
                return json.load(f)
        return list()

    def save(self, data):
        with open(self.json_file, 'w') as f:
            f.write(json.dumps(data))
        return

    def run(self):
        read_data = self.read()
        if self.action == CREATE:
            try:
                for item in self.tf_data["data"]["resources"][0]["instances"]:
                    info = item["attributes"]
                    read_data.append({
                        "hostname": info["instance_name"],
                        "ins_id": info["id"],
                        "create_by": human_datetime()
                    })
            except:
                import traceback
                traceback.print_exc()
                pass
        elif self.action == DELETE:
            del_index = list()
            for ins_id in self.tf_data["data"]:
                for i, item in enumerate(read_data):
                    if item["ins_id"] == ins_id:
                        del_index.append(i)
            for index in del_index:
                read_data.remove(index)
        self.save(read_data)
        return
