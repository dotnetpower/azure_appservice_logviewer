# Overview
This script is a tool that makes it easy to view the streamming logs of Azure App Service.

Support Features
- choose subscription
- choose resource group
- choose app service
- set development slot
- change logging level

# Prerequisites
Python 3.x

## Dependencies
requests==2.23.0
azure-cli-core==2.4.0
azure-cli==2.4.0


## clone
```
git clone https://github.com/dotnetpower/azure_appservice_logviewer.git
cd azure_appservice_logviewer
```

## Install Dependencies
```
pip install -r requirements.txt
```

## Run
```
python logviewer.py

```

## Steps
1. Login
![](images/2020-04-23-23-27-23.png)

2. Close Browser
![](images/2020-04-23-23-28-13.png)

3. select subscription
![](images/2020-04-23-23-29-41.png)

4. select app service
![](images/2020-04-23-23-32-45.png)

5. select log level
![](images/2020-04-23-23-33-46.png)

6. connecting
![](images/2020-04-23-23-35-59.png)

```
Enjoy debugging~
```

