#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2023/2/24 17:40
# @Author  : harilou
# @Describe:
import traceback
import time
import os
import json
import shutil
import copy
from libs.logger import logger
from libs import CallBack, runcmd, Dict, JobData
from celery import Celery
from celery.exceptions import SoftTimeLimitExceeded
from jinja2 import Environment, FileSystemLoader
from settings import BASE_DIR, REDIS_HOST, REDIS_PORT, CREATE, UPDATE, DELETE


celery = Celery('terraform', broker=f'redis://{REDIS_HOST}:{REDIS_PORT}/0')


class TFHandler(object):

    def __init__(self, res_type, form, form_data):
        self.res_type = res_type
        self.form = Dict(form)
        self.form_data = Dict(form_data)
        self.tf_name = self.get_tf_name()

    def gen_tmp(self):
        """生成临时目录"""
        # 创建临时目录
        tmp_path = os.path.join(BASE_DIR, "tmp", self.form.csp, f"{self.res_type}{self.form.job_id}")
        if os.path.exists(tmp_path):
            shutil.rmtree(tmp_path)
        os.makedirs(tmp_path)
        return tmp_path

    def render(self, tmp_path):
        # 渲染模板
        file_loader = FileSystemLoader(f'template/{self.form.csp}')
        env = Environment(loader=file_loader)
        template = env.get_template(f"{self.res_type}.tf.j2")
        output = template.render(data=self.form_data)
        tmp_tf_file = self.get_tf_file_path(tmp_path)
        with open(tmp_tf_file, 'w', encoding='utf-8') as fp:
            fp.write(output)
        logger.info(f"tmp_tf_file:{tmp_tf_file} output:\n{output}")
        return
    
    def init_env(self, tmp_path):
        """初始化环境"""
        init_path = os.path.join("template", self.form.csp, "init")
        if os.path.exists(init_path):
            cmd = f"cp -rf {init_path}/*  {tmp_path}/"
            runcmd(cmd)
        return

    def gen_cmd(self, action):
        terraform_bin = f"terraform_{self.form.csp}"
        if action == DELETE:
            tf_cmd = f"{terraform_bin} init && yes yes | {terraform_bin} destroy"
        else:
            tf_cmd = f"{terraform_bin} init && yes yes | {terraform_bin} apply"
        return tf_cmd

    def gen_env(self):
        """生成环境变量"""
        export_env = ""
        if self.form.csp == "tencent":
            export_env = f"export TENCENTCLOUD_REGION={self.form_data.region}"
        elif self.form.csp == "cds":
            export_env = f"export CDS_REGION={self.form_data.region}"
        return export_env

    def exec(self, tmp_path, cmd):
        data, error = dict(), None
        status, res = runcmd(cmd)
        if status != 0:
            error = f"执行失败:{res}"
            logger.error(error)
            return data, error

        tf_ret_json_file = os.path.join(tmp_path, "terraform.tfstate")
        if os.path.exists(tf_ret_json_file):
            with open(tf_ret_json_file, "r") as f:
                data = json.load(f)
        else:
            error = f"not find file: {tf_ret_json_file}!"
        return data, error

    def backup(self, tmp_path, data):
        """备份执行后的结果"""
        ins_tfstate = copy.deepcopy(data)
        for item in data["resources"][0]["instances"]:
            logger.info(item)
            if "attributes" in item and "id" in item["attributes"]:
                ins_tfstate["resources"][0]["instances"] = [item]
                logger.info(f"ins_tfstate:{ins_tfstate}")
                ins_id = item["attributes"]["id"]
                if not ins_id:
                    continue
                ins_path = self.get_ins_tf_path(ins_id)
                logger.info(f" ins_id:{ins_path}")
                if os.path.exists(ins_path):
                    shutil.rmtree(ins_path)
                os.makedirs(ins_path)
                # 只拷贝.tf文件
                src_tf = os.path.join(tmp_path, self.tf_name)
                shutil.copy(src_tf, ins_path)
                # 以单个实例信息作为保存
                ins_tfstate_file = os.path.join(ins_path, "terraform.tfstate")
                with open(ins_tfstate_file, "w") as f:
                    f.write(json.dumps(ins_tfstate))
        return

    def get_ins_tf_path(self, ins_id):
        return os.path.join(BASE_DIR, "provider", self.form.csp, self.res_type, ins_id)
    
    def get_tf_name(self):
        return "terraform.tf"
    
    def get_tf_file_path(self, target_path):
        return os.path.join(target_path, self.tf_name)


class TerraForm(TFHandler):

    def __init__(self, res_type, action, forms, form_data):
        self.res_type = res_type
        self.action = action
        super(TerraForm, self).__init__(res_type, forms, form_data)

    def create(self):
        tmp_path = self.gen_tmp()
        self.init_env(tmp_path=tmp_path)
        self.render(tmp_path=tmp_path)
        export_env = self.gen_env()
        tf_cmd = self.gen_cmd(self.action)
        cmd = f"cd {tmp_path} && source ~/.bash_profile && {export_env} && {tf_cmd}"
        data, error = self.exec(tmp_path, cmd)
        if not data:
            error = "create fail, not resources!"
        if error is None and data.get("resources"):
            self.backup(tmp_path=tmp_path, data=data)
        return data, error

    def update(self):
        data, error = None, None
        ins_id = self.form_data.instance_id
        ins_tf_path = self.get_ins_tf_path(ins_id)
        if not os.path.exists(ins_tf_path):
            logger.error(f"没有找到这个实例路径:{ins_tf_path}")
            error = f"InsID:{ins_id} It was not created by TF and cannot be deleted by TF!"
            return data, error
        self.init_env(tmp_path=ins_tf_path)
        self.render(tmp_path=ins_tf_path)
        export_env = self.gen_env()
        tf_cmd = self.gen_cmd(self.action)
        cmd = f"cd {ins_tf_path} && source ~/.bash_profile && {export_env} && {tf_cmd}"
        data, error = self.exec(ins_tf_path, cmd)
        if not data:
            error = "upate fail, not resources!"
        return data, error

    def delete(self):
        data_list, error_list = list(), list()
        for ins_id in self.form_data["instance_ids"]:
            ins_tf_path = self.get_ins_tf_path(ins_id)
            if not os.path.exists(ins_tf_path):
                logger.error(f"没有找到这个实例路径:{ins_tf_path}")
                error_list.append(f"InsID:{ins_id} It was not created by TF and cannot be deleted by TF!")
                continue
            self.init_env(tmp_path=ins_tf_path)
            export_env = self.gen_env()
            tf_cmd = self.gen_cmd(self.action)
            cmd = f"cd {ins_tf_path} && source ~/.bash_profile && {export_env} && {tf_cmd}"
            data, error = self.exec(ins_tf_path, cmd)
            if error:
                error_list.append(error)
            else:
                data_list.append(ins_id)
                shutil.rmtree(ins_tf_path)
        return data_list, error_list

    def run(self):
        if self.action == CREATE:
            return self.create()
        if self.action == DELETE:
            return self.delete()
        if self.action == UPDATE:
            return self.update()


@celery.task(default_retry_delay=300, max_retries=1, soft_time_limit=1800)
def async_job_exec(res_type, action, forms, data):
    """
    异步任务处理
    Args:
        res_type: 资源类型
        action: 执行动作
        forms: 请求数据
        data: 源数据
    Returns: dict()
    """
    result = {
        "data": None,
        "error": None
    }
    start = time.time()
    try:
        job_id = forms.get("job_id")
        logger.info(f"==============【开始】异步执行任务;JOB ID:[{job_id}]=============== ")
        tf_api = TerraForm(res_type=res_type, action=action, forms=forms, form_data=data)
        result["data"], result["error"] = tf_api.run()
    except SoftTimeLimitExceeded as e:
        result["error"] = "执行任务超时"
        logger.error(traceback.format_exc())
        logger.error("==JOB ID:{}=异步执行任务超时：{}".format(job_id, e))
    except Exception as e:
        result["error"] = "job exec unexpected error "
        logger.error(traceback.format_exc())
        logger.error("==JOB ID:{}=异步执行任务失败：{}".format(job_id, e))
    logger.info(
        "==============【结束】异步执行任务;JOB ID:[{}]，耗时：{}============= ".format(job_id, round(time.time() - start), 2))
    status = True if not result["error"] else False
    logger.info(f"result:{result}")
    call_back = CallBack(url=forms.get("callback"), action=action, status=status, data=result)
    call_back.run()

    job_data = JobData(action=action, data=result)
    job_data.run()
    return result

