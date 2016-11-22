from bs4 import BeautifulSoup
import os
import subprocess
import sys
import os.path

REPORT_PATH = sys.argv[1:][0]


def get_soup(url):
  return BeautifulSoup(open(url), 'html.parser')


def add_header(text):
  file.write("\n\n<h2>" + text + "</h2>\n\n")


def write(text):
  file.write(text)


def generate_functional_test_results(report_path):
  total_elapsed_time = subprocess.Popen(
    'grep "Time" '+ report_path +' ',
    shell=True,
    stdout=subprocess.PIPE
  ).stdout.read()
  write('<h4>' + total_elapsed_time + '</h4>')

  total_test_count = subprocess.Popen(
    'grep "OK (" '+ report_path +' ',
    shell=True,
    stdout=subprocess.PIPE
  ).stdout.read()
  write('<h4>' + total_test_count + '</h4>')

  tested_classes = subprocess.Popen(
    'sed -n "s/INSTRUMENTATION_STATUS: class=//gp" '+ report_path +' | uniq',
    shell=True,
    stdout=subprocess.PIPE
  ).stdout.read()
  tested_classes = tested_classes.split('\n')

  write('<ul>')
  for tested_class in tested_classes:
    if tested_class == '' :
      continue
    write('<li>' + tested_class + '</li>')
  write('</ul>')


with open(REPORT_PATH + '/build-acceptance-report.html', 'w+') as file:

  functional_tests_path=REPORT_PATH+"/android-test-log.txt"
  if os.path.isfile(functional_tests_path):
    print "Generating acceptance tests"
    add_header("Acceptance Tests")
    generate_functional_test_results(functional_tests_path)

  print "Build report is generated at " + REPORT_PATH + "/build-acceptance-report.html"