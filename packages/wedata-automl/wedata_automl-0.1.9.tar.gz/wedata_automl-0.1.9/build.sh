#!/bin/bash

# set current build version
version_file="wedata/__init__.py"
version=$(grep -o '__version__ = "[^"]*"' "$version_file" | awk -F'"' '{print $2}')
echo "current version: $version"

# install necessary packages
pip3 install twine
pip3 install build

# package as wheel
python3 setup.py sdist bdist_wheel

# upload to pypi tencent mirror
python3 -m twine upload dist/* --repository-url https://mirrors.tencent.com/repository/pypi/tencent_pypi/simple --username maxxhe --password 04d76d9897fe11efb8a0525400161d4c

#upload to pypi
python3 -m twine upload dist/*