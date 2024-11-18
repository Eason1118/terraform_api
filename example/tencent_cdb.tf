# TF官方参考文档：
# 创建数据库：https://registry.terraform.io/providers/tencentcloudstack/tencentcloud/latest/docs/resources/mysql_instance
# 创建数据库账号： https://registry.terraform.io/providers/tencentcloudstack/tencentcloud/latest/docs/resources/mysql_account
# 设置账号权限： https://registry.terraform.io/providers/tencentcloudstack/tencentcloud/latest/docs/resources/mysql_privilege
# 设置备份策略： https://registry.terraform.io/providers/tencentcloudstack/tencentcloud/latest/docs/resources/mysql_backup_policy

terraform {
  required_providers {
    tencentcloud = {
      source = "tencentcloudstack/tencentcloud"
      version = ">=1.81.20"
    }
  }
}

provider "tencentcloud" {
  region = "ap-singapore"
}


resource "tencentcloud_mysql_instance" "db" {
  # RO项目ID
  project_id        = 1111111
  # 是否允许从公网访问实例：0 - 否，1 - 是
  internet_service  = 1
  engine_version    = "5.7"
  # 预付费
  charge_type       = "PREPAID"
  # 实例周期
  prepaid_period    = 36
  # 自动续订
  auto_renew_flag   = 1
  # 参数必填
  root_password     = "Xq@vsdfsdf233423!@@#"
  # 可用区部署方法。可用值：0 - 单个可用区；1 - 多个可用区。
  slave_deploy_mode = 1
  availability_zone = "ap-singapore-4"
  # 从实例的可用区
  first_slave_zone  = "ap-singapore-2"
  # 数据复制模式。0 - 异步复制；1 - 半同步复制；2 - 强同步复制。
  slave_sync_mode   = 1               
  instance_name     = "{{ instance_name }}"
  cpu               = 4
  mem_size          = 8000
  volume_size       = 200
  vpc_id            = "vpc-xxxxxxxx"
  subnet_id         = "subnet-xxxxxxxx"
  intranet_port     = 3306
  security_groups   = ["sg-xxxxxxxx", "sg-xxxxxxxx"]

  tags = {
    "项目组" = "xxxxxxxx"
  }

  parameters = {
    character_set_server = "utf8mb4"
    max_connections      = "100000"
    time_zone            = "+07:00"
  }
}


# 创建数据库账号: exporter
resource "tencentcloud_mysql_account" "exporter" {
  mysql_id             = tencentcloud_mysql_instance.db.id
  name                 = "exporter"
  password             = "xxxxxxxx"
  description          = "monitor"
  max_user_connections = 10
}
# 创建数据库账号权限: exporter
resource "tencentcloud_mysql_privilege" "exporter" {
  mysql_id       = tencentcloud_mysql_instance.db.id
  account_name   = tencentcloud_mysql_account.exporter.name
  global     = ["PROCESS", "REPLICATION CLIENT", "LOCK TABLES", "SELECT", "SHOW DATABASES"]
}

# 创建数据库账号: sql_audit
resource "tencentcloud_mysql_account" "sql_audit" {
  mysql_id             = tencentcloud_mysql_instance.db.id
  name                 = "sql_audit"
  password             = "xxxxxxxx"
  description          = "sql_audit"
  max_user_connections = 10
  
}
# 创建数据库账号权限: sql_audit
resource "tencentcloud_mysql_privilege" "sql_audit" {
  mysql_id       = tencentcloud_mysql_instance.db.id
  account_name   = tencentcloud_mysql_account.sql_audit.name
  global     = ["PROCESS", "REPLICATION CLIENT", "LOCK TABLES", "SELECT", "SHOW DATABASES"]
}

# 创建数据库账号: origin_backup
resource "tencentcloud_mysql_account" "origin_backup" {
  mysql_id             = tencentcloud_mysql_instance.db.id
  name                 = "origin_backup"
  password             = "xxxxxxxx"
  description          = "origin_backup"
  max_user_connections = 10
  
}

# 创建数据库账号权限: origin_backup
resource "tencentcloud_mysql_privilege" "origin_backup" {
  mysql_id       = tencentcloud_mysql_instance.db.id
  account_name   = tencentcloud_mysql_account.origin_backup.name
  global     = ["PROCESS", "REPLICATION CLIENT", "LOCK TABLES", "SELECT", "SHOW DATABASES"]
}

# 创建数据库账号: admin
resource "tencentcloud_mysql_account" "admin" {
  mysql_id             = tencentcloud_mysql_instance.db.id
  name                 = "admin"
  password             = "xxxxxxxx"
  description          = "admin"
  max_user_connections = 10240
  
}

# 创建数据库账号权限: admin
resource "tencentcloud_mysql_privilege" "admin" {
  mysql_id       = tencentcloud_mysql_instance.db.id
  account_name   = tencentcloud_mysql_account.admin.name
  global     = ["ALTER", "ALTER ROUTINE", "CREATE", "CREATE ROUTINE", "CREATE TEMPORARY TABLES", "CREATE USER", "CREATE VIEW", "DELETE", "DROP", "EVENT", "EXECUTE", "INDEX", "INSERT", "LOCK TABLES", "PROCESS", "REFERENCES", "RELOAD", "REPLICATION CLIENT", "REPLICATION SLAVE", "SELECT", "SHOW DATABASES", "SHOW VIEW", "TRIGGER", "UPDATE"]
}

# 备份策略设置
resource "tencentcloud_mysql_backup_policy" "db_policy" {
  mysql_id              = tencentcloud_mysql_instance.db.id
  retention_period      = 15
  backup_model          = "physical"
}


# 获取内网IP变量
output "mysql_private_ip" {
  value       = tencentcloud_mysql_instance.db.intranet_ip
  description = "The created IPv4 mysql_private_ip"
}
# 获取内网端口变量
output "mysql_private_prot" {
  value       = tencentcloud_mysql_instance.db.intranet_port
  description = "The created IPv4 mysql_private_prot "
}

# 获取外网IP变量
output "mysql_public_ip" {
  value       = tencentcloud_mysql_instance.db.internet_host
  description = "The created mysql_public_ip "
}
# 获取外网端口变量
output "mysql_public_port" {
  value       = tencentcloud_mysql_instance.db.internet_port
  description = "The created mysql_public_port "
}
