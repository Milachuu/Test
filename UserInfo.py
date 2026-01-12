
class UserInfo():
    count_id = 0

    def __init__(self,username,gender,postal_code,email,login_email,phone_number,bio,points = 0):
        UserInfo.count_id += 1
        self.__UserInfo_id = UserInfo.count_id
        self.__username = username
        self.__gender = gender
        self.__postal_code = postal_code
        self.__email = email
        self.__login_email = login_email
        self.__phone_number = phone_number
        self.__bio = bio
        self.__points = points

    def get_UserInfo_id(self):
        return self.__UserInfo_id
    
    def get_username(self):
        return self.__username
    
    def get_gender(self):
        return self.__gender
    
    
    def get_postal_code(self):
        return self.__postal_code
    
    def get_email(self):
        return self.__email
    
    def get_login_email(self):
        return self.__login_email
    
    def get_phone_number(self):
        return self.__phone_number
    
    def get_bio(self):
        return self.__bio
    
    def get_points(self):
        return self.__points
    
    def set_UserInfo_id(self,User_Info_id):
        self.__UserInfo_id = User_Info_id
    
    def set_username(self,username):
        self.__username = username
    
    def set_gender(self,gender):
        self.__gender = gender
    
    def set_postal_code(self,postal_code):
        self.__postal_code = postal_code
    
    def set_email(self,email):
        self.__email = email
    
    def set_login_email(self,login_email):
        self.__login_email = login_email

    def set_phone_number(self,phone_number):
        self.__phone_number = phone_number

    def set_bio(self,bio):
        self.__bio = bio
    
    def set_points(self,points):
        self.__points = points

        