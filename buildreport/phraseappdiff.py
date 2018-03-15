#!/usr/bin/python
import getopt
import importlib
import sys
import urllib2
from os import makedirs, environ
from os.path import realpath, exists, dirname, join
from shutil import rmtree, copy

import yaml  # pip install PyYAML

WORKING_DIR = realpath("phraseappdifftmp")

PHRASEAPP_CONFIG_PATH = None
OUTPUT_PATH = realpath(".")
PHRASEAPP_TOKEN = None
IS_STRICT = True

HELP_MESSAGE = """\
Creates an HTML file which contains all differences between phraseapp strings and string resources in your project

Usage: 
  ./phraseappdiff.py [options] <phraseapp-config-yml> [<output-dir>]
Options:
  -i  Path to the phraseapp yaml config
  -o  Path to the output directory
  --phraseapptoken=<token>  Phrase App access token. Optional if PHRASEAPP_ACCESS_TOKEN env variable is set up.
  --strict={true|false} Fail or not if there are strings which are added in the project but not added on Phrase App.
                        True by default.
"""

SCRIPTS_PATH = "https://raw.githubusercontent.com/blacklane/zulu-scripts/master/buildreport/localization"


def main(argv):
  _read_args(argv)

  result = ''
  try:
    result = report_html(None, None, None, PHRASEAPP_TOKEN, IS_STRICT)
  finally:
    with open(join(OUTPUT_PATH, "localization-report.html"), 'w+') as output:
      output.write(result)
    rmtree(WORKING_DIR)


def report_html(github_token, repo, branch_name, phraseapp_token, is_strict=True):
  _makedir_if_not_exists(WORKING_DIR)
  _makedir_if_not_exists(OUTPUT_PATH)

  project_id, locale_keys_tuple, phraseapp_locale_ids_dict, string_files_paths_dict = _parse_phraseapp_yaml()

  _load_localization_scripts()

  sys.path.insert(0, WORKING_DIR)
  localization_report_module = importlib.import_module("localization.localization_report")

  return localization_report_module.report(
    github_token, repo, branch_name, phraseapp_token,
    project_id,  # Phraseapp project id
    locale_keys_tuple,  # eg ("en", "de", "fr")
    phraseapp_locale_ids_dict,  # Phraseapp locale ids
    string_files_paths_dict,  # Paths to the resource files in the working dir
    is_strict=is_strict
  )


def _makedir_if_not_exists(path):
  if not exists(path):
    makedirs(path)


def _read_args(argv):
  global PHRASEAPP_CONFIG_PATH, OUTPUT_PATH, PHRASEAPP_TOKEN, IS_STRICT

  try:
    (opts, args) = getopt.gnu_getopt(argv, 'hi:o:', [
      'phraseapptoken=',
      'strict='
    ])
  except getopt.GetoptError:
    print HELP_MESSAGE
    sys.exit(1)

  if len(opts) > 0:
    for opt, arg in opts:
      if opt == '-h':
        print HELP_MESSAGE
        sys.exit()
      elif opt == '-i':
        PHRASEAPP_CONFIG_PATH = realpath(arg)
      elif opt == '-o':
        OUTPUT_PATH = realpath(arg)
      elif opt == '--phraseapptoken':
        PHRASEAPP_TOKEN = arg
      elif opt == '--strict':
        IS_STRICT = arg == 'true'
      else:
        print "Wrong option : " + HELP_MESSAGE

  if len(args) > 0:
    if PHRASEAPP_CONFIG_PATH is None:
      PHRASEAPP_CONFIG_PATH = realpath(args[0])
    else:
      OUTPUT_PATH = realpath(args[0])

  if len(args) > 1:
    OUTPUT_PATH = realpath(args[1])

  if PHRASEAPP_TOKEN is None:
    try:
      PHRASEAPP_TOKEN = environ["PHRASEAPP_ACCESS_TOKEN"]
    except KeyError:
      print "Add phraseapp access token with argument '--phraseapptoken=<token>' or " \
            "add it to the environment variables as PHRASEAPP_ACCESS_TOKEN"
      sys.exit(1)


def _parse_phraseapp_yaml():
  global PHRASEAPP_CONFIG_PATH

  if PHRASEAPP_CONFIG_PATH is None:
    if exists(realpath(".phraseapp.yml")):
      PHRASEAPP_CONFIG_PATH = realpath(".phraseapp.yml")
    else:
      print "Error: phraseapp config path isn't specified"
      sys.exit(1)

  # The root project directory where the phraseapp.yml placed
  project_dir = dirname(PHRASEAPP_CONFIG_PATH)

  with open(PHRASEAPP_CONFIG_PATH, 'r') as stream:
    loaded_yaml = yaml.load(stream)
    project_id = loaded_yaml["phraseapp"]["project_id"]
    pull_targets = loaded_yaml["phraseapp"]["pull"]["targets"]

    locale_keys = []
    phraseapp_locale_ids_dict = {}
    string_files_paths_dict = {}
    for target in pull_targets:
      target_file = target["file"]
      locale_key, is_default = _get_localization_key(target_file)
      locale_keys.append(locale_key)
      phraseapp_locale_ids_dict[locale_key] = target["params"]["locale_id"]

      # Copy the project resource file to the working directory to parse it later
      locale_postfix = "" if is_default else "-" + locale_key  # Default locale directory doesn't have postfix
      path = join(WORKING_DIR, "strings{0}.xml".format(locale_postfix))
      copy(join(project_dir, target_file), path)
      string_files_paths_dict[locale_key] = path  # Save the file path by locale key

    locale_keys_tuple = tuple(locale_keys)
    print "project_id = {0}".format(project_id)
    print "locale keys = {0}".format(locale_keys_tuple)
    print "phraseapp locales ids = {0}".format(phraseapp_locale_ids_dict)
    print "string files paths = {0}".format(string_files_paths_dict)

    return project_id, locale_keys_tuple, phraseapp_locale_ids_dict, string_files_paths_dict


def _get_localization_key(file_path):
  dash_index = file_path.find("-")
  if dash_index > 0:
    slash_index = file_path.find("/", dash_index)
    return file_path[dash_index + 1:slash_index], False
  else:
    return "en", True


def _load_localization_scripts():
  scripts_dir = join(WORKING_DIR, "localization")
  _makedir_if_not_exists(scripts_dir)

  _load_file("{0}/__init__.py".format(SCRIPTS_PATH), join(scripts_dir, "__init__.py"))
  _load_file(
    "{0}/strings_resources_comparator.py".format(SCRIPTS_PATH), join(scripts_dir, "strings_resources_comparator.py")
  )
  _load_file("{0}/localization_report.py".format(SCRIPTS_PATH), join(scripts_dir, "localization_report.py"))
  _load_file("{0}/result_checker.py".format(SCRIPTS_PATH), join(scripts_dir, "result_checker.py"))
  _load_file("{0}/html_report_generator.py".format(SCRIPTS_PATH), join(scripts_dir, "html_report_generator.py"))


def _load_file(url, output_file_path):
  urlopen_output = urllib2.urlopen(url)
  with open(output_file_path, 'w+') as output_file:
    output_file.write(urlopen_output.read())


if __name__ == '__main__':
  main(sys.argv[1:])
