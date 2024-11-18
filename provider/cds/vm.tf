
resource "cds_instance" "cds_vm" {
  # 实例名称
  instance_name = "{{ data.instance_name }}"
  # 地区
  region_id     = "{{ data.region }}"
  # 镜像ID
  image_id      = "{{ data.image_id }}"
  # 实例类型
  instance_type = "{{ data.instance_type }}"
  # 私有网络
  vdc_id        = "{{ data.vpc_id }}"
  # 镜像密码
  image_password = "Huanle.2022"
  # 预期状态
  operate_instance_status = "{{ data.status|default('run') }}"
  # 子网ID
  private_ip {
    private_id="{{ data.subnet_id }}"
    address= "auto"
  }

  system_disk = {
    type = "{{ data.system_disk_type }}"
    size = {{ data.system_disk_size }}
    iops = 0
  }

}