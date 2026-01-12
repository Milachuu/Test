class two_fa():
    def __init__(self, email, totp_secret):
        self.__email = email
        self.__totp_secret = totp_secret
    
    def get_email(self):
        return self.__email

    def get_totp_secret(self):
        return self.__totp_secret
    

    def set_email(self,email):
        self.__email = email

    def set_totp(self, totp_secret):
        self.__totp_secret = totp_secret
    

    
