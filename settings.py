#!/usr/bin/env python3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

LOG_FILE = os.path.join(BASE_DIR, "log", "terraform_api.log")
LOG_LEVEL = "INFO"

# redis 配置
REDIS_HOST = "0.0.0.0"
REDIS_PORT = 6379

# 认证Token
TOKEN_LIST = ["xxxxxxxxxxxxxxxxxxxxxxxxx"]

# cvm网络计费类型
INTERNET_CHARGE_TYPE_LIST = ["BANDWIDTH_PREPAID", "TRAFFIC_POSTPAID_BY_HOUR", "BANDWIDTH_POSTPAID_BY_HOUR",
                             "BANDWIDTH_PACKAGE"]
# cvm实例计费类型
INSTANCE_CHARGE_TYPE_LIST = ["PREPAID", "POSTPAID_BY_HOUR", "SPOTPAID"]
# 云厂商
TENCENT = "tencent"
CDS = "cds"
CSP_LIST = [TENCENT, CDS]

# 创建
CREATE = "create"
UPDATE = "update"
STOP = "stop"
DELETE = "delete"

# 资源类型
VM = "vm"

# 资源类型
TARGET_LIST = [VM]
# 实例状态映射
INS_STATUS_MAP = {
    TENCENT: {
        "runing": "RUNNING",
        "stop": "STOPPED"
    },
    CDS: {
        "runing": "run",
        "stop": "stop"
    }
}


