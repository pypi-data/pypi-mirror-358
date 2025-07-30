from setuptools import setup, find_packages

setup(
    name="apc-core",
    version="0.1.0",
    description="APC (Agent Protocol Conductor) core protocol library for decentralized agent orchestration.",
    long_description=open("../README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="APC Contributors",
    url="https://github.com/deepfarkade/apc-protocol",
    packages=find_packages(),
    install_requires=[
        "grpcio",
        "grpcio-tools",
        "websockets",
        "redis",
        "boto3"
    ],
    python_requires=">=3.8",
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    project_urls={
        "Documentation": "https://github.com/deepfarkade/apc-protocol/blob/main/docs/documentation.md",
        "Source": "https://github.com/deepfarkade/apc-protocol",
        "Tracker": "https://github.com/deepfarkade/apc-protocol/issues",
    },
)
