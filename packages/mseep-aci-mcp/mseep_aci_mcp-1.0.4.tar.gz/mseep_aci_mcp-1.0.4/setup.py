from setuptools import setup, find_packages

setup(
    name='mseep-aci-mcp',
    version='1.0.4',
    description='ACI MCP server, built on top of ACI.dev by Aipolabs',
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
    install_requires=['aci-sdk>=1.0.0b2', 'anthropic>=0.49.0', 'anyio>=4.9.0', 'click>=8.1.8', 'httpx>=0.27.2', 'mcp>=1.6.0', 'starlette>=0.46.1', 'uvicorn>=0.34.0'],
    keywords=['mseep', 'aipolabs', 'mcp', 'aci', 'mcp server', 'llm', 'tool calling', 'function calling'],
)
