#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  2 09:40:26 2018

@author: Saif

"""

import os.path
import io
import collections
import datetime

data_dir = 'JLRCCCommon-Redev/features'
dest_folder = 'Testing/BDD Tests/Classes/XCTestCase'

def check_manual(filename, folder):
    
    with open(folder) as info:
            data = info.read()
    
    data = data.split("\n")
    feature_key = "Feature:"
    manual_key = "@manual"
    for i in range(len(data)):
        if feature_key in data[i]:
            if manual_key in data[i-1]:
                return True
            else:
                return False

def find_feature(filename, folder):
 
    with open(folder) as info:
            data = info.read()
    
    feature_key = "Feature:"
    for item in data.split("\n"):
        if (feature_key in item):
            feature = item.replace(feature_key, "").strip().replace(" ", "")
            return feature  

def check_presence(feature, folder):
    
    case_filename = feature + "TestCase.swift"
    extension_filename = feature + ".swift"
    
    list_of_files = []
    for filename in os.listdir(folder):
        if filename.endswith(".swift"):
            list_of_files.append(filename)
    
    if case_filename and extension_filename in list_of_files:
        return True
    else:
        return False

def find_scenarios(filename, folder):
    
    with open(data_folder) as info:
            data = info.read()
            if ("@generated" in data): return
    
    outline_key = "Scenario Outline:"
    scenario_key = "Scenario:"
    manual_key = "@manual"
    scenario_number = 0
    scenarios = collections.OrderedDict()
    words = ["Given", "And", "Then", "When", "But"]
    skip = False
    data = data.split("\n")
    
    for i in range(len(data)):
        item = data[i]
        
        if (outline_key in item or scenario_key in item):
            if (manual_key in data[i-1]):
                skip = True
                continue
            else:
                skip = False
                scenario = item.strip()
                scenario_number += 1
                scenarios[scenario_number] = [scenario]
        
        if skip == False:
            if (item.strip().split(' ')[0] in words):
                scenarios[scenario_number].append(item.strip())
            
    return scenarios

def populate_io(title):
    
    now = datetime.datetime.now()
    date_format = now.strftime("%d/%m/%Y")
    
    output = io.StringIO()
    output.write("//\n")
    output.write("//  " + title + ".swift\n")
    output.write("//  BDD Tests\n")
    output.write("//\n")
    output.write("//  Created by Python Tool on " + date_format + ".\n")
    output.write("//  Copyright © 2018 Jaguar Land Rover. All rights reserved.\n")
    output.write("//\n\n")
    
    return output

def write_test_case(feature):
    
    imports = ["Foundation"]
    class_title = feature + "TestCase"
    extension_title = "ComfortControllerXCTestCase"
    override_funcs = ["setUp", "tearDown"]
    
    output = populate_io(class_title)
    
    for package in imports:
        output.write("import " + package + "\n")
    
    output.write("\n")
    output.write("@testable import Landrover_Comfort_Controller\n")
    output.write("class " + class_title + ": " + extension_title + " {\n\n")
    
    for func in override_funcs:
        output.write("\toverride func " + func + "() {\n")
        output.write("\t\tsuper." + func +"()\n")
        output.write("\t}\n\n")
    
    output.write("}\n\n")
    
    return output

def write_extension(feature, scenarios):
    
    imports = ["Foundation"]
    extension_title = feature
    
    output = populate_io(extension_title)
    
    for package in imports:
        output.write("import " + package + "\n")
    
    output.write("\n")
    output.write("@testable import Landrover_Comfort_Controller\n")
    output.write("extension " + extension_title + " {\n")
    
    outline_key = "Scenario Outline:"
    scenario_key = "Scenario:"
    
    for key in scenarios:
        output.write("\n")
        
        scenario = scenarios[key][0]
        
        if (outline_key in scenario):
            scenario = scenario.replace(outline_key, "").strip()
            name = "ScenarioOutline"
        else:
            if (scenario_key in scenario):
                scenario = scenario.replace(scenario_key, "").strip()
                name = "Scenario"
        
        split_scenario = scenario.split(" ")
        split_scenario = [x.capitalize() for x in split_scenario]
        func = "test" + "".join(split_scenario) + "()"
        
        output.write("\tfunc " + func + " {\n\n")
        output.write("\t\t" + name + "(\"" + scenario + "\") {\n" )
         
        for value in scenarios[key][1:]:
            val_type = value.split(' ')[0]
            val = value.replace(val_type, "").strip()
            output.write("\n\t\t\t" + val_type + "(\"" + val + "\")\n")
            
        output.write("\t\t}\n")
        output.write("\t}\n" )
    
    output.write("}\n\n")
    
    return output

def create_files(test, extension, feature_name, dest_path):
    
    test_file = feature_name + "TestCase.swift"
    extension_file = feature_name + ".swift"
    
    test_loc = os.path.join(dest_path, test_file)
    extension_loc = os.path.join(dest_path, extension_file)
    
    with open(test_loc, "w") as f:
        f.write(test.getvalue())
    
    with open(extension_loc, "w") as f:
        f.write(extension.getvalue())
    
if __name__ == '__main__':
    for filename in os.listdir(data_dir):
        if filename.endswith(".feature"):
            data_folder = os.path.join(data_dir, filename)
            feature_name = find_feature(filename, data_folder)
            exist = check_presence(feature_name, dest_folder)
            manual = check_manual(filename, data_folder)
            if exist or manual:
                pass
            else:
                scenarios = find_scenarios(filename, data_folder)
                test_output = write_test_case(feature_name)
                extension_output = write_extension(feature_name, scenarios)
                create_files(test_output, extension_output, feature_name, dest_folder)
    