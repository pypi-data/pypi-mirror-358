from setuptools import setup, find_packages

setup(
    name='mseep-tripo-mcp',
    version='0.1.5',
    description='MCP (Model Control Protocol) integration for Tripo',
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
    install_requires=['tripo3d>=0.2.0', 'mcp[cli]>=1.4.1'],
    keywords=['mseep', 'mcp', 'blender', '3d', 'automation'],
)
