from setuptools import setup, find_packages

setup(
    name='mseep-cratedb-mcp',
    version='1.0.1',
    description='CrateDB MCP Server for natural-language Text-to-SQL and documentation retrieval.',
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
    install_requires=['attrs', 'cachetools<7', 'click<9', 'cratedb-about==0.0.5', 'fastmcp<2.7', 'hishel<0.2', 'pueblo==0.0.11', 'sqlparse<0.6'],
    keywords=['mseep', 'cratedb', 'documentation retrieval', 'knowledge base', 'mcp', 'mcp server', 'model context protocol', 'sql', 'text-to-sql'],
)
