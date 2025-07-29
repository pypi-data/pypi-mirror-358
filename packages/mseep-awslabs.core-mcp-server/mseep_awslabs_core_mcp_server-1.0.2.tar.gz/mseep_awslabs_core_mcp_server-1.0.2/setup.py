from setuptools import setup, find_packages

setup(
    name='mseep-awslabs.core-mcp-server',
    version='1.0.2',
    description='An AWS Labs Model Context Protocol (MCP) server for aswlabs Core MCP Server',
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
    install_requires=['boto3>=1.37.0', 'loguru>=0.7.3', 'mcp[cli]>=1.3.0', 'pydantic>=2.10.6', 'python-dotenv>=1.0.1'],
    keywords=['mseep'],
)
