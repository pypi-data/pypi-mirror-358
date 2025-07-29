from setuptools import find_packages, setup

setup(
    name="xiaozhi-sdk",  # 包名
    version="0.1.0",  # 版本号
    packages=find_packages(),  # 自动发现包
    install_requires=[  # 依赖
        "numpy",
        "requests>=2.32.1",
        "sounddevice>=0.4.2",
    ],
    author="dairoot",
    author_email="623815825@qq.com",  # 作者邮箱
    description="A short description of your package",  # 简短描述
    long_description=open('README.md').read(),  # 详细描述（通常从 README 读取）
    long_description_content_type='text/markdown',  # README 文件格式
    url="https://github.com/dairoot/xiaozhi-sdk",  # 项目主页
    classifiers=[  # 分类元数据
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",  # 支持的 Python 版本
)
