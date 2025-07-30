from stv_create_file.core.stv_parse import arg_check, stv_parse
from stv_create_file.utils.utils import get_format_time, log_print, can_encode
from stv_create_file.mul_lang.change_text import parse_text
from re import sub as re_sub
import gc
import os
import chardet
import codecs


class FileCreator:
    def __new__(cls, *args, **kwargs):
        if arg_check(short_cut = "v"):
            """
            这一步是因为参数还没解析
            所以使用argv来检测是否启用了详细模式
            又因为 argparse 的参数是可以合并的
            所以需要使用startswith来检测是否以 "-" 开头
            并且包含 "v"
            """
            log_print(color = 90, prefix = "|>", msg = parse_text(function_name="auto")["new"])
        return super().__new__(cls)


    def __del__(self):
        gc.collect()
        if arg_check(short_cut = "v"):
            log_print(color = 90, prefix = "|>", msg = parse_text(function_name="auto")["del"])


    def __init__(self):
        self.args = stv_parse()
        # 需要直接映射的属性列表
        self.attribute = ['path', 'encoding', 'prefix',
                          'left_paren', 'right_paren',
                          'monopolize', 'coding_check',
                          'version', 'license', 'verbose', 'Debug']
        self.args_allot()


    def args_allot(self):
        # 简化方案 / 但是会催生很多 IDE 警告, 有些烦人
        # 批量设置属性
        for attr in self.attribute:
            setattr(self, attr, getattr(self.args, attr))
        self.path = [os.path.abspath(path) for path in self.path[:]]
        self.path = [re_sub(r"\\", "/", path) for path in self.path[:]]
        self.develop = True if (self.Debug and self.verbose) else False
        self.coding_check = True if self.develop else self.coding_check


    def debug_pause(self, function_name: str = "Default")->None:
        if self.Debug:
            log_print(color = 35, prefix = "[DEBUG]", msg = f"DEBUG PAUSE")
            input(f" . . . . . . . ^ In function '{function_name}'")


    def developing(self, function_name: str = "Default")->None:
        if self.develop and function_name != "developing":
            log_print(color = 32, prefix = "[Dev]", msg = f"Calling function: {function_name}")
        else:
            return


    def initialize(self):
        self.debug_pause(function_name="initialize")
        self.developing(function_name = "initialize")
        text = parse_text(function_name="initialize")

        if not self.user_encoding_check(self.encoding):
            log_print(color = 31, prefix = "[Err]", msg = f"{text["coding"]["Err"]}{self.encoding}", sep='  ')
            continue_check = input(f"[Tips] {text['coding']['Tips']}")
            if 'y' not in continue_check.lower():
                exit(-1)
            self.encoding = "utf-8"

        if not self.prefix.isascii():
            log_print(color = 31, prefix = "[Err]", msg = f"{text["prefix"]["Err"]}{self.prefix}", sep = '  ')
            continue_check = input(f"[Tips] {text["prefix"]["Tips"]}")
            if 'y' not in continue_check.lower():
                continue_check = input(f"[Tips] {text['prefix']['default']}")
                if 'y' not in continue_check.lower():
                    exit(-1)
                else:
                    self.prefix = '#'
            else:
                self.prefix = input(f"{text["prefix"]["new_prefix"]}")


        folder_arr = [os.path.dirname(path) for path in self.path]
        nonexistent = []
        ptr = 0
        for folder in folder_arr:
            if not os.path.exists(folder):
                log_print(color = 33, prefix = "[Warn]",
                          msg = f"{text["folder"][0]}{os.path.basename(self.path[ptr])}{text["folder"][1]}{folder}{text["folder"][2]}")
                nonexistent.append(folder)
            ptr += 1

        if nonexistent:
            if self.develop: log_print(color = 32, prefix = "[Dev]", msg = f"{nonexistent}")
            continue_check = input(f"[Tips] {text["folder"]["Tips"]}")
            if 'y' not in continue_check.lower():
                exit(-1)
            nonexistent = set(nonexistent)
            for new_folder in nonexistent:
                try:
                    if self.develop:
                        log_print(color = 32, prefix = "[Dev]", msg = f"{text["folder"]["Dev"]}{new_folder}")
                    os.makedirs(new_folder, exist_ok=True)
                    if self.verbose:
                        print(f"[INFO] {text["folder"]["INFO"]}{new_folder}")
                except Exception as e:
                    log_print(color = 31, prefix = "[Err]", msg = f"{text["folder"]["Exception"]}\n{" "*4}{e}", sep='  ')


    def user_encoding_check(self, encoding_name):
        """
        检查给定的编码名称是否是 Python 支持的编码。
        """
        self.developing(function_name="user_encoding_check")
        try:
            codecs.lookup(encoding_name)
            return True
        except LookupError:
            return False


    def file_coding_check(self, path):
        self.developing(function_name = "file_coding_check")
        text = parse_text(function_name = "file_coding_check")
        detector = chardet.UniversalDetector()
        with open(path, 'rb') as f:
            for line in f:
                detector.feed(line)
                if detector.done:
                    break
        detector.close()
        log_print(color=96, prefix="[INFO]", msg=f"{text["coding"][0]} {os.path.basename(path)} {text["coding"][1]} {detector.result['encoding']}")
        log_print(color=96, prefix="[INFO]", msg=f"[INFO] {text["confidence"]} {detector.result['confidence']}")


    def create_one_file(self,
                        path,
                        encoding: str,
                        prefix: str = '# ',
                        left_paren: str = '<|',
                        right_paren: str = '|>',
                        monopolize = False,
                        verbose: bool = False)->None:
        """
        用于创建指定编码格式的文件
        :param path: 文件路径
        :param encoding: 用户指定的编码
        :param prefix: 创建文件时所写入的前缀，可以指定为注释符号(以在不清理时注释掉第一行)
        :param left_paren: 标签的左侧标记
        :param right_paren: 标签的右侧标记
        :param monopolize: 是否以独占模式创建文件
        :param verbose: 是否启用详细模式
        :return: None
        """

        self.developing(function_name = "create_one_file")

        self.debug_pause(function_name="create_one_file")

        text = parse_text(function_name = "create_one_file")

        mode = 'w'
        if monopolize:
            mode = 'x'

        if verbose:
            print(f"[INFO] {text["creating"]}{os.path.basename(path)}")

        try:
            with open(path, mode, encoding=encoding) as f:
                """
                这很奇怪, 当我们直接使用ANSI打开文件时，如果不写入点什么中文字符，就会变成u8格式
                """
                """
                ANSI 编码是 MBCS 编码的别名
                """
                if can_encode(encoding=self.encoding):
                    content = f"{prefix} {left_paren}NEW FILE{right_paren} 创建\"{os.path.basename(path)}\" {left_paren}END CREATE{right_paren}\n"
                else:
                    content = f"{prefix} {left_paren}NEW FILE{right_paren} {os.path.basename(path)} {left_paren}END CREATE{right_paren}\n"
                    content += f"{prefix} {left_paren} The coding which you want is {self.encoding} not support wide character {right_paren}"
                content += f"{prefix} {left_paren} {get_format_time()} {right_paren}\n"

                if self.develop:
                    log_print(color = 32, prefix = "[Dev]", msg = f"'{content.rstrip()}'")

                f.write(content)
                f.flush()
                print(f"[INFO] {text["created"]}{os.path.basename(path)}")
        except FileExistsError:
            log_print(color = 33, prefix = "[Warn]", msg = f"{text["FileExistsError"]}\033[0m{path}")
        except PermissionError:
            log_print(color = 31, prefix = "[Err]", msg = f"{text["PermissionError"]}\033[0m{os.path.dirname(path)}", sep='  ')
            exit(-1)
        except Exception as e:
            log_print(color = 31, prefix = "[Err]", msg = f"{text["Exception"]}\n{" "*4}\033[0m{e}", sep='  ')
            exit(-1)


    def create_more_file(self):
        self.developing(function_name = "create_more_file")
        for path in self.path:
            self.debug_pause(function_name="create_more_file")
            self.create_one_file(path,
                                 self.encoding,
                                 prefix = self.prefix,
                                 left_paren = self.left_paren,
                                 right_paren = self.right_paren,
                                 monopolize = self.monopolize,
                                 verbose = self.verbose)


    def run(self)-> None:
        self.developing(function_name = "run")
        self.debug_pause(function_name="run")
        self.initialize()
        self.create_more_file()
        if self.coding_check:
            for path in self.path:
                self.file_coding_check(path)