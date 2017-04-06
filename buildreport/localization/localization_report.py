#!/usr/bin/python

import os
from os import path
from os.path import splitext
import shutil
import strings_resources_comparator
import base64
import urllib2
from urllib2 import Request
import importlib


##
# Compares local strings files with files from Phraseapp.
# Compares the default locale string keys with other locales.
# Generates report.
#
# @param phraseapp_access_token An access token for Phraseapp
# @param project_id The id of a project on Phraseapp
# @param locale_keys A tuple which contains locale keys. These keys are used to find corresponding files in
#        "locale_ids_by_keys" and "string_files_by_keys" dictionaries. Also these keys are used in the report.
#        The first key is treated as the default locale key.
#        Example: ("en", "de", "fr")
#
# @param locale_ids_by_keys A dictionary which contains locale ids for Phraseapp grouped by locale_keys.
#                           Must contain all keys which locale_keys tuple contains.
#                           Example: {'en': 'en_id', 'de': 'de_id', 'fr': 'fr_id'}
#
# @param string_files_by_keys A dictionary which contains full paths to strings files in of the app
#                             grouped by locale_keys. Must contains all keys which locale_keys tuple contains.
#                             Example: {'en': '.../res/values/strings.xml', 'de': '.../res/values-de/strings.xml',
#                                       'fr': '.../res/values-fr/strings.xml'}
#
# @param report_generator_module The name of a module which generates report. Uses html_report_generator.py by default
#
# @return A string with the report formatted by report_generator_module.
def report(phraseapp_access_token, project_id, locale_keys,
           locale_ids_by_keys, string_files_by_keys, report_generator_module="localization.html_report_generator"):
  _check_parameters(phraseapp_access_token, project_id, locale_keys, locale_ids_by_keys, string_files_by_keys)

  _, extension = splitext(string_files_by_keys[locale_keys[0]])

  sandbox_path = _create_sandbox()
  result = {}
  for locale_key in locale_keys:
    locale_id = locale_ids_by_keys[locale_key]
    phraseapp_file_path = _pull_file_from_phraseapp(sandbox_path, phraseapp_access_token, project_id,
                                                    locale_id, locale_key, extension)
    diff = strings_resources_comparator.diff(string_files_by_keys[locale_key], phraseapp_file_path)
    result[locale_key] = diff

  shutil.rmtree(sandbox_path)

  default_locale_key = locale_keys[0]
  for locale_key in locale_keys[1:]:
    diff = strings_resources_comparator.diff(string_files_by_keys[default_locale_key], string_files_by_keys[locale_key])
    del diff[strings_resources_comparator.SAME_KEY_DIFFERENT_VALUES]
    result[default_locale_key + "-" + locale_key] = diff

  print str(result)

  return importlib.import_module(report_generator_module).generate_report(locale_keys, result)


# Checks parameters and raises an error if a parameter is wrong
def _check_parameters(phraseapp_access_token, project_id, locale_keys, locale_ids_by_keys, string_files_by_keys):
  if type(phraseapp_access_token) is not str:
    raise TypeError('Wrong type of "phraseapp_access_token" argument. Must be a string')
  if type(project_id) is not str:
    raise TypeError('Wrong type of "project_id" argument. Must be a string')
  if type(locale_keys) is not tuple:
    raise TypeError('Wrong type of "locale_keys" argument. Must be a tuple')
  if type(locale_ids_by_keys) is not dict:
    raise TypeError('Wrong type of "locale_ids_by_keys" argument. Must be a dictionary')
  if type(string_files_by_keys) is not dict:
    raise TypeError('Wrong type of "string_files_by_keys" argument. Must be a dictionary')

  if len(locale_keys) < 2:
    raise ValueError('"locale_keys" set must contains at least 2 items')

  for key in locale_keys:
    if key not in locale_ids_by_keys:
      raise ValueError('"locale_ids_by_keys" doesn\'t contain key ' + key +
                       '"locale_ids_by_keys" must contain the same set of keys as "locale_keys"')
    if key not in string_files_by_keys:
      raise ValueError('"string_files_by_keys" doesn\'t contain key ' + key +
                       '"string_files_by_keys" must contain the same set of keys as "locale_keys"')


##
# Creates a temporary working dir inside the current directory.
#
# @return The full path to the created dir.
def _create_sandbox():
  current_dir_path = path.dirname(path.realpath(__file__))
  sandbox_path = path.join(current_dir_path, "tmp")
  if not path.exists(sandbox_path):
    os.makedirs(sandbox_path)

  return sandbox_path


##
# Fetch locale data from Phraseapp and save it in a temporary file.
#
# @param sandbox A string with full path to the temporary working dir
# @param phraseapp_access_token An access token for Phraseapp
# @param project_id The id of a project on Phraseapp
# @param locale_id The id of a locale on Phraseapp
# @param locale_key A key (e.g "en" / "de" / "fr"). Is used to create a temporary dir for downloaded file.
# @param extension An extension of the file which will be created (".strings" or ".xml")
#
# @return The full path to the created file with loaded strings.
def _pull_file_from_phraseapp(sandbox, phraseapp_access_token, project_id, locale_id, locale_key, extension):
  url = "https://api.phraseapp.com/api/v2/projects/{0}/locales/{1}/download?" \
        "file_format={2}&include_empty_translations=true".format(project_id, locale_id, extension[1:])
  print "Pull strings from phraseapp url : " + url

  urlopen_output = urllib2.urlopen(
    Request(url, headers={"Authorization": "Basic " + base64.b64encode(phraseapp_access_token)})
  )

  output_dir = path.join(sandbox, locale_key)
  if not path.exists(output_dir):
    os.makedirs(output_dir)

  output_file_path = path.join(output_dir, "strings" + extension)
  with open(output_file_path, 'w+') as output_file:
    output_file.write(urlopen_output.read())

  return output_file_path
