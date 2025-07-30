import argparse
from sys import argv as sys_argv
from stv_create_file.mul_lang.change_text import parse_text
from stv_create_file.utils.GetConfig import start_process
__version__ = "0.0.3"

configer = start_process()
use_verbose = False
if configer.verbose:
    use_verbose = True


def arg_check(short_cut: str = '', full_arg: str = '')->bool:
    """
    检查命令行参数中是否包含指定的参数
    :param short_cut: 参数的简写，如"v"
    :param full_arg: 参数的全称，如"verbose"
    :return: bool
    """
    for args in sys_argv:
        if (args.startswith("-")
                and short_cut in args
                and not args.startswith("--")
                or args == full_arg)\
                or use_verbose:
            """
            因为 argparse 的短参数可以合并
            所以我们需要检查某参数是否以 "-" 开头且包含指定的短参数字母
            同时要排除以 "--" 开头的长参数
            """
            return True
    return False


def advance_parse():
    parser = argparse.ArgumentParser(add_help = False)
    parser.add_argument('-lic', '--license', action="store_true")
    parser.add_argument('-V', '--version', action="store_true")
    parser.add_argument('-sl', '--set-language', type=str, choices=['chinese', 'english'])
    args, _ = parser.parse_known_args()
    if args.version:
        print(f"Project Version: {__version__}")
        exit(0)
    if args.license:
        print("Project License: MIT")
        exit(0)
    if args.set_language:
        configer.change(key = "lang", value = "chinese" if args.set_language == "chinese" else "english")
        print("Language changed successfully." if (configer.lang == "english" or configer.lang == "en-uk") else "语言已更改成功")
        exit(0)


def stv_parse():
    advance_parse()
    text = parse_text(function_name="stv_parse")
    parser = argparse.ArgumentParser(description=text["description"])
    parser.add_argument('path', nargs='+', help=text["path"])
    # nargs 代表 接受至少1个参数值，无上限
    parser.add_argument('-e', '--encoding', type=str, default='utf-8', help=text["encoding"])
    parser.add_argument('-p', '--prefix', type=str, default='#', help=text["prefix"])
    parser.add_argument('-l', '--left-paren', type=str, default='<|', help=text["left_paren"])
    parser.add_argument('-r', '--right-paren', type=str, default='|>', help=text["right_paren"])

    parser.add_argument('-m', '--monopolize', action="store_true", help=text["monopolize"])

    parser.add_argument('-cc', '--coding-check', action="store_true", help=text["coding_check"])
    parser.add_argument('-V', '--version', action="store_true", help=text["version"])
    parser.add_argument('-lic', '--license', action="store_true", help=text["license"])
    parser.add_argument('-v', '--verbose', action="store_true", help=text["verbose"])
    parser.add_argument('-D', '--Debug', action="store_true", help=argparse.SUPPRESS)

    parser.add_argument('-sl', '--set-language', type=str,
                        choices=['chinese', 'english'],help=text["lang"])
    args = parser.parse_args()

    if use_verbose:
        args.verbose = True

    return args
