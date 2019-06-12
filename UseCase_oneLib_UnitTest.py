# -*- coding: utf-8 -*-
"""
Created on Thu Jun  6 11:16:04 2019

@author: 90546523
"""

import unittest
from UseCase_oneLib.py import *

# unit test for UseCase_oneLib.py script:
class TestCase_UseCase_oneLib(unittest.TestCase):
    
    def setUpClass(self):
        self.filename= 'RX_Data_library.xlsx'   
        self.rule_df = pd.read_excel(filename,sheet_name = 'UseCaseGenerationInput')
        self.lib_df = pd.read_excel(filename,sheet_name = 'Summary')[["LibraryName", "SubLibrary name"]]
        self.lib_num_list= [0,1,2]
        self.lib_name_list = [self.lib_df['LibraryName'].unique()[x] for x in self.lib_num_list]
        self.rule_dict={'Axis0': [20],'Axis3': [45],'Medium': ['Tissue'],'TransducerLength_mm': [0.6]}
        self.data_df_list = create_df_list(self.filename,self.lib_name_list)
        self.rule_num= 1
        self.row_num= 7
    def test_input_rule_num(self):
        print('enter 1 for unit test')
        self.assertEqual(input_rule_num(),1)
    def test_create_rule_dict(self):
        self.assertEqual(create_rule_dict(1,rule_df), self.rule_dict)
    def test_input_lib_num(self):
        print('enter 1 2 3 for unit test')
        self.assertEqual(input_lib_num(),self.lib_num_list)   
    def test_isfloat(self):
        self.assertTrue(isfloat(4))
    def test_create_usecase(self):
        self.assertEqual(create_usecase(self.data_df_list, self.filename, self.rule_dict, self.lib_name_list, self.rule_num), self.row_num)
    

# unittest.main(argv=[''], verbosity=2, exit=False) # for Jupyter notebook execution   
if __name__ == '__main__':
    unittest.main()
