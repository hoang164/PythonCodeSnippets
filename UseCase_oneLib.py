# -*- coding: utf-8 -*-
"""

"""

import pandas as pd
from openpyxl import load_workbook

def input_rule_num():
    while True:
        try:
            rule_num = int(input("please input rule# ex 1:"))
            break
        except ValueError:
            print("Error: Input should be numberic number")
    return rule_num


def create_df_list(filename,lib_name_list):
    
    data_df_list=[] 
    data_df = pd.read_excel(filename,sheet_name = 'DataLibrary')
    for _lib in lib_name_list:
        try: 
            #data_df_list += [pd.read_excel(filename,sheet_name = _lib)] # list of dataFrame objects
             data_df_list += [data_df[data_df['LibraryName']==_lib]]
        except: 
             continue
    return data_df_list

     

def input_lib_num():
    
     while True:
        try:
           lib_num_list = [int(x)-1 for x in input("Please input library number ex 1 3 4:").split()] 
           break
        except ValueError:
            print("Error: Input should be numeric number")
     return lib_num_list
 
    
def create_usecase(data_df_list, filename, rule_dict, lib_name_list,rule_num):
       
   
    usecase_format=[] 
    
    for _i,item in enumerate(lib_name_list):  
        sig_idx_list=[]  
       
        newdf= data_df_list[_i]  
        for match_item in rule_dict:
            temp = pd.DataFrame()
            for _ii, _item in enumerate(rule_dict[match_item]) :
                temp = temp.append( newdf[newdf[match_item]==rule_dict[match_item][_ii]])
            newdf = temp
            
        sig_idx_list = list(newdf['Row'].values)
        signal_str= ",".join(str(s) for s in sig_idx_list)
        usecase_format += ["{}: ({})".format(lib_name_list[_i], signal_str)] # list   

    usecase_format= ",".join(str(s) for s in usecase_format)  # convert from list to 1 string
    lib_format=",".join(str(s) for s in lib_name_list)
    # Output a new excel file with new usecase
    usecase_df = pd.read_excel(filename,sheet_name = 'TestUseCase')
    row_num = usecase_df.shape[0] + 1  
    description = ""
    
    temp_df = pd.DataFrame([[row_num,usecase_format,description,rule_num,lib_format]],columns = ["Row","UseCase_set","Description","Rule_Number","Lib_Used"])
    #usecase_df = usecase_df.append(temp_df,ignore_index = True)
    
    book = load_workbook(filename)
    std = book['TestUseCase']
    #book.remove(std)
    #writer = pd.ExcelWriter(filename,engine ='openpyxl')
    #writer.book = book
    #usecase_df.to_excel(writer, sheet_name = 'TestUseCase', index = False)
    #writer.save()
    #writer.close()
    
    for index, row in temp_df.iterrows():
        std.append(row.tolist())

    book.save(filename)
    return row_num

def create_rule_dict(rule_num, rule_df):
    temp_rule_df = rule_df[rule_df['Rule_Number'] == rule_num]
    rule_dict ={}
    
    for item in temp_rule_df:  # key
                
        if pd.isna (temp_rule_df[item]).bool() or (item == 'Rule_Number'):
            temp_rule_df = temp_rule_df.drop(item, axis=1)
        
        else:
            value = temp_rule_df[item][rule_num-1]
            
            if (isfloat(value)):
                rule_dict[item] = [value]
                
            elif "," in value:
                rule_dict[item] = [float(x) for x in value.split(",")] 
            else:
                rule_dict[item] = [value]
                
                 
    return rule_dict
    

def isfloat(x):
    try:
        float(x)
        return True
    except:
        return False
    
    
# Main Program

# import data and use case library
# RX_Data_library has the following datasheet
#   Summary
#   TestUseCase
#   DataLibrary
#   Lib1   Ezono
#   Lib2   GE
#   Lib3   Sonosite
#   Lib4   Toshiba
#   Lib5   Sonosite 3-D
#   Rule



filename= 'RX_Data_library.xlsx'   
rule_df = pd.read_excel(filename,sheet_name = 'UseCaseGenerationInput')
lib_df = pd.read_excel(filename,sheet_name = 'Summary')[["LibraryName", "SubLibrary name"]]

## rule only one rule
#print(rule_df.to_string())
print(rule_df['Rule_Number'].values)
rule_num = input_rule_num()
rule_dict = create_rule_dict(rule_num, rule_df)

## libray list based on user input
print('\n Data Library are:')
print(lib_df['LibraryName'].unique())
lib_num_list= input_lib_num()
lib_name_list = [lib_df['LibraryName'].unique()[x] for x in lib_num_list]

## generate df_list based on the lib
data_df_list = create_df_list(filename,lib_name_list)
  

# create new usecase 
row_num = create_usecase(data_df_list, filename, rule_dict, lib_name_list,rule_num)

#current_dir= os.getcwd()
print('TestUseCase #%d has been created'%(row_num))

