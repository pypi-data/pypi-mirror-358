from setuptools import setup, find_packages

setup(
    name='mseep-code-index-mcp',
    version='0.3.1',
    description='Code indexing and analysis tools for LLMs using MCP',
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
    install_requires=['mcp>=0.3.0'],
    keywords=['mseep'],
)
