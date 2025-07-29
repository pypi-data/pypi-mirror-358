import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "renovosolutions.aws-cdk-crowdstrike-ingestion",
    "version": "0.0.0",
    "description": "A CDK library to ease repetetive construct creation for CrowdStrike data ingestion",
    "license": "Apache-2.0",
    "url": "https://github.com/RenovoSolutions/cdk-library-crowdstrike-ingestion.git",
    "long_description_content_type": "text/markdown",
    "author": "Renovo Solutions<webmaster+cdk@renovo1.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/RenovoSolutions/cdk-library-crowdstrike-ingestion.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "crowdstrike_ingestion",
        "crowdstrike_ingestion._jsii"
    ],
    "package_data": {
        "crowdstrike_ingestion._jsii": [
            "cdk-library-crowdstrike-ingestion@0.0.0.jsii.tgz"
        ],
        "crowdstrike_ingestion": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "aws-cdk-lib>=2.200.1, <3.0.0",
        "constructs>=10.0.5, <11.0.0",
        "jsii>=1.112.0, <2.0.0",
        "publication>=0.0.3",
        "typeguard>=2.13.3,<4.3.0"
    ],
    "classifiers": [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Typing :: Typed",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
