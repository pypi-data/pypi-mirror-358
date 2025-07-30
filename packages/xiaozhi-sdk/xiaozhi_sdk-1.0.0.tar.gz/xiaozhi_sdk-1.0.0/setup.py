from setuptools import find_packages, setup

setup(
    name="xiaozhi-sdk",  # 包名
    version="1.0.0",  # 版本号
    packages=find_packages(),  # 自动发现包
    install_requires=[  # 依赖
        "numpy",
        "websockets",
        "aiohttp",
        "av",
        "opuslib",
        "requests",
        "sounddevice",
        "python-socks"
    ],
    author="dairoot",
    author_email="623815825@qq.com",  # 作者邮箱
    description="一个用于连接和控制小智智能设备的Python SDK，支持实时音频通信、MCP工具集成和设备管理功能。",  # 简短描述
    long_description=open("README.md").read(),  # 详细描述（通常从 README 读取）
    long_description_content_type="text/markdown",  # README 文件格式
    url="https://github.com/dairoot/xiaozhi-sdk",  # 项目主页
    classifiers=[  # 分类元数据
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",  # 支持的 Python 版本
)
