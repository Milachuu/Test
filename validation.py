def sanitisation(data_input):
    string_field = str(data_input).lower()
    valid = True
    for character in string_field:
        print(character)
        if character in ["<",">","/","'",'"','"""',"*",":","=","{","}"]:
            string_field = string_field.replace(character,"")
            print(string_field)

            valid = False

    
    if "script" in string_field:
        valid = False
        string_field = string_field.replace("script","")
        print(string_field)


    return string_field


