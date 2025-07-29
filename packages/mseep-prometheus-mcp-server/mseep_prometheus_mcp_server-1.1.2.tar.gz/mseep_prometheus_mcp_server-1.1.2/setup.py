from setuptools import setup, find_packages

setup(
    name='mseep-prometheus_mcp_server',
    version='1.1.2',
    description='MCP server for Prometheus integration',
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
    install_requires=['mcp[cli]', 'prometheus-api-client', 'python-dotenv', 'pyproject-toml>=0.1.0', 'requests', 'structlog>=23.0.0'],
    keywords=['mseep'],
)
