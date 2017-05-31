#!/usr/bin/python
import codecs
import xml.etree.ElementTree as ElementTree
import re
from os.path import splitext

STRINGS_ADDED_IN_FIRST_FILE = "STRINGS_ADDED_IN_FIRST_FILE"
STRINGS_ADDED_IN_SECOND_FILE = "STRINGS_ADDED_IN_SECOND_FILE"
SAME_KEY_DIFFERENT_VALUES = "SAME_KEY_DIFFERENT_VALUES"


##
# Finds differences in two string resources files.
# Can handle android's string.xml files and ios' Localizable.strings files
#
# @param first_file_path A full path to the first .xml or .strings file
# @param second_file_path A full path to the second .xml or .strings file
#
# @return A dictionary which contains three entries with keys:
#         STRINGS_ADDED_IN_FIRST_FILE, STRINGS_ADDED_IN_SECOND_FILE, SAME_KEY_DIFFERENT_VALUES.
#         The value under the key "STRINGS_ADDED_IN_FIRST_FILE" is the dictionary name-string pairs,
#           which are contained in the first file, but are not contained in the second.
#           Can be empty.
#         The value under the key "STRINGS_ADDED_IN_SECOND_FILE" is the dictionary name-string pairs,
#           which are contained in the second file, but are not contained in the first.
#           Can be empty.
#         The value under the key "SAME_KEY_DIFFERENT_VALUES" is the dictionary name-tuple(string, string) pairs
#           which are contained in both files but with different values. The first item of the tuple is the string value
#           from the first file, the second item is the string value from the second file.
#           Can be empty.
#
# Example:
# first.xml :
#    <resources>
#      <string name="added_in_first_name">Added in first</string>
#      <string name="added_in_both_name">Added in both</string>
#      <string name="different_values_name">Value 1</string>
#    </resources>
# second.xml :
#    <resources>
#      <string name="added_in_second_name">Added in second</string>
#      <string name="added_in_both_name">Added in both</string>
#      <string name="different_values_name">Value 2</string>
#    </resources>
#
# result of diff(first.xml, second.xml):
#    {
#      'STRINGS_ADDED_IN_FIRST_FILE': {'added_in_first_name': 'Added in first'}
#      'STRINGS_ADDED_IN_SECOND_FILE': {'added_in_second_name': 'Added in second'},
#      'SAME_KEY_DIFFERENT_VALUES': {'different_values_name': ('Value 1', 'Value 2')},
#    }
#
def diff(first_file_path, second_file_path):
  first_strings_dict = _read_file(first_file_path)
  second_strings_dict = _read_file(second_file_path)

  # If strings dictionaries are equal return empty results
  if cmp(first_strings_dict, second_file_path) == 0:
    return {STRINGS_ADDED_IN_FIRST_FILE: {}, STRINGS_ADDED_IN_SECOND_FILE: {}, SAME_KEY_DIFFERENT_VALUES: {}}

  strings_added_in_first_file = _find_entries_which_are_not_in_second_dict(first_strings_dict, second_strings_dict)

  strings_added_in_second_file = _find_entries_which_are_not_in_second_dict(second_strings_dict, first_strings_dict)

  # Find strings with the same names but with different values
  same_key_different_values = {}
  for entry in first_strings_dict.items():
    key = entry[0]
    value = entry[1]
    if key in second_strings_dict and not second_strings_dict[key] == value:
      same_key_different_values[key] = (value, second_strings_dict[key])

  return {STRINGS_ADDED_IN_FIRST_FILE: strings_added_in_first_file,
          STRINGS_ADDED_IN_SECOND_FILE: strings_added_in_second_file,
          SAME_KEY_DIFFERENT_VALUES: same_key_different_values}


##
# Parses a document with string resources into a dictionary with name as a key.
#
# @param path A path to a file
#
# @return A dictionary with strings' names as keys and strings' values as values
def _read_file(path):
  _, extension = splitext(path)

  if extension not in (".xml", ".strings"):
    raise IOError("File extension must be .xml or .strings. The current is : " + extension)

  return _read_xml(path) if extension == ".xml" else _read_ios_strings(path)


##
# Parses an string.xml document into a dictionary with name as a key.
#
# @param path A path to a string.xml file
#
# @return A dictionary with strings' names as keys and strings' values as values
def _read_xml(path):
  tree = ElementTree.parse(path)
  resources = tree.getroot()
  # Root element is <resources>
  if not resources.tag == "resources":
    raise IOError("Root tag must be <resources>. The current is : " + resources.tag)

  strings_dict = {}
  for child in resources:
    if child.tag == "string" and child.text:  # Don't save empty strings
      if "name" in child.attrib:
        strings_dict[child.attrib["name"]] = child.text  # Put a string resource to the name-value dictionary
      else:
        raise IOError("string doesn't contain name attribute. attrib = " + str(child.attrib))

  return strings_dict


##
# Parses an localizable.strings document into a dictionary with name as a key.
#
# @param path A path to a localizable.strings file
#
# @return A dictionary with strings' names as keys and strings' values as values
def _read_ios_strings(path):
  strings_dict = {}
  with codecs.open(path, 'r', encoding='utf-16') as strings_file:
    for line in strings_file:
      line = line.strip()
      if len(line) != 0 and line.find('"') == 0:
        key = _find_first_match('"(?:[^\\"]|\\.)*"(?=\s*=)', line, "Can't find string's key in line : " + line)
        value = _find_first_match('"(?:[^\\"]|\\.)*"(?=;)', line, "Can't find string's value in line : " + line)

        # We parse strings with double quotes. Remove them
        key = key[1:len(key) - 1]
        value = value[1:len(value) - 1]
        if len(key) > 0 and len(value) > 0:
          strings_dict[key] = value

  return strings_dict


def _find_first_match(pattern, string, error_message):
  matches = re.findall(pattern, string)
  if len(matches) == 0:
    raise IOError(error_message)
  else:
    return matches[0]


##
# Finds all entries which the first dictionary contains but the second dictionary doesn't contain
#
# @param first_dict A dictionary which contains entries to check
# @param second_dict A dictionary which is checked for containing the entries of the first dictionary
#
# @return A dictionary with entries which the first dictionary contains but the second dictionary doesn't contain
def _find_entries_which_are_not_in_second_dict(first_dict, second_dict):
  result = {}
  for entry in first_dict.items():
    key = entry[0]
    value = entry[1]
    if key not in second_dict:
      result[key] = value

  return result
