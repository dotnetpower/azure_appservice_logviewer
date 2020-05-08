# -*- coding: utf-8 -*-

import sys, logging, requests
logging.basicConfig(level=logging.INFO, filename='logviewer.log')
requests.packages.urllib3.disable_warnings() #ignore certificate verification

from azure.cli.core import get_default_cli
from requests.auth import HTTPBasicAuth

class AzHelper:
    def __init__(self):
        self.azResource = self.az_cli('login')
        self.subscriptionId = ''
        self.subscriptionName = ''
        self.resourceGroupName = ''
        self.logstreamUri = ''
        self.appServiceName = ''
        self.deploymentSlotName = ''

        logging.info('start')


    # https://stackoverflow.com/questions/51546073/how-to-run-azure-cli-commands-using-python
    def az_cli(self, args_str):
        args = args_str.split()
        cli = get_default_cli()
        cli.invoke(args)
        print('\n')
        if cli.result.result:
            return cli.result.result
        elif cli.result.error:
            raise cli.result.error
        return True


    def askInput(self, message):
        print('--------------------------------------------------------------------')
        return input(message)


    def askSubscription(self):
        logging.info('call askSubscription')

        count = 0
        for subscriptions in self.azResource: 
            count += 1
            print(f"{count}. {subscriptions['id']} - {subscriptions['name']}")

        selectedNum = self.askInput(f"Please choose subscription number[1-{len(self.azResource)}]: ")
        self.subscriptionId = self.azResource[int(selectedNum)-1]['id']
        self.subscriptionName = self.azResource[int(selectedNum)-1]['name']
        self.az_cli(f"account set --subscription {self.subscriptionId}")


    def askAppService(self):
        logging.info('call askAppService')
        result = self.az_cli('webapp list')
        
        count = 0
        for app in result:
            count += 1
            print(f"{count}. {app['name']}")

        selectedNum = self.askInput(f"Please choose app service number[1-{len(result)}]: ")

        #check running state
        if result[int(selectedNum)-1]['state'] != 'Running':
            print(f"{result[int(selectedNum)-1]['name']} is not running")
            sys.exit()

        self.appServiceName = result[int(selectedNum)-1]['name'].lower()
        self.resourceGroupName = result[int(selectedNum)-1]['resourceGroup'].lower()
        self.logstreamUri = f"https://{result[int(selectedNum)-1]['hostNameSslStates'][1]['name']}/api/logstream".lower()
    

    #it can skip if app service has not slot.
    def askSlot(self):
        logging.info('call askSlot')
        result = self.az_cli(f"webapp deployment slot list --resource-group {self.resourceGroupName} --name {self.appServiceName}")

        if result == True: # return True if return value is null
            return

        count = 0
        for slot in result:
            count += 1
            print(f"{count}. {slot['name']}")
        
        selectedNum = self.askInput(f"Please choose deployment slot number[1-{len(result)}]: ")
        self.deploymentSlotName = result[int(selectedNum)-1]['name'].lower()

        #change logstream uri
        self.logstreamUri = self.logstreamUri.replace(self.appServiceName, f"{self.appServiceName}-{self.deploymentSlotName}")
    

    def getCredential(self):

        if self.deploymentSlotName:
            result = self.az_cli(f"webapp deployment list-publishing-credentials --resource-group {self.resourceGroupName} --name {self.appServiceName} --slot {self.deploymentSlotName}")
        else:
            result = self.az_cli(f"webapp deployment list-publishing-credentials --resource-group {self.resourceGroupName} --name {self.appServiceName}")
        
        return result['publishingUserName'], result['publishingPassword']


    def checkLogSettings(self):
        result = self.az_cli(f"webapp log show --resource-group {self.resourceGroupName} --name {self.appServiceName}")

        loggingOptions = ['Error', 'Warning', 'Information', 'Verbose']

        if result['applicationLogs']['fileSystem']['level'] == 'Off':
            count = 0
            for option in loggingOptions:
                count += 1
                print(f"{count}. {option}")

            selectedNum = self.askInput(f"Application logging turned off. Please choose logging level number[1-{len(loggingOptions)}]: ")

            if self.deploymentSlotName:
                action = self.az_cli(f"webapp log config --resource-group {self.resourceGroupName} --name {self.appServiceName} --slot {self.deploymentSlotName} --application-logging --level {loggingOptions[int(selectedNum)-1]}")
            else:
                action = self.az_cli(f"webapp log config --resource-group {self.resourceGroupName} --name {self.appServiceName} --application-logging --level {loggingOptions[int(selectedNum)-1]}")
            

    def viewLog(self):
        logging.info('call viewLog')
        publishingUserName, publishingPassword = self.getCredential()

        req = requests.get(self.logstreamUri, stream=True, auth=HTTPBasicAuth(publishingUserName, publishingPassword), verify=False)

        print('Connecting... (it takes a few seconds)')
        isConnected = False

        for line in req.iter_lines():
            if line:
                if isConnected == False:
                    isConnected = True
                    print('Connected!!')

                print(line.decode('utf-8'))


if __name__ == '__main__':
    azhelper = AzHelper()
    azhelper.askSubscription()
    #skip askResourceGroup
    azhelper.askAppService()
    azhelper.askSlot()
    azhelper.checkLogSettings()
    azhelper.viewLog()
