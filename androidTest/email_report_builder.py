from bs4 import BeautifulSoup
import os


def get_soup(url):
    return BeautifulSoup(open(url), 'html.parser')


def add_header(text):
    file.write("\n\n<h2>" + text + "</h2>\n\n")
    file.write('<p>Here are the tests that failed: </p>')


def write(text):
    file.write(text)


def generate_table(report_path):
    failures = []

    soup = get_soup(report_path)

    for test in soup.find_all('td', attrs={'class': 'test fail'}):
        failures.append(test.find('a')['data-content'])

    for failure in failures:
        write("<p><li>" + failure + "</li><p>\n")


with open('email-report.html', 'w+') as file:
        add_header("Failed Tests")
        test_suite = ['Booking', 'Login', 'Registration', ]

        for test_class in test_suite:
            generate_table('results/' + test_class + 'Tests/debug/index.html')

        print "Failure report completed"

