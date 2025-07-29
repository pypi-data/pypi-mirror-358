from setuptools import setup, find_packages

setup(
    name='mseep-mcp-neo4j-cypher',
    version='0.2.4',
    description='A simple Neo4j MCP server',
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
    install_requires=['mcp[cli]>=1.6.0', 'neo4j>=5.26.0', 'pydantic>=2.10.1'],
    keywords=['mseep'],
)
