import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="protocolws",
    version="0.2",
    author="Michael Pan",
    author_email="panmpan@gmail.com",

    python_requires='>=3.5',
    install_requires=['asyncws'],

    description="Simple protocol websocket server",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/panmpan17/ProtocolWebsocket",

    packages=setuptools.find_packages(exclude=["build", "dist", "docs",
        "*.egg-info", "testcase"]),
    keywords="websocket protocol socket",
    classifiers=(
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)