from setuptools import setup, find_packages

setup(
    name='mseep-clickhouse-mcp-server',
    version='0.1.1',
    description='A Model Context Protocal (MCP) server that enables secure interaction with Clickhouse. This server allows AI assistants to list tables, read data, and execute SQL queries through a controlled inter...',
    long_description="Package managed by MseeP.ai",
    long_description_content_type="text/plain",
    author='mseep',
    author_email='support@skydeck.ai',
    maintainer='mseep',
    maintainer_email='support@skydeck.ai',
    url='https://github.com/mseep',
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=['clickhouse-connect>=0.8.15', 'httpx>=0.28.1', 'mcp>=1.4.1'],
    keywords=['mseep'],
)
