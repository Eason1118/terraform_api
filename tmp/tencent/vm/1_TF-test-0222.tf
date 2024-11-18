
resource "tencentcloud_instance" "tf_vm" {
        # 实例名称
        instance_name = "TF-test-0222"
        # 可用区
        availability_zone = "ap-shanghai-5"
        # 镜像id
        image_id = "img-57j4snjh"
        # 实例类型
        instance_type = "S5.MEDIUM2"
        # 磁盘类型
        system_disk_type = "CLOUD_PREMIUM"
        
        # 安全组
        security_groups = ["sg-5aw0ubdu"]
        

        # VPC ID 参考：腾讯云-上海私有网络
        vpc_id = "vpc-4d8eaoy0"
        # 子网ID
        subnet_id = "subnet-53rip33v"
        # 自动分配外网IP
        allocate_public_ip = true
        # 网络计费类型
        internet_charge_type = "TRAFFIC_POSTPAID_BY_HOUR"
        # 最大带宽输出
        internet_max_bandwidth_out = 50
        # 数量
        count = 1
    }