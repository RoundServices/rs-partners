# rs-partners


# rs-partners
Here you can find all the RS-APIs and Modules to simplify communication across all our partner products

## Setup

### Pre-requisites
- Python > 3.x
- pip3 (package-management system)
- [rs-utils](https://github.com/RoundServices/rs-utils)

## Couchbase API requisites
- install couchbase dependencies following [SDK instructions](https://docs.couchbase.com/python-sdk/current/hello-world/start-using-sdk.html)

## Deploy
To install/upgrade Round Services &copy; python-commons library, execute the following command on your server

- SSH deploy (last version)
```sh
pip install --upgrade git+ssh://git@github.com:RoundServices/rs-partners.git@master
```
- HTTPS deploy
```sh
pip install --upgrade git+https://github.com/RoundServices/rs-partners.git@master
```
- zip file downloaded from github
```sh
unzip -d ./ ./rs-partners-main.zip
pip3 install --upgrade --force-reinstall ./rs-partners-main/.
rm -rf ./rs-partners-main/
```

## Coding

All classes contained in **rs** folder can be used for develop awesome scripts or classes, just import the dependencies on your python code:
```python
from rs.package.MyClass import MyClass
```
