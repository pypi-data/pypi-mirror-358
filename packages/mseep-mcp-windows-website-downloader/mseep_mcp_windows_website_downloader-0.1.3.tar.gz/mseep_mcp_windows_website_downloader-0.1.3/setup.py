from setuptools import setup, find_packages

setup(
    name='mseep-mcp-windows-website-downloader',
    version='0.1.3',
    description='Simple MCP server for downloading documentation websites',
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
    install_requires=['aiohttp>=3.8.0', 'beautifulsoup4>=4.9.0', 'mcp-python>=0.1.0', 'lxml>=4.9.0'],
    keywords=['mseep'],
)
