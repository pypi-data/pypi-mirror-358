# Example Package

This is a simple example package. You can use
[GitHub-flavored Markdown](https://guides.github.com/features/mastering-markdown/)
to write your content. 

The program is also a simple Python program that does nothing except
state that there is nothing to see.  

Here is the how-to on how to build and deploy it.
```shell
cd <PROJECT-DIRECTORY>
# start with a clean `venv`
rm -fr venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
# remember to increment the version value in `pyproject.toml` before each new build
pip install build
pip install twine
# build the distribution
python3 -m build
# upload to test.pypi.org (user is __token__, pw is API token)
python3 -m twine upload --verbose --repository testpypi dist/*
#
# PyPi module can be installed like this:
# BAND-noop

```console
pip install -i https://test.pypi.org/simple/ noop-BAND
```
# module is run like this:

```console
noop
```
# output is this:
`INFO:root:nothing to see here`




