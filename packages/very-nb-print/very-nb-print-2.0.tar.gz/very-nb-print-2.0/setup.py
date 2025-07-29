

# d:\codes\nb_print\setup.py

import setuptools
from pathlib import Path

# 从 README.md 文件中读取长描述
# 这可以确保 PyPI 上的项目介绍和 GitHub 上保持一致
long_description = Path("README.md").read_text(encoding="utf-8")

setuptools.setup(
    # PyPI 上的包名，必须是唯一的
    name="very-nb-print",

    # 版本号，每次更新上传时都需要增加版本号
    # 建议遵循 PEP 440 规范 (例如: 1.6 -> 1.7, 1.7.1, 1.8.0a1)
    # 你当前最新版本是 1.6，所以下一个版本可以是 1.7
    version="2.0",

    # 作者信息
    author="ydf0509",
    author_email="your_email@example.com",  # !! 重要：请替换为你的邮箱地址

    # 简短描述，会显示在 PyPI 的项目列表页
    description="增强print函数,使其输出内容能被点击并直接跳转到源代码位置",

    # 详细描述，从 README.md 加载
    long_description=long_description,
    long_description_content_type="text/markdown",

    # 项目主页的 URL
    url="https://github.com/ydf0509/nb_print",

    # 自动发现项目中的包
    # 它会在当前目录下寻找所有含有 __init__.py 的文件夹作为包
    packages=setuptools.find_packages(),

    # 项目分类，有助于用户在 PyPI 上搜索和筛选
    classifiers=[
        # 开发状态:
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 5 - Production/Stable",

        # 目标用户
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Debuggers",
        "Topic :: Utilities",

        # 许可证信息
        "License :: OSI Approved :: MIT License",

        # 支持的 Python 版本
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",


        # 操作系统
        "Operating System :: OS Independent",
    ],

    # 指定项目依赖的最低 Python 版本
    python_requires='>=3.6',

    # 项目的依赖包
    # nb_print 似乎没有外部依赖，所以这里保持为空
    # install_requires=[
    #     "requests",
    # ],
)


"""

python setup.py sdist bdist_wheel ; twine upload dist/*




"""