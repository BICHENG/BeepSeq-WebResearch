from setuptools import setup, find_packages

# # 读取 README.md 作为长描述
# with open("README.md", "r", encoding="utf-8") as f:
#     long_description = f.read()

setup(
    name="webresearch",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A powerful web research tool for crawling and extracting content from websites.",
    long_description="A powerful web research tool for crawling and extracting content from websites.",
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/webresearch",  # 替换为你的项目地址
    packages=find_packages(),  # 自动查找所有包
    install_requires=[
        "alive_progress",
        "cachetools",
        "uvicorn",
        "fastapi",
        "nodriver",
        "duckduckgo-search",
        "lxml_html_clean",
        "py3langid",
        "brotli",
        "cchardet",
        "faust-cchardet",
        "py3langid",
        "pycurl",
        "urllib3[socks]",
        "zstandard",
        "trafilatura[all]",
        "htmldate[speed]",
        "typer",
        "rich",
        # "click",
        "numpy<2",
    ],
    entry_points={
        'console_scripts': [
            'webresearch=cli:app',  # 注意路径是 webresearch.cli:app
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",  # 最低 Python 版本要求
)