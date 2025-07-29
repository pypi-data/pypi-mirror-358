import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "renovosolutions.aws-cdk-fargate-log-collector",
    "version": "0.0.0",
    "description": "AWS CDK Construct Library to deploy CloudWatch Agent as a Fargate service",
    "license": "Apache-2.0",
    "url": "https://github.com/RenovoSolutions/cdk-library-fargate-log-collector.git",
    "long_description_content_type": "text/markdown",
    "author": "Renovo Solutions<webmaster+cdk@renovo1.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/RenovoSolutions/cdk-library-fargate-log-collector.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "fargate_log_collector",
        "fargate_log_collector._jsii"
    ],
    "package_data": {
        "fargate_log_collector._jsii": [
            "cdk-library-fargate-log-collector@0.0.0.jsii.tgz"
        ],
        "fargate_log_collector": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "aws-cdk-lib>=2.199.0, <3.0.0",
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
