#!/usr/bin/env python3
"""This script creates a pip package from the NcpSemApi sources.
The scons target for NcpSemApi calls this script.
"""

import setuptools
import os
import glob
import sys

#print("please run: ./setup.py sdist bdist_wheel <version>")
assert len(sys.argv) == 4, "Wrong number of arguments - you should use the scons target 'NcpSemApi' to call this script"
version = sys.argv[3]
assert version
sys.argv.remove(version)	# setuptools also parse the args. They do not like additional arguments

long_description = ""
with open("README.md", "r") as fh:
	long_description += fh.read()

with open("CHANGELOG.md", "r") as fh:
	long_description += fh.read()

old_files = glob.glob("dist/*")
for file in old_files:
	os.remove(file)

setuptools.setup(
	name="NcpSemApi",
	version=version,
	author="NCP engineering GmbH",
	author_email="info@ncp-e.com",
	description="Python API of the NCP secure enterprise management server",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://ncp-e.com",
	extras_require={
		"ldap-support": ["ldap3"],
		"azure-support": ["msal", "requests"],
		"okta-support": ["okta"]
	},
	install_requires=[],
	packages=["NcpSemApi"],
	license="Proprietary",
	license_files = ("LICNESE.txt",),
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: Other/Proprietary License",
		"Operating System :: OS Independent",
	],
	python_requires='>=3.9',
)
# the above command aborts when errors occure

print()
print(f"NcpSemApi lib files can be found in {os.getcwd()}/build/lib/")
print(f"NcpSemApi package files can be found in {os.getcwd()}/dist/")
print(f"to upload them to PyPi, run 'twine upload {os.getcwd()}/dist/*'")
print("to try the upload without modifying the official release, upload to TestPyPi:")
print(f"run 'twine upload --repository-url https://test.pypi.org/legacy/ {os.getcwd()}/dist/*'")


