# nb_print

[![pypi](https://img.shields.io/pypi/v/nb-print.svg)](https://pypi.org/project/nb-print)
[![versions](https://img.shields.io/pypi/pyversions/nb-print.svg)](https://pypi.org/project/nb-print)
[![license](https://img.shields.io/pypi/l/nb-print.svg)](https://pypi.org/project/nb-print)

**`nb_print`：让你的 `print()` "活" 起来，一键跳转到代码位置。**

在大型项目或遗留代码中进行调试时，你是否曾被满屏的 `print` 输出所困扰，苦苦寻找 "这行输出究竟是哪里打印的？" `nb_print` 正是为解决这一痛点而生。

它通过极简的方式，增强了 Python 内置的 `print` 函数，让你的每一次打印输出都附带源码位置的超链接。

---

## ✨ 核心功能

- **🚀 无感植入**: 只需在项目入口 `import nb_print` 一次，无需修改任何现有 `print` 代码，即可全局生效。
- **🖱️ 点击跳转**: 在 PyCharm, VSCode 等现代 IDE 的控制台中，点击输出前缀即可直接跳转到发起 `print` 的确切代码行。
- **🎨 智能美化**: 自动美化打印内容，提升复杂数据结构（如 `dict`, `list`）在控制台中的可读性。
- **🎯 解决痛点**: 彻底告别大海捞针式的 `print` 调试，极大提升开发和排错效率。

## 📦 安装

```bash
pip install nb-print
```

## 🚀 使用方法

在你的项目主入口文件（例如 `main.py` 或 `app.py`）的顶部，加入一行导入语句即可。

```python
# a_module.py
def some_function():
    user_data = {'id': 1001, 'name': 'Alice', 'roles': ['admin', 'editor']}
    print(user_data)

# main.py
import nb_print  # 只需要在程序入口导入一次

import requests
from a_module import some_function

print("程序开始运行...")
some_function()
print(requests.get('https://www.baidu.com/'))
print("程序运行结束。")
```

## 效果演示

**使用前**，你的控制台输出是这样的，无法快速定位来源：

```text
程序开始运行...
{'id': 1001, 'name': 'Alice', 'roles': ['admin', 'editor']}
<Response [200]>
程序运行结束。
```

**使用 `nb_print` 后**，控制台输出会附带可点击的文件路径和行号：

```text
main.py:10 - 程序开始运行...
a_module.py:4 - {'id': 1001, 'name': 'Alice', 'roles': ['admin', 'editor']}
main.py:12 - <Response [200]>
main.py:13 - 程序运行结束。
```
> 在 PyCharm 或 VSCode 中，`main.py:10` 这部分文本会变成一个超链接，点击即可跳转。

## 🛠️ 工作原理

`nb_print` 的实现非常轻量，其核心原理是 **"猴子补丁" (Monkey Patching)**。

1.  当 `import nb_print` 时，它会用一个自定义的函数替换掉 Python `builtins` 模块中的原生 `print` 函数。
2.  这个新的 `print` 函数在执行打印操作前，会使用 `inspect` 模块回溯调用堆栈 (`inspect.stack()`)。
3.  通过分析堆栈信息，它可以精确地获取到调用者的文件名和行号。
4.  最后，它将文件名和行号格式化后，与原始的打印内容一并输出到控制台。现代 IDE 会自动识别 `文件名:行号` 这种格式并将其渲染为可点击的链接。

## 🤝 贡献

欢迎通过提交 Issues 和 Pull Requests 来贡献代码、报告问题或提出功能建议。

## 📄 许可证

本项目基于 MIT License 开源。