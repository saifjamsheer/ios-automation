#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 25 11:26:32 2018

@author: Saif
"""

import logging
from colorlog import ColoredFormatter
import os.path
import collections
from collections import defaultdict
import argparse
from lxml import etree
import re
from pyfiglet import Figlet
from termcolor import cprint

XML_TITLE = "strings.xml"

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

f1 = Figlet(font='ogre')
f2 = Figlet(font='digital')

logger = logging.getLogger("Android XML Tool")
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)

#format_str = '%(asctime)s - %(name)s - [%(levelname)s]: %(message)s'
formatter = ColoredFormatter(
        '%(yellow)s%(asctime)s%(reset)s - %(name)s - %(log_color)s[%(levelname)s]%(reset)s: %(message)s',
        reset = True,
        log_colors = {
                'DEBUG': 'blue',
                'INFO': 'cyan',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red'
        }
)
        

handler.setFormatter(formatter)
logger.addHandler(handler)

parser = argparse.ArgumentParser(prog="Android XML Tool",
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 description="This tool has been created to automate "
                                 "the process of formatting a text file to an xml layout. "
                                 "The tool checks each line in the text file for any potential "
                                 "errors and if there are none, a strings.xml file can be "
                                 "populated with the strings (formatted correctly) - the tool "
                                 "will then automatically overwrite any preexisting string.xml "
                                 "file. In the case of one or more errors, the user will be "
                                 "informed of these errors and the lines they are located in.")

group = parser.add_mutually_exclusive_group()

group.add_argument("-c", "--check", action="store_true", 
                   help="Checks text file for any formatting errors.")
group.add_argument("-f", "--format", action="store_true", 
                   help="Formats and constructs a strings.xml if no errors are located.")

parser.add_argument("text_file_name", type=str, 
                    help="Text file name to be checked/formatted.")
parser.add_argument("source_path", type=str, 
                    help="Directory of text file.")
parser.add_argument("dest_path", type=str, 
                    help="Output file (strings.xml) to be stored in this directory.")

print(f1.renderText('strings tool\n'))
print("------------------------------------------------------------------------")

def main(args):
    if args.check:
        cprint(f2.renderText('CHECKING TEXT FILE\n'), "yellow")
        string_checker(args.text_file_name, args.source_path)
    elif args.format:
        cprint(f2.renderText('ATTEMPTING TO CONSTRUCT XML\n'), "cyan")
        xml_formatter(args.text_file_name, args.source_path, args.dest_path)
    else:
        logger.warning("Passed argument is invalid.")

def string_checker(filename, source_path):
    
    data_folder = os.path.join(source_path, filename)
    file = open(data_folder)
    
    pattern = re.compile("^\"[a-z0-9_]*\" \= \"\S.+?\S(?=\")\"\;")
    
    incorrect_lines = list()
    lines_to_delete = list()
    
    for num, line in enumerate(file, 1):
        line = line.rstrip()
        end_index = line.find('";')
        try:
            line[end_index+2]
            incorrect_lines.append('[Line %s]: %s' %(num, line))
            lines_to_delete.append(line)
        except IndexError:
            if not (pattern.match(line)):
                if not (len(line.strip()) == 0):
                    incorrect_lines.append('[%s]: %s' %(num, line))
                    lines_to_delete.append(line)
    
    with open(data_folder) as info:
        data = info.read()
        
    split_data = data.split("\n")
    split_data = list(filter(None, split_data))
    
    for line in lines_to_delete:
        split_data.remove(line)
    
    strings = collections.OrderedDict()
    duplicates = defaultdict(list)
    for item in split_data:
        key_and_value = item.split("=")
        key = key_and_value[0].strip().replace('"','')
        if key in strings.keys():
            duplicates = find_duplicates(data, lines_to_delete)
            break
        value = key_and_value[1].strip().replace('"','')
        strings[key] = value
    
    if len(incorrect_lines) == 0 and len(duplicates) == 0:
        print('')
        cprint(f2.renderText('NO ERRORS'), "green")
        print("------------------------------------------------------------------------")
        return strings
    else:
        print('')
        cprint(f2.renderText('ERROR(S) LOCATED'), "red")
        if len(incorrect_lines) > 0:
            logger.error("One or more lines is formatted incorrectly.")
            for line in incorrect_lines:
                logger.info(line)
            
        if len(duplicates) > 0:
            logger.error("One or more duplicate keys exists.")
            for key in duplicates:
                value_str = str(duplicates[key]).replace('[','').replace(']','')
                logger.info("Key: " + color.PURPLE + "["+ key + "]" + color.END + " - Value Instances: " + value_str)
        
        print("------------------------------------------------------------------------")
        return dict()
            
def xml_formatter(filename, source_path, dest_path):
    
    string_dict = string_checker(filename, source_path)
    
    if len(string_dict) == 0:
        logger.critical("Please fix all errors before passing in this argument.")
        return
    
    resources = etree.Element("resources")
    code = "string"
    
    for key, value in string_dict.items():
        etree.SubElement(resources, code, name=key).text = value
    
    tree = etree.tostring(resources, pretty_print=True, xml_declaration=True, encoding='UTF-8')
    
    file_loc = os.path.join(dest_path, XML_TITLE)
    with open(file_loc, "wb") as f:
        f.write(tree)
        print('')
        print(f2.renderText('SUCCESSFULLY CREATED FILE'))
        print("------------------------------------------------------------------------\n")
        
    
def find_duplicates(data, lines):
    
    data = data.split("\n")
    
    key_values = defaultdict(list)
    
    for index, string in enumerate(data):
        
        if string:
            if string not in lines:
                key_and_value = string.split("=")
                key = key_and_value[0].strip().replace('"','')
                value = ["{Line: " + str(index+1) + "}", key_and_value[1].strip().replace('"','')]
                key_values[key].append(value)
        
    for key in list(key_values):
                    if len(key_values[key]) <= 1: 
                        key_values.pop(key)
                        
    return key_values
            
if __name__ == '__main__':
    arguments = parser.parse_args()
    main(arguments)      


# Saifs-MBP:PythonFiles Saif$ python xmltool.py -f "copy_doc.txt" 
# "/Users/saif/Desktop/ProjectsGit/JLRCCAndroid-Redev/JLRCCCommon-Redev/copy" 
# "/Users/saif/Desktop/PythonFiles"
        
