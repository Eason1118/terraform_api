# TF官方参考文档：
# 创建服务器：https://registry.terraform.io/providers/tencentcloudstack/tencentcloud/latest/docs/resources/instance
# 创建EIP：https://registry.terraform.io/providers/tencentcloudstack/tencentcloud/latest/docs/resources/eip
# 绑定EIP：https://registry.terraform.io/providers/tencentcloudstack/tencentcloud/latest/docs/resources/eip_association


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


# 创建弹性EIP并绑定实例
resource "tencentcloud_eip" "ipv4_address" {
    name                       = "{{ instance_name }}"
    internet_max_bandwidth_out = 2000
    bandwidth_package_id = "bwp-xxxxxx"
    internet_charge_type = "BANDWIDTH_PACKAGE"
    type                 = "EIP"
}
resource "tencentcloud_eip_association" "ipv4_address_association" {
  eip_id      = tencentcloud_eip.ipv4_address.id
  instance_id = tencentcloud_instance.vm.0.id
}

resource "tencentcloud_instance" "vm" {
        # RO项目ID
        project_id        = 11111
        # 实例名称
        instance_name = "{{ instance_name }}"
        # 主机名
        hostname      = "{{ instance_name }}"
        # 可用区
        availability_zone = "ap-singapore-3"
        # 镜像id
        image_id = "img-xxxxx"
        # 实例机型；正式游戏服：S5.16XLARGE256
        instance_type = "S5.16XLARGE256"
        # 实例计费类型
        instance_charge_type = "PREPAID"
        # 包年包月:租期(时间单位为月)
        instance_charge_type_prepaid_period     = 1
        # 包年包月:自动续订标志; 这里默认到期通知并续订
        instance_charge_type_prepaid_renew_flag = "NOTIFY_AND_AUTO_RENEW"
        # 磁盘类型
        system_disk_type = "CLOUD_PREMIUM"
        # 磁盘大小
        system_disk_size = 1024
        # 安全组
        orderly_security_groups = ["sg-xx", "sg-xx"]
        # VPC ID
        vpc_id = "vpc-xxx"
        # 私有子网ID
        subnet_id = "subnet-xxx"
        # 标签
        tags = {
            "项目组" = "xxx"
        }
        # 数量
        count = 1
    }


output "ipv4_private_ip" {
  value       = tencentcloud_instance.vm.0.private_ip
  description = "The created IPv4 private_ip address"
}

output "ipv4_public_ip" {
  value       = tencentcloud_eip.ipv4_address.public_ip
  description = "The created IPv4 public_ip address"
}

output "vm_instance_id" {
  value       = tencentcloud_instance.vm.0.id
  description = "The created VM instance id"
}
