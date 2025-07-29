from setuptools import setup, find_packages

setup(
    name='mseep-mcp_doc_scraper',
    version='0.1.3',
    description='MCP server for scraping documentation',
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
    install_requires=['aiohttp', 'mcp', 'pydantic'],
    keywords=['mseep'],
)
