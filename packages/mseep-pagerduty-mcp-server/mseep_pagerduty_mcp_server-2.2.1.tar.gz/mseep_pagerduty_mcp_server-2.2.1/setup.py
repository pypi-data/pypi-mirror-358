from setuptools import setup, find_packages

setup(
    name='mseep-pagerduty_mcp_server',
    version='2.2.1',
    description='MCP server for LLM agents to interact with PagerDuty SaaS',
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
    install_requires=['hatch>=1.14.1', 'fastmcp>=2.5.1', 'pagerduty>=1.0.0', 'pytest>=8.3.5', 'ruff>=0.11.2'],
    keywords=['mseep', 'pagerduty', 'mcp', 'llm', 'api', 'server'],
)
