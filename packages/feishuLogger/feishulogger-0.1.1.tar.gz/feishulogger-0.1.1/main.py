import logging
import json
import requests
from datetime import datetime
import os
from logging.handlers import RotatingFileHandler


class FeishuLogger:
    """飞书日志通知器类"""

    # 定义自定义日志级别 ORDER
    ORDER_LEVEL = 55  # 介于 INFO(20) 和 WARNING(30) 之间

    def __init__(
        self,
        webhook_url,
        min_level=logging.ERROR,
        logger_name="FeishuAlertLogger",
        enable_file_log=False,
        log_file_path=None,
        max_file_size=10 * 1024 * 1024,  # 10MB
        backup_count=5,
    ):
        """
        初始化飞书日志器

        Args:
            webhook_url (str): 飞书机器人Webhook URL
            min_level (int): 最小日志级别，默认为ERROR
            logger_name (str): Logger名称
            enable_file_log (bool): 是否启用文件日志，默认False
            log_file_path (str): 日志文件路径，默认为None（自动生成）
            max_file_size (int): 单个日志文件最大大小（字节），默认10MB
            backup_count (int): 日志文件备份数量，默认5个
        """
        self.webhook_url = webhook_url
        self.min_level = min_level
        self.logger_name = logger_name
        self.enable_file_log = enable_file_log
        self.log_file_path = log_file_path or self._get_default_log_path()
        self.max_file_size = max_file_size
        self.backup_count = backup_count

        # 添加自定义日志级别
        logging.addLevelName(self.ORDER_LEVEL, "ORDER")

        # 初始化Logger
        self.logger = self._setup_logger()

        # 为Logger添加order方法
        self._add_order_method()

    def _get_default_log_path(self):
        """生成默认日志文件路径"""
        log_dir = "/home/hongmin/coding/testpylogger/logs"
        os.makedirs(log_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d")
        return os.path.join(log_dir, f"feishu_logger_{timestamp}.log")

    def _add_order_method(self):
        """为Logger添加order方法"""

        def order(message, *args, **kwargs):
            if self.logger.isEnabledFor(self.ORDER_LEVEL):
                self.logger._log(self.ORDER_LEVEL, message, args, **kwargs)

        # 绑定方法到logger实例
        self.logger.order = order

    def _setup_logger(self):
        """配置Logger"""
        logger = logging.getLogger(self.logger_name)
        logger.setLevel(self.min_level)

        # 避免重复添加handler
        if not logger.handlers:
            # 控制台Handler
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

            # 文件Handler (可选)
            if self.enable_file_log:
                # 确保日志目录存在
                log_dir = os.path.dirname(self.log_file_path)
                os.makedirs(log_dir, exist_ok=True)

                # 使用RotatingFileHandler支持日志轮转
                file_handler = RotatingFileHandler(
                    self.log_file_path,
                    maxBytes=self.max_file_size,
                    backupCount=self.backup_count,
                    encoding="utf-8",
                )
                file_formatter = logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
                )
                file_handler.setFormatter(file_formatter)
                logger.addHandler(file_handler)
                print(f"📁 文件日志已启用: {self.log_file_path}")

            # 飞书Handler
            feishu_handler = self.FeishuHTTPHandler(self.webhook_url, self.min_level)
            logger.addHandler(feishu_handler)

        return logger

    class FeishuHTTPHandler(logging.Handler):
        """自定义Handler，将日志发送到飞书webhook"""

        def __init__(self, webhook_url, min_level=logging.ERROR):
            super().__init__()
            self.webhook_url = webhook_url
            self.min_level = min_level

        def mapLogRecord(self, record):
            """重写日志格式映射，构造飞书消息体"""
            log_time = datetime.fromtimestamp(record.created).strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            # 根据日志级别返回不同的消息格式
            if record.levelname == "ORDER":
                return {
                    "msg_type": "text",
                    "content": {
                        "text": f"💰 **交易订单通知** 💰\n\n"
                        f"⏰ **时间**: <font color='green'>{log_time}</font>\n"
                        f"📊 **系统**: <font color='blue'>交易监控系统</font>\n"
                        f"🏷️ **类型**: <font color='orange'>**订单状态更新**</font>\n"
                        f"💻 **服务**: <font color='grey'>{record.processName}</font>\n\n"
                        f"📋 **订单详情**:\n"
                        f"```\n{record.getMessage()}\n```\n\n"
                        f"---\n"
                        f"<font color='grey'>*交易系统自动通知*</font> 📈"
                    },
                }
            elif record.levelno >= self.min_level:  # 使用可配置的最小级别
                # 格式化时间
                log_time = datetime.fromtimestamp(record.created).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                # 原有的错误/警告日志格式
                return {
                    "msg_type": "text",
                    "content": {
                        "text": f"🚨 **程序发生错误告警** 🚨\n\n"
                        f"📅 **时间**: <font color='grey'>{log_time}</font>\n"
                        f"📁 **文件**: <font color='blue'>`{record.filename}`</font> (Line: **{record.lineno}**)\n"
                        f"🔥 **级别**: <font color='red'>**{record.levelname}**</font>\n"
                        f"💻 **进程**: <font color='grey'>{record.processName} ({record.process})</font>\n"
                        f"🧵 **线程**: <font color='grey'>{record.threadName}</font>\n\n"
                        f"💥 **错误详情**:\n"
                        f"```\n{record.getMessage()}\n```\n\n"
                        f"---\n"
                        f"<font color='grey'>*自动化日志监控系统*</font> | "
                    },
                }
            return None  # 低于最小级别的日志不发送

        def emit(self, record):
            """发送日志到飞书（自动跳过低级别日志）"""
            log_body = self.mapLogRecord(record)
            if not log_body:
                return  # 忽略低级别日志
            try:
                # 构建HTTP请求
                headers = {"Content-Type": "application/json"}
                requests.post(
                    self.webhook_url,
                    data=json.dumps(log_body),
                    headers=headers,
                    timeout=5,
                )
            except Exception as e:
                print(f"⚠️ 发送日志到飞书失败: {e}")

    def get_logger(self):
        """获取配置好的logger实例"""
        return self.logger

    def get_log_file_path(self):
        """获取当前日志文件路径"""
        return self.log_file_path if self.enable_file_log else None

    def set_file_log_enabled(self, enabled):
        """动态启用/禁用文件日志"""
        if enabled and not self.enable_file_log:
            # 启用文件日志
            self.enable_file_log = True
            log_dir = os.path.dirname(self.log_file_path)
            os.makedirs(log_dir, exist_ok=True)

            file_handler = RotatingFileHandler(
                self.log_file_path,
                maxBytes=self.max_file_size,
                backupCount=self.backup_count,
                encoding="utf-8",
            )
            file_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
            print(f"📁 文件日志已动态启用: {self.log_file_path}")

        elif not enabled and self.enable_file_log:
            # 禁用文件日志
            self.enable_file_log = False
            # 移除文件handler
            for handler in self.logger.handlers[:]:
                if isinstance(handler, RotatingFileHandler):
                    self.logger.removeHandler(handler)
                    handler.close()
            print("📁 文件日志已禁用")

    def info(self, message):
        """发送INFO级别日志"""
        self.logger.info(message)

    def warning(self, message):
        """发送WARNING级别日志"""
        self.logger.warning(message)

    def error(self, message):
        """发送ERROR级别日志"""
        self.logger.error(message)

    def order(self, message):
        """发送ORDER级别日志（订单通知）"""
        self.logger.order(message)


# ===== 使用示例 =====
if __name__ == "__main__":
    # 替换为你的飞书机器人Webhook URL
    WEBHOOK_KEY = "https://www.feishu.cn/flow/api/trigger-webhook/44e904a7f35d914119a73d3d5e3083ea"

    # 初始化FeishuLogger (启用文件日志)
    feishu_logger = FeishuLogger(
        webhook_url=WEBHOOK_KEY,
        min_level=logging.WARN,
        enable_file_log=False,
        log_file_path="./logs/my_app.log",
        max_file_size=5 * 1024 * 1024,  # 5MB
        backup_count=3,
    )

    feishu_logger.info("这是一个信息日志，不会发送到飞书，但会记录到文件")
    feishu_logger.order(
        "订单 #12345 已创建 | 用户: user123 | 金额: ¥1,299.00 | 商品: iPhone 15"
    )
    feishu_logger.order(
        "订单 #12345 支付成功 | 支付方式: 微信支付 | 交易号: wx20231201123456"
    )

    print(f"当前日志文件路径: {feishu_logger.get_log_file_path()}")

    # 动态禁用文件日志
    # feishu_logger.set_file_log_enabled(False)

    # feishu_logger.warning("这是一个警告日志，会发送到飞书")
    # feishu_logger.error("这是一个错误日志，会发送到飞书")
