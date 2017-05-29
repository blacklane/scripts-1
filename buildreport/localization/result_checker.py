#!/usr/bin/python

import strings_resources_comparator
import urllib2
from urllib2 import Request
import json


class PhraseappError(Exception):
  def __init__(self, value):
    self.value = value

  def __str__(self):
    return repr(self.value)


def fail_if_not_all_keys_added_on_phraseapp(locale_keys, result, github_token, repo, branch_name):
  default_locale = locale_keys[0]
  diff = result[default_locale]
  keys_not_added_on_phraseapp = diff[strings_resources_comparator.STRINGS_ADDED_IN_FIRST_FILE]
  if len(keys_not_added_on_phraseapp) > 0:
    comment = _build_comment(keys_not_added_on_phraseapp)
    issue_url = _get_issue_url(github_token, repo, branch_name)
    _send_comment(github_token, issue_url, comment)
    raise PhraseappError(comment)


def _get_issue_url(token, repo, branch_name):
  url = "https://api.github.com/repos/blacklane/{0}/pulls?head=blacklane:{1}".format(repo, branch_name)
  print "Get PR info from github url : " + url

  pull_requests_result = urllib2.urlopen(
    Request(url, headers={"Authorization": "Basic " + token})
  )
  pull_requests_json = json.load(pull_requests_result)

  if type(pull_requests_json) is list and 'issue_url' in pull_requests_json[0]:
    return pull_requests_json[0]['issue_url']
  else:
    print "Can't find pull request for branch " + branch_name
    return None


def _send_comment(token, issue_url, comment):
  if issue_url is None:
    return

  url = issue_url + "/comments"
  body = '{{"body":"{0}"}}'.format(comment)

  print "Post comment : {0} Body : {1}".format(url, body)
  comment_result = urllib2.urlopen(
    Request(url, body, headers={"Authorization": "Basic " + token, "Content-Type": "application/json"})
  )

  if comment_result.getcode() == 201:
    print "Comment was successfully sent"
  else:
    print "Comment wasn't sent"


def _build_comment(keys_not_added_on_phraseapp):
  keys_str = ",\\n".join(keys_not_added_on_phraseapp)
  return "Add the following keys on PhraseApp:\\n" + keys_str
