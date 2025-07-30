import os
import json
from stv_utils import is_ch
from typing import TextIO

home = os.path.expanduser("~")
config_path = os.path.join(home, ".stv_project/config.json")


class ConfigProcessor:
    def load(self, path: str, depth: int = 0) -> dict:
        depth = 1 if not depth else depth
        if depth > 3:
            print("Your config file is broken, please delete it and restart the program")
            exit(-1)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                content = json.load(f)
                if not isinstance(content, dict):
                    try:
                        os.remove(path)
                        self.initialize()
                        """
                        实际上在此处并不会导致递归过多
                        因为我们能重置文件以打破递归
                        并且我们有深度限制
                        """
                        self.load(path, depth=depth+1)
                    except PermissionError:
                        print("Permission denied")
                else:
                    return content
        return {}


    def parse(self, args: str) -> bool or str:
        if self.config:
            try:
                return self.config[args]
            except KeyError:
                print(f"No such key: {args}")
        return ''

    def __str__(self):
        return f"ConfigPath: {self.path}\nConfigText: {self.config}"

    def __init__(self, path: str):
        self.path = path
        self.initialize()
        self.config = self.load(self.path)
        self.verbose = self.parse("verbose")
        self.lang = self.parse("lang")

    def initialize(self):
        if not os.path.exists(self.path):
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            open(self.path, "w", encoding="utf-8").close()
        with (open(self.path, "r+", encoding="utf-8") as f):
            if not f.read():
                print("Initializing config file...")
                content = {"lang": "zh-cn","verbose": False} \
                            if is_ch() \
                            else \
                          {"lang": "en-uk","verbose": False,}
                self.save(content, f)

    def re_parse(self):
        self.initialize()
        self.config = self.load(self.path)
        self.verbose = self.parse("verbose")
        self.lang = self.parse("lang")

    @staticmethod
    def save(content: dict or json, ptr: str or TextIO = None, path = ""):
        if path:
            with open(path, 'w', encoding="utf-8") as f:
                json.dump(content, f, indent=4, ensure_ascii=False)
        else:
            json.dump(content, ptr, indent=4, ensure_ascii=False)

    def change(self, key: str = "", value: bool or str = False):
        if not key or not value:
            raise ValueError("Key and value must be provided")
        self.config[key] = value
        self.save(self.config, path = self.path)
        self.re_parse()


def start_process()->None or ConfigProcessor:
    loader = ConfigProcessor(config_path)
    if __name__ == "__main__":
        print(loader)
    else:
        return loader

if __name__ == "__main__":
    start_process()