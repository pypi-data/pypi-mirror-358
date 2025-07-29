from setuptools import setup, find_packages

setup(
    name='mseep-mcp-neo4j-aura-manager',
    version='0.2.3',
    description='MCP Neo4j Aura Database Instance Manager',
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
    install_requires=['mcp>=1.6.0', 'requests>=2.31.0'],
    keywords=['mseep'],
)
