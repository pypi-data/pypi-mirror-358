from enum import Enum


class LaserCommand(Enum):
    """大族激光打标机通信指令枚举类

    包含客户端发送指令和服务端响应状态码
    """

    # 基础指令
    INITIALIZE = ("$Initialize_", "$Initialize_OK", "$Initialize_NG")
    DATA_UPDATE = ("$Data_", "$Data_OK", "$Data_NG")
    POSITION_UPDATE = ("$Move_", "$Move_OK", "$Move_NG")
    MARK_START = ("$MarkStart_", "$MarkStart_OK", "$MarkStart_NG")
    MARK_STOP = ("$MarkStop_", "$MarkStop_OK", "$MarkStop_NG")
    OPEN_MULTI = ("$OpenMul_", "$OpenMul_OK", "$OpenMul_NG")

    # 高级指令
    MARK_SELECTIVE = ("$MarkSel_", "$MarkSel_OK", "$MarkSel_NG")
    MARK_OBJECT = ("$MarkObj_", "$MarkObj_OK", "$MarkObj_NG")
    OPEN_PROJECT = ("$Project_", "$Project_OK", "$Project_NG")
    QUERY_STATUS = ("$SYS_Status", None, None)
    CLEAR_STATE = ("$Clear_", "$Clear_OK", "$Clear_NG")
    GET_PARAMETERS = ("$GetMarkParam_", None, None)

    def __init__(self, send_cmd: str, success_res: str, fail_res: str):
        """
        Args:
            send_cmd: 客户端发送指令
            success_res: 服务端成功响应
            fail_res: 服务端失败响应
        """
        self.send_cmd = send_cmd
        self.success_res = success_res
        self.fail_res = fail_res

    @property
    def send(self) -> str:
        """获取发送指令"""
        return self.send_cmd

    @property
    def success(self) -> str:
        """获取成功响应"""
        return self.success_res

    @property
    def fail(self) -> str:
        """获取失败响应"""
        return self.fail_res
