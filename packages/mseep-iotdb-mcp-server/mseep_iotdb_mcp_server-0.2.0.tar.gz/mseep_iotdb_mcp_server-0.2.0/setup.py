from setuptools import setup, find_packages

setup(
    name='mseep-iotdb-mcp-server',
    version='0.2.0',
    description='A Model Context Protocol (MCP) server that enables secure interaction with IoTDB databases. This server allows AI assistants to list tables, read data, and execute SQL queries through a controlled ...',
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
    install_requires=['fastmcp>=2.8.1', 'apache-iotdb>=2.0.3', 'openpyxl>=3.1.5'],
    keywords=['mseep'],
)
