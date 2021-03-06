import getopt

from bs4 import BeautifulSoup
import subprocess

import phraseappdiff
from apk_info import ApkInfo
import sys
import os.path


REPORT_PATH = ''
PACKAGE_NAME = ''
GITHUB_TOKEN = ''
REPO = ''
BRANCH_NAME = ''
PHRASEAPP_TOKEN = ''


def read_args(argv):
  global REPORT_PATH, PACKAGE_NAME, GITHUB_TOKEN, REPO, BRANCH_NAME, PHRASEAPP_TOKEN

  (opts, args) = getopt.getopt(argv, 'h:', [
    'report=',
    'package=',
    'githubtoken=',
    'repo=',
    'branch=',
    'phraseapptoken=',
  ])

  for (opt, arg) in opts:
    if opt == '--report':
      REPORT_PATH = arg
    elif opt == '--package':
      PACKAGE_NAME = arg
    elif opt == '--githubtoken':
      GITHUB_TOKEN = arg
    elif opt == '--repo':
      REPO = arg
    elif opt == '--branch':
      BRANCH_NAME = arg
    elif opt == '--phraseapptoken':
      PHRASEAPP_TOKEN = arg

  check_required_args(((REPORT_PATH, 'report'), (PACKAGE_NAME, 'package'),
                       (GITHUB_TOKEN, 'githubtoken'), (REPO, 'repo'),
                       (BRANCH_NAME, 'branch'), (PHRASEAPP_TOKEN, 'phraseapptoken')))


def check_required_args(arg_value_name_pairs):
  for pair in arg_value_name_pairs:
    if not pair[0]:
      print pair[1], 'is empty or invalid'
      sys.exit(1)


def get_soup(url):
  return BeautifulSoup(open(url), 'html.parser')


def add_header(text):
  file.write("\n\n<h2>" + text + "</h2>\n\n")


def write(text):
  file.write(text)


def runShell(command):
  return subprocess.Popen(
          command,
          shell=True,
          stdout=subprocess.PIPE
        ).stdout.read()

def generate_pr_info():
  commits = runShell('git log origin/master.. --oneline --pretty=%B')
  commits = commits.split('\n')

  write('<ul>')
  for commit in commits:
    if commit == '' :
      continue
    write('<li>' + commit + '</li>')
  write('</ul>')

def generate_lint_report():
  lint_report_path = REPORT_PATH + "/lint.html"
  if not os.path.isfile(lint_report_path):
    return

  soup = get_soup(lint_report_path)
  table = soup.find('table', attrs={'class': 'overview'})
  if table is None:
    return

  categories = table.find_all('td', attrs={'class': 'categoryColumn'})
  for category in categories:
    category.a.wrap(soup.new_tag('b'))
    category.a.insert_before(soup.new_tag('hr'))

  # This report is sent via email and it doesn't contain any css/img files, no image will be shown.
  # Therefore remove all images
  img_tags = table.find_all('img')
  for img in img_tags:
    text = img["alt"]
    img.insert_after('[{0}]'.format(str(text)))
    img.extract()

  # Remove links since they point to local address
  a_tags = table.find_all('a')
  for a in a_tags:
    a_content = a.string
    a.insert_after(str(a_content))
    a.extract()

  write(str(table))


def generate_checkstyle_report():
  checkstyle_report_path = REPORT_PATH + "/checkstyle.html"
  if not os.path.isfile(checkstyle_report_path):
    return

  soup = get_soup(checkstyle_report_path)

  table = soup.find('table', attrs={'class': 'log'})
  table.attrs = None

  write(str(table))


def generate_unit_tests():
  soup = get_soup(REPORT_PATH + "/unittests.html")

  # Add summary
  div_summary = soup.find('div', attrs={'id': 'summary'})
  write(str(div_summary))

  # Tabs are generated dynamically based on the status. For example: If there is no failure test
  # Failure tab won't be shown, therefore we need to dynamically fetch the classes tab which is
  # always the last tab
  tab_links = soup.find('ul', attrs={'class': 'tabLinks'}).find_all('li')
  last_tab = "tab" + str(len(tab_links) - 1)

  # Add test classes
  div_classes = soup.find('div', attrs={'id': last_tab})
  div_classes.h2.extract()

  tr_tags = div_classes.tbody.find_all('tr')
  for tr in tr_tags:
    td_tags = tr.find_all('td')

    # 0 : Empty column, we will replace it with name
    # 1 : Test count
    # 2 : Failure test count
    # 3 : Ignored test count
    # 4 : Duration in second
    # 5 : Status

    for index, item in enumerate(td_tags):
      # There is a bug in the generated report. An empty redundant column is generated.
      # We fix it by removing basically and add the class name as new column
      if index == 0:
        item.extract()

      # If the test class has failures, paint to red
      if index == 2:
        fail_count = float(item.string)
        if fail_count > 0:
          tr['bgcolor'] = "#ff9999"

      # If the test class has ignoring tests, paint to orange
      if index == 3:
        ignore_count = float(item.string)
        if ignore_count > 0:
          tr['bgcolor'] = "#ffeb99"

      # If the duration is longer than 1 second, paint to blue
      if index == 4:
        duration = float(item.string[:-1])
        if duration > 1:
          tr['bgcolor'] = "#ccccff"

  # There is a bug in generated test report html which is class names are not inside <td> tag
  # Remove the links and move them inside a td tag
  links = div_classes.find_all('a')
  for a in links:
    a.wrap(soup.new_tag('td'))
    a.insert_after(str(a.string))
    a.extract()

  write(str(div_classes))


def delete_column(index_to_remove, td_count, td_step, div_parent):
  deletedList = list()
  for i in range(index_to_remove, td_count, td_step):
      deletedList.append(i)

  td_tags = div_parent.find_all('td')
  for index, item in enumerate(td_tags):
      if index in deletedList:
          item.extract()


def generate_coverage_report():
  if not os.path.isfile(REPORT_PATH + "/coveragetests.html"):
      return

  print "Generating coverage test report"
  add_header("Coverage Report")
  soup = get_soup(REPORT_PATH + "/coveragetests.html")

  #get coverage table
  div_table = soup.find('table', attrs={'id': 'coveragetable'})
  div_table.extract()

  #style table headers
  head_tr_tags = div_table.thead.find_all('tr')
  for tr in head_tr_tags:
    head_td_tag = tr.find_all('td')
    for index, header in enumerate(head_td_tag):
        header.wrap(soup.new_tag('td',style="background-color:#E0E0E0; font-weight:bold; text-align: center; padding-right:20px"))
        header_title = str(header.string)
        if index == 2:
            header_title = "Instructions Cov."
        elif index == 4:
            header_title = "Branches Cov."

        header.insert_after(header_title)
        header.extract()

  # delete second row ("Missed Instructions")
  td_count = len(div_table.find_all('td'))
  td_step = len(div_table.thead.find_all('td'))
  delete_column(1, td_count, td_step,div_table)

  # delete foruth row ("Missed Branches")
  td_count = len(div_table.find_all('td'))
  td_step = len(div_table.thead.find_all('td'))
  delete_column(2, td_count, td_step,div_table)

  # remove any href links in the table
  links = div_table.find_all('a')
  for a in links:
    del a['href']

  write(str(div_table))


def apk_info_row(current, change, new, remaining):
  return "<td>Current: <b>" + str(current) + "</b></td>" + \
         "<td>Diff: <b>" + str(change) + "</b></td>" + \
         "<td>New: <b>" + str(new) + "</b></td>" + \
         "<td>Remaining: <b>" + str(remaining) + "</b></td>"


def generate_apk_info():
  print "Generating current APK info"
  # release apk (app-release.apk) is uploaded to AWS S3 ('bl-jenkins-artifacts' bucket) upon merge to master
  # and it is downloaded when building a PR (right before generating the build report)
  # see deployMaster() and 'generate build report' stage in Jenkinsfile of Android projects (pepper and salt)
  current_apk_info = ApkInfo.new_info(REPORT_PATH, PACKAGE_NAME)
  print "Generating new APK info"
  new_apk_info = ApkInfo.new_info('app/build/outputs/apk/release', PACKAGE_NAME)

  write("<table>")

  # Package name
  write("<tr><td><b>Package name</b></td><td><td colspan=4>" + new_apk_info.package_name + "</td></td></tr>")

  # Method count
  method_count_text = apk_info_row(
      current_apk_info.method_count,
      (new_apk_info.method_count - current_apk_info.method_count),
      new_apk_info.method_count,
      new_apk_info.remaining_method_count()
  )
  write("<tr><td><b>Method Count</b></td><td>" + method_count_text + "</td></tr>")

  # APK Size
  apk_size_text = apk_info_row(
      current_apk_info.apk_size_in_mb_formatted(),
      new_apk_info.apk_size_diff(current_apk_info),
      new_apk_info.apk_size_in_mb_formatted(),
      "-"
  )
  write("<tr><td><b>Apk Size (mb)</b></td><td>" + apk_size_text + "</td></tr>")

  # Min Sdk Version
  min_sdk_version = apk_info_row(current_apk_info.min_sdk_version, "-", new_apk_info.min_sdk_version, "-")
  write("<tr><td><b>Min Sdk Version</b></td><td>" + min_sdk_version + "</td></tr>")

  # Target Sdk Version
  target_sdk_version = apk_info_row(current_apk_info.target_sdk_version, "-", new_apk_info.target_sdk_version, "-")
  write("<tr><td><b>Target Sdk Version</b></td><td>" + target_sdk_version + "</td></tr>")

  # Permissions
  # Check what permission is added
  write("<tr><td><b>Permissions</b></td><td colspan='4'></td></tr>")
  permissions = current_apk_info.permissions_diff(new_apk_info)
  for permission in permissions:
    if permission.deleted:
      write("<tr><td></td><td colspan='4'><font color='red'>[REMOVED] " + permission.name + "</font></td></tr>")
    elif permission.new_added:
      write("<tr><td></td><td colspan='4'><font color='#01dc00'>[NEW] " + permission.name + "</font></td></tr>")
    else:
      write("<tr><td></td><td colspan='4'>" + permission.name + "</td></tr>")

  write("</table>")


def generate_localization_report():
  write(phraseappdiff.report_html(GITHUB_TOKEN, REPO, BRANCH_NAME, PHRASEAPP_TOKEN))


if __name__ == '__main__':
  read_args(sys.argv[1:])


with open(REPORT_PATH + '/build-report.html', 'w+') as file:
  print "Generating pull request info"
  write('<html lang="en"><head><meta charset="UTF-8"></head><body>')

  add_header("Pull Request Info")
  generate_pr_info()

  print "Generating APK info (release)"
  add_header("APK Info (release)")
  generate_apk_info()

  if PHRASEAPP_TOKEN is None:
    print "phrase app access token is not set"
  else:
    print "Generating localization report"
    add_header("Localisation Report")
    generate_localization_report()

  print "Generating lint report"
  add_header("Lint")
  generate_lint_report()

  print "Generating checkstyle report"
  add_header("Checkstyle")
  generate_checkstyle_report()

  print "Generating unit test report"
  add_header("Unit Tests")
  generate_unit_tests()

  generate_coverage_report()

  print "Build report is generated at " + REPORT_PATH + "/build-report.html"
  write('</body></html>')
