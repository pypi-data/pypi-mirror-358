import logging

from gkg_laser.laser_client import DazuLaserMarkerClient
from gkg_laser.laser_command import LaserCommand


class LaserController:
    """激光打标机控制封装类"""

    def __init__(self, host: str, port: int):
        self.client = DazuLaserMarkerClient(host, port)
        self.logger = logging.getLogger("LaserController")

    def execute_command(self, command: LaserCommand, payload: str = "", wait_response=True) -> bool:
        """执行激光控制指令

        Args:
            command: 枚举指令类型
            payload: 附加参数（例如："power=80,x=100,y=200"）

        Returns:
            bool: 是否执行成功
        """
        try:
            # 构造完整指令
            full_command = f"{command.send}{payload}"

            # 发送指令并等待响应
            response = self.client.send_command(full_command, wait_response=wait_response)
            if wait_response:
                if response == command.success_res:
                    self.logger.info("执行 %s 命令成功, 返回数据是: %s", full_command, response)
                    return True
                self.logger.warning("执行 %s 命令失败, 返回数据是: %s", full_command, response)
                return False
            self.logger.info("不判断返回结果, 执行 %s 命令成功, 返回数据是: %s", full_command, response)
            return True
        except ConnectionError:
            self.logger.error("激光打印设备未打开服务端.")
            return False
        except Exception as e:
            self.logger.error("执行 %s 发生异常: %s", command.name, str(e))
            return False
