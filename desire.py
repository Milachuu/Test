class desire():
    def __init__(self, email, item,description):
        self.__email = email
        self.__item = item
        self.__description = description
       
    
    def get_email(self):
        return self.__email
    
    def get_item(self):
        return self.__item
    
    def get_description(self):
        return self.__description
    
   
    
    def set_email(self,email):
        self.__email = email
    
    def set_item(self,item):
        self.__item = item
    
    def set_description(self,description):
        self.__description = description
    

    
    
