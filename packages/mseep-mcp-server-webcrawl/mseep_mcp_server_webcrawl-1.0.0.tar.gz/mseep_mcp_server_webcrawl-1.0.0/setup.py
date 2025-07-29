from setuptools import setup, find_packages

setup(
    name='mseep-mcp-server-webcrawl',
    version='1.0.0',
    description='MCP server for search and retrieval of web crawler content',
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
    install_requires=['mcp>=1.3.0', 'lxml>=4.6.0', 'Pillow>=9.0.0', 'aiohttp>=3.8.0', 'warcio>=1.7.0', 'ply==3.11'],
    keywords=['mseep'],
)
