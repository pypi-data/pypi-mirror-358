from setuptools import setup, find_packages

setup(
    name='mseep-keboola-mcp-server',
    version='1.5.1',
    description='MCP server for interacting with Keboola Connection',
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
    install_requires=['fastmcp ~= 2.5, <2.6', 'mcp == 1.9.3', 'httpx ~= 0.28', 'jsonschema~=4.23', 'pyjwt~=2.10', 'json-log-formatter ~= 1.0'],
    keywords=['mseep'],
)
