import socket
import logging
from typing import Optional


class DazuLaserMarkerClient:
    """大族激光打标机通信客户端

    通过TCP/IP协议与激光打标机服务端通信，支持指令发送、连接管理和异常处理

    Attributes:
        host (str): 打标机服务器IP地址
        port (int): 打标机服务端口（默认：5025）
        timeout (int): 连接超时时间（单位：秒）
        encoding (str): 指令编码格式（默认：utf-8）
        logger (logging.Logger): 日志记录器
        sock (socket.socket): Socket连接对象

    Example:
        >>> with DazuLaserMarkerClient('192.168.1.100') as client:
        ...     client.send_command('START_MARKING')
        ...     client.send_command('SET_POWER 80')
    """

    DEFAULT_PORT = 5025  # 假设大族默认端口，需根据实际情况调整
    DEFAULT_TIMEOUT = 5
    RETRY_ATTEMPTS = 3

    def __init__(self, host: str, port: int = DEFAULT_PORT,
                 timeout: int = DEFAULT_TIMEOUT, encoding: str = 'utf-8'):
        """初始化客户端

        Args:
            host: 打标机服务器IP地址
            port: 服务端口（默认：5025）
            timeout: 连接超时时间（默认：5秒）
            encoding: 指令编码格式（默认：utf-8）
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.encoding = encoding
        self.sock: Optional[socket.socket] = None
        self._setup_logger()

    def _setup_logger(self):
        """配置日志记录器"""
        self.logger = logging.getLogger('DazuLaserClient')
        self.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def connect(self) -> bool:
        """建立与打标机的连接

        Returns:
            bool: 是否成功建立连接
        """
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(self.timeout)
            self.sock.connect((self.host, self.port))
            self.logger.info(f"成功连接到 {self.host}:{self.port}")
            return True
        except Exception as e:
            self.logger.error(f"连接失败: {str(e)}")
            self.close()
            return False

    def send_command(self, command: str, wait_response: bool = False) -> Optional[str]:
        """发送指令到打标机

        Args:
            command: 要发送的指令字符串
            wait_response: 是否等待设备响应（默认：False）

        Returns:
            Optional[str]: 当wait_response=True时返回响应内容，否则返回None

        Raises:
            ConnectionError: 当连接不可用时抛出
            TimeoutError: 当操作超时时抛出
        """
        if not self._is_connected():
            self.logger.warning("连接不可用, 尝试重新连接...")
            if not self.connect():
                raise ConnectionError("无法建立有效连接")

        try:
            # 添加指令终止符（根据实际协议可能需要调整）
            full_command = command.strip() + '\r\n'
            self.sock.sendall(full_command.encode(self.encoding))
            self.logger.debug(f"已发送指令: {command}")

            if wait_response:
                return self._receive_response()
            return None

        except socket.timeout:
            self.logger.error("指令发送超时")
            raise TimeoutError("操作超时")
        except Exception as e:
            self.logger.error(f"指令发送失败: {str(e)}")
            self.close()
            raise

    def _receive_response(self) -> str:
        """接收设备响应

        Returns:
            str: 解码后的响应内容

        Raises:
            TimeoutError: 接收超时时抛出
        """
        try:
            response = self.sock.recv(1024)
            decoded = response.decode(self.encoding).strip()
            self.logger.debug(f"收到响应: {decoded}")
            return decoded
        except socket.timeout:
            self.logger.warning("等待响应超时")
            raise TimeoutError("响应接收超时")
        except Exception as e:
            self.logger.error(f"响应接收失败: {str(e)}")
            raise

    def _is_connected(self) -> bool:
        """检查当前连接状态

        Returns:
            bool: 是否处于连接状态
        """
        try:
            return self.sock is not None and self.sock.getpeername() is not None
        except (OSError, AttributeError):
            return False

    def close(self) -> None:
        """关闭连接"""
        if self.sock:
            try:
                self.sock.close()
                self.logger.info("连接已关闭")
            except Exception as e:
                self.logger.error(f"关闭连接时出错: {str(e)}")
            finally:
                self.sock = None

    def __enter__(self):
        """上下文管理入口"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理出口"""
        self.close()
