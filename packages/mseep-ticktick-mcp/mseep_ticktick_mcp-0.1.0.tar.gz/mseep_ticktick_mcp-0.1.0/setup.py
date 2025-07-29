from setuptools import setup, find_packages

setup(
    name="mseep-ticktick-mcp",
    
    long_description="Package managed by MseeP.ai",
    long_description_content_type="text/plain",version="0.1.0",
    description="Model Context Protocol (MCP) server for TickTick task management",
    author="mseep",
    author_email="parkjs814@gmail.com",
    
    maintainer="mseep",
    maintainer_email="support@skydeck.ai",url="https://github.com/parkjs814/ticktick-mcp",
    packages=find_packages(),
    install_requires=[
        "mcp[cli]>=1.2.0,<2.0.0",
        "python-dotenv>=1.0.0,<2.0.0",
        "requests>=2.30.0,<3.0.0",
    ],
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "ticktick-mcp=ticktick_mcp.cli:main",
            "ticktick-auth=ticktick_mcp.authenticate:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)