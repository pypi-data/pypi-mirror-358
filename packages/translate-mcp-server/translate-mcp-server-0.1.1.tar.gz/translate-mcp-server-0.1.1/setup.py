from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="translate-mcp-server",
    version="0.1.0",
    author="TranslateMcpServer",
    author_email="example@example.com",
    description="MCP服务器用于项目国际化，提供提取中文、翻译中文、替换文本功能",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/translate-mcp-server",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7, <3.13",
    install_requires=[
        "mcp-server>=0.1.0",
        "aliyun-python-sdk-core>=2.13.0",
        "aliyun-python-sdk-alimt>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "translate-mcp-server=translate_mcp_server.cli:main",
        ],
    },
    include_package_data=True,
    keywords="i18n, internationalization, translation, chinese, english, mcp, server",
)