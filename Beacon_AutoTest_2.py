#!/usr/bin/env python3
# coding: utf-8
import pandas as pd
import time
import os
import numpy as np
import re
import multiprocessing as mp


def input_row_numbers():
    """
    Prompt user input for the row numbers. Ex: 2,3,4,5
    :return: list of row numbers
    """

    while True:
        try:
            row_num_list = [int(x) - 1 for x in input("Please input the row number/numbers ex 1 3 4:").split()]
            break
        except ValueError:
            print("Error: Input should be numeric number")
    return row_num_list


def extract_param_range_str_to_dict(model_name, sim_model_info):
    """
    extract parameters value range list from "Model" sheet in excel and return: dict of parameters range value
    example of parameter range format:  "SAMPLE_TIME: (0:inf),Threshold: (-inf:inf),Gain: (1:10)..."

    :param model_name: model name used in test
    :param sim_model_info: data frame generated from "Model" sheet in "test_info_1.xlsx"
    :return: params range value as a dictionary , format of output: {param1: [1,10], param2: [2,20]}
    """

    param_list = sim_model_info[sim_model_info["Sim_model"] == model_name]["Parameter_range_list"].values[0].split(",")
    params_range_value_dict = {}

    for _item in param_list:
        [param_name, param_value] = _item.split(" ")  # extract param_name & value_range with "(:)"
        [minimum, maximum] = param_value[1:-1].split(":")  # extract min and max
        params_range_value_dict[param_name] = [float(minimum), float(maximum)]

    return params_range_value_dict


def param_verify(error_flag, test_dataframe, model_dataframe):
    """
    self-checking of modified parameters against default parameter name & within default value range
    format of params values include 3 type:
        1. param1: (1:1:5) -> this is fine tune param
        2. param2: (1,2,3,4,5) -> also a fine tune param
        3. param3: (1) -> param with fixed value
    Note: In our code, just allow one fine tune param in each row.

    :param error_flag: a flag for checking if there is error in modified params
    :param test_dataframe: sub data frame of "Default Parameters" sheet only include info of rows we choose at the beginning
    :param model_dataframe: data frame for "Model" Sheet in "test_info_1.xlsx"
    :return: 1 if we find the error in params info and 0 for no error
    """

    model_list = test_dataframe["Sim_model"].values[:]
    for _i, _model in enumerate(model_list):
        find_finetune_var = 0
        params_range_value_dict = extract_param_range_str_to_dict(_model, model_dataframe)
        row_num = test_dataframe.iloc[_i]['Row']
        modified_params = test_dataframe.iloc[_i]["Modified Parameters"]

        if pd.isna(modified_params):
            print("-----> Input %d: Row #%d  model %s no customized parameter is defined. Default parameter is used. \n"
                  % (_i + 1, row_num, _model))
        else:
            # what if modified_params_name is NAN?
            modified_params_name = re.findall(r"([a-zA-Z]+[_]*[a-zA-Z]+[:])", modified_params)
            modified_params_value = re.findall(r"([-]*[0-9]+[.]*[0-9]*:[-]*[0-9]+[.]*[0-9]*:[-]*[0-9]+[.]*[0-9]*"
                                               r"|[-]*[0-9]+[.]*[0-9]*(,[-]*[0-9]+[.]*[0-9]*)+|[-]*[0-9]+[.]*[0-9]*)",
                                               modified_params)  # list made of tuple

            for param_idx, param_item in enumerate(modified_params_name):
                value = modified_params_value[param_idx][
                    0]  # delete last element in each sublist of modified params values

                if param_item not in params_range_value_dict:
                    print("-----> Input %d: ERROR Row#%d model %s parameter <%s> is not defined. Simulation aborted\n" %
                          (_i + 1, row_num, _model, param_item))
                    error_flag = 1

                elif ":" in value:
                    [minimum, step, maximum] = value.split(":")
                    if float(minimum) > float(maximum) or float(minimum) < params_range_value_dict[param_item][
                        0] or float(maximum) > params_range_value_dict[param_item][1] or float(step) + float(
                            minimum) > float(maximum):
                        print(
                            "-----> Input %d: ERROR Row#%d  model %s parameter <%s> value is out of range. Simulation aborted\n"
                            % (_i + 1, row_num, _model, param_item))
                        error_flag = 1
                    else:
                        find_finetune_var += 1

                elif "," in value:
                    value_list = value.split(",")
                    for value_item in value_list:
                        if float(value_item) < params_range_value_dict[param_item][0] or float(value_item) > \
                                params_range_value_dict[param_item][1]:
                            print(
                                "-----> Input %d: ERROR Row#%d  model %s parameter <%s> value is out of range. Simulation aborted\n"
                                % (_i + 1, row_num, _model, param_item))
                            error_flag = 1
                    find_finetune_var += 1

                elif float(value) < params_range_value_dict[param_item][0] or float(value) > \
                        params_range_value_dict[param_item][1]:
                    print(
                        "-----> Input %d: ERROR Row #%d  model %s parameter <%s> value is out of range. Simulation aborted\n"
                        % (_i + 1, row_num, _model, param_item))
                    error_flag = 1

        if find_finetune_var > 1:
            print('-----> Input %d: ERROR Row #%d too many fine-tune parameter.  Simulation aborted\n' % (
            _i + 1, row_num))
            error_flag = 1

    if error_flag == 0:
        print('--> Parameter input is verified and accepted. \n')
    else:
        print('--> Parameter input is not valid. Please modify the input parameters. \n')

    return error_flag


def usecase_verify(error_flag, test_dataframe, usecase_dataframe):
    """
    self-checking if the use case No. exist
    format of Use Case: "1,2,3,..."

    :param error_flag:  flag for checking if there is error in "UseCases" column
    :param test_dataframe: sub data frame of "Default Parameters" sheet only include info of rows we choose at the beginning
    :param usecase_dataframe: data frame for "TestUseCase" Sheet in "data_info.xlsx"
    :return: 1 if there is error in use case column
    """
    usecase_array = test_dataframe['UseCases'].values[:]  # returns numpy array instead of pandas series
    total_usecase_number = usecase_dataframe.shape[0]

    for _i, _usecase in enumerate(usecase_array):
        row_num = test_dataframe.iloc[_i]['Row']

        if pd.isna(_usecase):
            print("-----> Input %d: ERROR Row #%d use case is empty. Simulation aborted\n"
                  % (_i + 1, row_num))
            error_flag = 1
        else:

            for _item in str(_usecase).split(","):  # what about only 1 usecase
                if int(round(float(_item))) < 0 or int(round(float(_item))) > total_usecase_number:
                    print("------> Input %d: ERROR Row #%d < use_case %s > is not on the list.Simulation aborted \n"
                          % (_i + 1, row_num, _item))
                    error_flag = 1

    if error_flag == 0:
        print('--> Use case input is verified and accepted. \n')
    else:
        print('--> Use case input is not valid. Please check the UseCases from test_info.xlsx. \n')

    return error_flag


def reformat_usecase_list(usecase_array):
    """
    extract signal No.s from "TestUseCase" sheet "UseCaseSet" column
    convert format from "Lib1: (1,2,3);Lib2: (3,4,5)" to "1,2,3,4,5,6"

    :param usecase_array: list of usecase No.s in each row
    :return: list of strings represent signal No.s used in each row
    """

    usecase_array_reformat = []
    usecase_array_each_lib = usecase_array.split(";")
    _signal_nos = ""
    for _usecase_no_list in usecase_array_each_lib:
        [_name, _signals] = _usecase_no_list.split(" ")
        _signal_nos += ("," + _signals[1:-1])

    usecase_array_reformat.append(_signal_nos[1:])
    return usecase_array_reformat[0]


def convert_usecase_to_signal_list(usecase_dataframe, usecaselist):
    """
    convert list of use cases No. to list of Signal No. in each use case
    eg. use case list [1,2]
        use case No.1  -> Signal No.2 & 3
        use case No.2  -> Signal No.4 & 5
        Final new signal usecase list -> [2,3,4,5]
     signal list to be updated with library information
    :param usecase_dataframe: data frame generated by "TestUseCase" in "data_info.xlsx"
    :param usecaselist: list of use cases No. you want to use for each testing.
    :return: signals No.s list based on the use cases you choose.
    """

    signal_no_list = []
    for _i in usecaselist:
        signal_id_list_with_libname = str(
            usecase_dataframe[usecase_dataframe["Row"] == int(float(_i))]["UseCase_set"].values[0])
        signal_id_list_wout_libname = reformat_usecase_list(signal_id_list_with_libname)

        for _j in signal_id_list_wout_libname.split(","):
            _signal_no = int(_j)
            if _signal_no not in signal_no_list:
                signal_no_list.append(_signal_no)

    return signal_no_list


def append_test_sequence_to_df(test_info_dataframe, params_dict, fine_tune, model, signal_no_list):

    """
    add row information (model,Parameters,Model Number, Signal Set) to the test_info_dataframe
    making different combinations of params and signal ID and append them into dataframe
    eg.
    input: Params_dict: {param1: [1,2], param2: 3}; signal_no_list=[4,5],model: 'MP_test'
    output data frame:
        Model        Params                  signal_no_list
        'MP_test'    param1: 1, param2: 3     4
        'MP_test'    param1: 1, param2: 3     5
        'MP_test'    param1: 2, param2: 3     4
        'MP_test'    param1: 2, param2: 3     5
    df is hardcoded  with the following fields: 'Model_Parameters','Model_No''SignalSet','SignalSet'

    :param test_info_dataframe: data frame used for saving all info used for Simulation
    :param params_dict: dictionary saved params name & value for each model
    :param fine_tune: fine_tune parameter
    :param model: simulink model name (only 1 name)
    :param signal_no_list: list of use cases No. for each rows
    :return: test_info_dataframe after adding new rows info
    """

    df_col = {'Model_Parameters': None, 'Model_No': None, 'SignalSet': None}
    temp_df_save_testinfo_eachrow = pd.DataFrame(df_col, index=range(0, 1))  # create a data frame

    for _i in params_dict[fine_tune]:
        temp_parameters = ""
        for _param in params_dict:
            if _param != fine_tune:
                # remove extra "[]" in parameters column
                params_dict[_param] = params_dict[_param][0] if isinstance(params_dict[_param], list) else params_dict[
                    _param]
                temp_parameters += ("," + _param[:-1] + ": " + str(params_dict[_param]))
            else:
                temp_parameters += ("," + _param[:-1] + ": " + str(_i))
            temp_df_save_testinfo_eachrow.Model_Parameters = temp_parameters[1:]  # hardcoded
            temp_df_save_testinfo_eachrow.Model_No = model  # hardcoded
            temp_df_save_testinfo_eachrow.SignalSet = None  # hardcoded

        for _item in signal_no_list:
            temp_df_save_testinfo_eachrow.SignalSet = _item
            test_info_dataframe = test_info_dataframe.append(temp_df_save_testinfo_eachrow)

    return test_info_dataframe


def create_simulink_input_df(test_dataframe, usecase_dataframe):
    """
    Create a test_info_dataframe for simulink test
    test_info_dataframe is hardcoded  with the following fields: 'Model_Parameters','Model_No''SignalSet','SignalSet'

    :param test_dataframe: sub data frame of "Default ParameterSet" sheet only included the rows info based on rows number you input
    :param usecase_dataframe: data frame of "TestUseCase" sheet
    :return: a new data frame included all info (Model, Parameters, Signal Use Case) used for simulink testing
    """
    test_info_dataframe = pd.DataFrame({'Model_Parameters': None, 'Model_No': None, 'SignalSet': None},
                                       index=range(0, 1))
    model_list = test_dataframe['Sim_model'].values[:]

    for _i, _model in enumerate(model_list):
        default_params = test_dataframe.iloc[_i]["Parameters"].split(",")
        modifed_params = test_dataframe.iloc[_i]["Modified Parameters"]
        usecase = test_dataframe.iloc[_i]["UseCases"]
        signal_no_list = convert_usecase_to_signal_list(usecase_dataframe, str(usecase).split(","))

        modified_params_name = re.findall(r"([a-zA-Z]+[_]*[a-zA-Z]+[:])", modifed_params)  # extract parameters name
        modified_params_value = re.findall(r"([-]*[0-9]+[.]*[0-9]*:[-]*[0-9]+[.]*[0-9]*:[-]*[0-9]+[.]*[0-9]*"
                                           r"|[-]*[0-9]+[.]*[0-9]*(,[-]*[0-9]+[.]*[0-9]*)+|[-]*[0-9]+[.]*[0-9]*)",
                                           modifed_params)  # require modify

        params_dict = {}  # default param, dictionary
        for _item in default_params:  # extract default parameters name and values into a dictionary
            [param_name, param_value] = _item.split(" ")
            params_dict[param_name] = float(param_value)

        # what about modified params is NaN?
        fine_tune = ""
        for _ii, _item in enumerate(modified_params_name):
            value = modified_params_value[_ii][0]

            if ":" in value:
                [minimum, step, maximum] = value.split(":")
                params_dict[_item] = np.arange(float(minimum), float(maximum) + float(step), float(step))
                fine_tune = _item

            elif "," in value:
                params_dict[_item] = [float(x) for x in value.split(",")]
                fine_tune = _item

            else:
                params_dict[_item] = [float(value)]
                if fine_tune == "":
                    fine_tune = _item

        test_info_dataframe = append_test_sequence_to_df(test_info_dataframe, params_dict, fine_tune, _model,
                                                         signal_no_list)

    test_info_dataframe.reset_index(drop=True, inplace=True)
    test_info_dataframe = test_info_dataframe.drop([0])
    print('\n--> Simulation test sequence is generated:  ')
    return test_info_dataframe


def output_excel_create(test_info_dataframe, loglist_dataframe, log_filename):
    """
    generate 2 excel files into folders:
        1) simulation_log -> contain simulation_log_[].xlsx
        2) Matlab_input -> contain sim_[].xlsx
    :param test_info_dataframe: contain information of the tests to be executed with columns Model, Parameters, Signal Use Case
    :param loglist_dataframe: data frame of log file
    :param log_filename: name of the log file
    :return: none
    """
    log_folder = "Testinfo_history_log"  # hardcoded , change needed
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    output_folder = "Excel_files_for_Simulink_testing"  # hardcoded , change needed
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    current_time = time.strftime("%Y-%m-%d-%H-%M")  # time str
    test_info_dataframe.to_excel("%s/sim_%s.xlsx" % (output_folder, current_time))  # temp simulation log
    test_info_df_rownum = test_info_dataframe.shape[0] + 1

    output_files_dir_list = [os.path.abspath("%s/sim_%s.xlsx" % (log_folder, current_time))] * test_info_df_rownum
    current_time_list = [current_time] * test_info_df_rownum

    # add them into the test_info_dataframe
    path = pd.DataFrame({'Path': output_files_dir_list})
    date = pd.DataFrame({'Date': current_time_list})
    test_info_dataframe = pd.DataFrame.join(test_info_dataframe, path)  # add path
    test_info_dataframe = pd.DataFrame.join(test_info_dataframe, date)  # add time

    loglist_dataframe = loglist_dataframe.append(test_info_dataframe, sort=False, ignore_index=True)
    loglist_dataframe.to_excel(log_filename, index=False)
    print('\n\nThe following simulation records are added to the log file. \n')
    print(test_info_dataframe.to_string())


def matlab_simulation(entry):
    print('matlab -nodesktop -nosplash -r "Autotest_Beacon({0},{1},{2},{3},{4},{5},{6},{7},{8});exit"'.format(
        entry[0], entry[1], entry[2], entry[3], entry[4], entry[5], entry[6], entry[7], entry[8]))


def create_matlab_input_list(test_info_dataframe, datalib_dataframe, model_dataframe):
    """
    create input arguments for Matlab which runs Simulink model simulations
    :param test_info_dataframe:   hardcoded
        "Model_Parameters"
        "Model_No"
        "SignalSet"
    :param datalib_dataframe:     hardcoded
        "RawSignal_FileName"
        "folder_path"
    :param model_dataframe:       hardcoded
        "Sim_model"
        "Model_No"
        "Model_description"
        "Parameter_range_list"
    :return: entry -> nested list with each sublist contain inputs for each Matlab simulation run  hardcoded
        _entry0 Full_File
        _entry1 Parameters
        _entry2 index of each row in Matlab_input/sim- excel file
        _entry3 Model filename
        _entry4 Simulink_output_foldername    log_#_date
        _entry5 Signal_filepath
        _entry6 ModelPath
        _entry7 initialization function name
        _entry8 Signal No.
    """

    num_sim_run = test_info_dataframe.shape[0]  # total number of simulations to run
    current_time = time.strftime("%Y-%m-%d-%H-%M")  # time str
    entry = []  # master list
    # for each simulation, there will be a list of 9 Matlab input arguments
    for _i in range(num_sim_run):
        signal_idx = int(test_info_dataframe.iloc[_i]["SignalSet"])  # signal
        signal_name = datalib_dataframe.iloc[signal_idx]["filename"]  # str
        param = test_info_dataframe.iloc[_i]["Model_Parameters"]
        model = test_info_dataframe.iloc[_i]["Model_No"]
        foldername = current_time
        signal_path = (datalib_dataframe.iloc[signal_idx]["DataFolderName"] + "/" +
                       datalib_dataframe.iloc[signal_idx][
                           "StudyName"])  # should change as folder path + study name + signal name
        model_path = model_dataframe[model_dataframe["Sim_model"] == test_info_dataframe.iloc[_i]["Model_No"]][
            "Sim_FilePath"].values[0]

        _entry0 = "'" + signal_name + "'"
        _entry1 = "'" + param + "'"
        _entry2 = "'" + str(_i) + "'"
        _entry3 = "'" + model + "'"
        _entry4 = "'" + "Log_" + foldername + "'"
        _entry5 = "'" + signal_path + "'"
        _entry6 = "'" + model_path + "'"
        _entry7 = "'" + model[:-4] + "_init.m" + "'"
        _entry8 = "'" + str(signal_idx) + "'"

        entry_list = [_entry0, _entry1, _entry2, _entry3, _entry4, _entry5, _entry6, _entry7, _entry8]
        entry.append(entry_list)  # add sublist to master list

    return entry


