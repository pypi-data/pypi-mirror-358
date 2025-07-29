from setuptools import setup, find_packages

setup(
    name='mseep-awslabs.nova-canvas-mcp-server',
    version='1.0.2',
    description='An AWS Labs Model Context Protocol (MCP) server for Amazon Nova Canvas',
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
    install_requires=['boto3>=1.37.24', 'loguru>=0.7.3', 'mcp[cli]>=1.6.0', 'pydantic>=2.11.1', 'pytest>=8.0.0', 'pytest-asyncio>=0.26.0', 'pytest-cov>=4.1.0', 'pytest-mock>=3.12.0'],
    keywords=['mseep'],
)
