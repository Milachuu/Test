class Report():
    def __init__(self, email, reason,other_reason,description):
        self.__email = email
        self.__reason = reason
        self.__other_reason = other_reason
        self.__description = description
    
    def set_email(self,email):
        self.__email = email
    
    def set_reason(self,reason):
        self.__reason = reason
    
    def set_other_reason(self,other_reason):
        self.__other_reason = other_reason

    def set_description(self,description):
        self.__description = description
    
    def get_email(self):
        return self.__email
    
    def get_reason(self):
        return self.__reason
    
    def get_other_reason(self):
        return self.__other_reason
    
    def get_description(self):
        return self.__description
        
    