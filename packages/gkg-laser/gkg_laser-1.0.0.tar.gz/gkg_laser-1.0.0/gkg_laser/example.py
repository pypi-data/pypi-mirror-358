# 配置日志
import logging

from gkg_laser.laser_command import LaserCommand
from gkg_laser.laser_controller import LaserController

logging.basicConfig(level=logging.INFO)

# 创建控制器
controller = LaserController("127.0.0.1", 7005)

try:
    # 建立连接
    controller.client.connect()

    # 案例1：初始化设备
    if controller.execute_command(LaserCommand.INITIALIZE, "M1_D_TG"):
        print("设置模板成功")

        # 打标
        result = controller.execute_command(LaserCommand.MARK_START)
        if result:
            print("打标成功")
        else:
            print("打标失败")
    else:
        print("设置模板失败")
finally:
    controller.client.close()