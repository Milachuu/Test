class Feedback():
    def __init__(self,feedback_ID,name,email,message):
        self.__feedbackID = feedback_ID
        self.__name = name
        self.__email = email
        self.__message = message
       
    
    def set_feedback_ID(self,feedback_ID):
        self.__feedbackID = feedback_ID

    def set_name(self,name):
        self.__name = name

    def set_email(self,email):
        self.__email = email

    def set_message(self,message):
        self.__message = message
    
    def get_feedback_ID(self):
        return self.__feedbackID
    
    def get_name(self):
        return self.__name
    
    def get_email(self):
        return self.__email
    
    def get_message(self):
        return self.__message
    