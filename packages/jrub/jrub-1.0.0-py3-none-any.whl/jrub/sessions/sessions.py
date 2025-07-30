from os.path import exists
from json import loads, dumps

class Sessions:

    def __init__(self, client:object) -> None:
        self.client = client

    def cheackSessionExists(self):
        return exists(f"{self.client.session}.jrub")
    
    def loadSessionData(self):
        return loads(open(f"{self.client.session}.jrub", encoding="UTF-8").read())
        
    def createSession(self):
        from ..methods import Methods
        methods:object = Methods(
            sessionData={},
            platform=self.client.platform,
            apiVersion=6,
            proxy=self.client.proxy,
            timeOut=self.client.timeOut,
            showProgressBar=True
        )

        while True:
            phoneNumber:str = input("📱 Enter your phone number (start with country code, e.g. 98 for Iran, 1 for USA):\nExample for Iran: 989123456789\nExample for USA: 11326547896\nphone > ")

            try:
                sendCodeData:dict = methods.sendCode(phoneNumber=phoneNumber)
            except Exception as e:
                print(f"The phone number is invalid! Please try again. {e}")
                continue

            if sendCodeData['status'] == 'SendPassKey':
                while True:
                    passKey:str = input(f'\nEnter the pass key [{sendCodeData["hint_pass_key"]}]  » ')
                    sendCodeData:dict = methods.sendCode(phoneNumber=phoneNumber, passKey=passKey)
                    
                    if sendCodeData['status'] == 'InvalidPassKey':
                        print(f'\nThe pass key({sendCodeData["hint_pass_key"]}) is invalid! Please try again.')
                        continue
                    break
            
            while True:
                phoneCode:str = input("\ncode » ").strip()
                signInData:dict = methods.signIn(phoneNumber=phoneNumber, phoneCodeHash=sendCodeData['phone_code_hash'], phoneCode=phoneCode)
                if signInData['status'] != 'OK':
                    print("The code is invalid! Please try again.")
                    continue
                break
            
            from ..crypto import Cryption

            sessionData = {
                'auth': Cryption.decryptRsaOaep(signInData["private_key"], signInData['auth']),
                'private_key': signInData["private_key"],
                'user': signInData['user'],
            }

            open(f"{self.client.session}.jrub", "w", encoding="UTF-8").write(dumps(sessionData, indent=4))

            Methods(
                sessionData=sessionData,
                platform=self.client.platform,
                apiVersion=6,
                proxy=self.client.proxy,
                timeOut=self.client.timeOut,
                showProgressBar=True
            ).registerDevice(deviceModel=f"jrub {self.client.session}")
            print(f"\nSign\"{self.client.session}\" ok")

            return sessionData