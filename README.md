# rs-partners

Here you can find all the RS-APIs and Modules to simplify communication across all our partner products

## Setup

### Pre-requisites
- Python > 3.x
- pip3 (package-management system)
- [rs-utils](https://github.com/RoundServices/rs-utils)

## Couchbase API requisites
- install couchbase dependencies following [SDK instructions](https://docs.couchbase.com/python-sdk/current/hello-world/start-using-sdk.html)
- install CMake 3.x
```sh
# CentOS
sudo yum -y install make3

# Ubuntu 20
sudo apt-get -y install make
```  

## Deploy
To install/upgrade Round Services &copy; python-commons library, execute the following command on your server

- SSH deploy
```sh
pip install --upgrade git+ssh://git@github.com:RoundServices/rs-partners.git@main
```
- HTTPS deploy
```sh
pip install --upgrade git+https://github.com/RoundServices/rs-partners.git@main
```
- zip file downloaded from github
```sh
unzip -d ./ ./rs-partners-main.zip
pip3 install --upgrade --force-reinstall ./rs-partners-main/.
rm -rf ./rs-partners-main/
```

## Coding

All classes contained in **rs** folder can be used to develop awesome scripts or classes, just import the dependencies on your python code:
```python
from rs.package.MyClass import MyClass
```
