from setuptools import setup, find_packages

setup(
    name='mseep-mcp-analyst',
    version='0.3.3',
    description='MCP Analyst is an MCP server that empowers claude to analyze local CSV or Parquet files.',
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
    install_requires=['mcp[cli]>=1.6.0', 'polars>=1.26.0'],
    keywords=['mseep'],
)
