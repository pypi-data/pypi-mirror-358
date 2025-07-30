import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "ajithapackage1",
    "version": "0.0.23",
    "description": "ajithapackage1",
    "license": "Apache-2.0",
    "url": "https://github.com/ajestharl/genet-test-repo.git",
    "long_description_content_type": "text/markdown",
    "author": "Ajitha<ajithamanit@gmail.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/ajestharl/genet-test-repo.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "ajithapackage1",
        "ajithapackage1._jsii"
    ],
    "package_data": {
        "ajithapackage1._jsii": [
            "ajithapackage1@0.0.23.jsii.tgz"
        ],
        "ajithapackage1": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.8",
    "install_requires": [
        "aws-cdk-lib>=2.1.0, <3.0.0",
        "constructs>=10.0.5, <11.0.0",
        "jsii>=1.108.0, <2.0.0",
        "publication>=0.0.3",
        "typeguard>=2.13.3,<4.3.0"
    ],
    "classifiers": [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
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
