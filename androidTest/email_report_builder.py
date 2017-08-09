from bs4 import BeautifulSoup
import os, re


def get_soup(url):
    return BeautifulSoup(open(url), 'html.parser')


def add_header(text, report_path):
    file.write("\n\n<h2>" + text + "</h2>\n\n")

    try:
        soup = get_soup(report_path)
        table = soup.find('div', attrs={'class': 'hero-unit'})
        stats = table.find_all('p')[0]
        file.write('<b>' + str(stats) + '</b>')

    except IOError e:
        write("<p>[warning]: " + report_path + " was found with no results.</p>\n")
        
    file.write('<p>Here are the tests that failed: </p>')



def write(text):
    file.write(text)

def parse_device(device_href):
    text = re.split('[/.]+', device_href)
    device_name = text[1]
    return device_name


def generate_table(report_path):
    failures = []

    try:
        soup = get_soup(report_path)
        
        for test in soup.find_all('td', attrs={'class': 'test fail'}):
            device_href = test.find('a')['href']
            device_name = parse_device(device_href)
            failures.append(test.find('a')['data-content'] + ' - ' + device_name)
            
    except IOError, e:
        write("<p>[warning]: " + report_path + " was found with no results.</p>\n")

    for failure in failures:
        write("<p><li>" + failure + "</li><p>\n")


with open('email-report.html', 'w+') as file:
        add_header("Failed Tests", 'results/spoon/debug/index.html' )
        generate_table('results/spoon/debug/index.html')

        print "Failure report completed"

