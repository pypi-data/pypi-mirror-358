import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mcp_stock_calculator",
    version="0.1.0",
    author="YORK",
    author_email="27123167@qq.com",
    description="A股技术指标计算器 - 提供MACD, RSI, KDJ, BOLL等常用技术指标计算",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yorkqqcom/mcp_stock_calculator",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Office/Business :: Financial",
        "Topic :: Office/Business :: Financial :: Investment",
        "Development Status :: 4 - Beta",
    ],
    python_requires='>=3.7',
    install_requires=[
        'flask>=2.0.0',
        'pandas>=1.0.0',
        'numpy>=1.18.0',
        'akshare>=1.0.0',
    ],
    entry_points={
        'console_scripts': [
            'mcp_calculator_kel = mcp_stock_calculator:main',
        ],
    },
    include_package_data=True,
    keywords='stock, technical indicator, a-share, chinese stock, finance',
)