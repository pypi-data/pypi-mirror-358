# CreateFile with Designated Encoding ✨

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/StarWindv/CreateFile-with-DesignatedEncoding/blob/main/LICENSE)
[![PyPI Version](https://img.shields.io/pypi/v/stv_create_file)](https://pypi.org/project/stv_create_file/)
[![Python Versions](https://img.shields.io/pypi/pyversions/stv_create_file)](https://pypi.org/project/stv_create_file/)

[English](./README.en.md)

**CreateFile with Designated Encoding** 是一个强大的命令行工具，用于创建具有指定编码格式的文件，支持自定义元数据标签和多语言提示。

> 用您指定的编码创建文件

## 🌟 核心功能

- **指定文件编码** - 创建 UTF-8、GBK、Big5 等多种编码格式的文件
- **元数据标签** - 自定义文件首行的元数据格式
- **多语言支持** - 自动适配中英文界面
- **编码验证** - 创建后自动检测文件实际编码
- **独占模式** - 防止意外覆盖现有文件
- **详细日志** - 可选的详细输出模式
- **用户配置** - 保存偏好设置到配置文件

## 🚀 安装方式

### 通过 PyPI 安装

```bash
pip install stv_create_file
```

### 通过 GitHub 源码安装

```bash
git clone https://github.com/StarWindv/CreateFile-with-DesignatedEncoding.git
cd CreateFile-with-DesignatedEncoding
pip install .
```

## 🛠 使用指南

### 基本命令

```bash
create [文件路径] [选项]
nf [文件路径] [选项]      # newfile 的缩写
newfile [文件路径] [选项] # 完整命令
```

### 命令行选项

| 选项               | 简写     | 默认值     | 描述         |
|------------------|--------|---------|------------|
| `--encoding`     | `-e`   | `utf-8` | 文件编码格式     |
| `--prefix`       | `-p`   | `#`     | 文件首行前缀     |
| `--left-paren`   | `-l`   | `<\|`   | 元数据左标签     |
| `--right-paren`  | `-r`   | `\|>`   | 元数据右标签     |
| `--monopolize`   | `-m`   | `False` | 独占模式（防止覆盖） |
| `--coding-check` | `-cc`  | `False` | 创建后验证编码    |
| `--verbose`      | `-v`   | `False` | 详细输出模式     |
| `--version`      | `-V`   | -       | 显示版本信息     |
| `--license`      | `-lic` | -       | 显示项目许可证    |

### 使用示例

1. **创建基本文件**
   ```bash
   create example.txt
   ```

2. **指定文件编码**
   ```bash
   nf data.csv -e gbk
   ```

3. **自定义元数据格式**
   ```bash
   newfile config.ini -p "// " -l "{{" -r "}}"
   ```

4. **独占模式创建**
   ```bash
   create important.log -m
   ```

5. **创建并验证编码**
   ```bash
   nf report.txt -e big5 -cc -v
   ```

## ⚙️ 配置文件

配置文件位于：`~/.stv_project/config.json`

**默认配置：**
```json
{
    "lang": "English",
    "verbose": false
}
```

**可配置项：**
- `lang`：界面语言 (`English`/`zh-cn`)
- `verbose`：是否默认启用详细输出模式

## 📂 项目结构

```
CreateFile-with-DesignatedEncoding/
├── LICENSE
├── pyproject.toml
├── README.md
├── README.en.md
└── src/
    └── stv_create_file/
        ├── core/
        │   ├── __init__.py
        │   ├── FileCreator.py    # 文件创建核心逻辑
        │   └── stv_parse.py      # 命令行参数解析
        ├── main.py               # 程序入口点
        ├── mul_lang/
        │   ├── __init__.py
        │   └── change_text.py    # 多语言支持
        └── utils/
            ├── __init__.py
            ├── GetConfig.py      # 配置管理
            └── utils.py          # 工具函数
```

## 📦 依赖项

- `chardet` - 文件编码检测库

## 📜 许可证

本项目采用 [MIT 许可证](https://github.com/StarWindv/CreateFile-with-DesignatedEncoding/blob/main/LICENSE)

## 🤝 贡献指南

欢迎通过 Issue 或 Pull Request 作出贡献！  
项目地址：[GitHub 仓库](https://github.com/StarWindv/CreateFile-with-DesignatedEncoding)