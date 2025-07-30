import datetime
from sys import stdout as sys_stdout
import codecs


def get_format_time()->str:
    now = datetime.datetime.now()
    """
    # 格式化为 yyyy-mm-dd hh:mm:ss
    """
    return now.strftime("%Y-%m-%d %H:%M:%S")


def log_print(color: int = 0,
              prefix: str = "[Log]",
              msg: str = "Default Log Msg",
              sep: str = " ",
              end: str = "\n"):
    sys_stdout.write(f"\x1b[{color}m{prefix}{sep}{msg}\x1b[0m{end}")


def can_encode(encoding = ''):
    try:
        encoder = codecs.lookup(encoding).incrementalencoder()
        encoder.encode("宽字符测试", final=True)
        return True
    except UnicodeEncodeError:
        return False