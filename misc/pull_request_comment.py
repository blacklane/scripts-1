
GITHUB_TOKEN = ''
REPO = ''
BRANCH_NAME = ''
COMMENT = ''


def read_args(argv):
    global GITHUB_TOKEN, REPO, BRANCH_NAME, COMMENT

    (opts, args) = getopt.getopt(argv, 'h:', [
        'githubtoken=',
        'repo=',
        'branch=',
        'comment='
    ])
  
    for (opt, arg) in opts:
        elif opt == '--githubtoken':
        GITHUB_TOKEN = arg
        elif opt == '--repo':
        REPO = arg
        elif opt == '--branch':
        BRANCH_NAME = arg
        elif opt == '--comment':
        COMMENT = arg

    check_required_args(((GITHUB_TOKEN, 'githubtoken'), (REPO, 'repo'),
                         (BRANCH_NAME, 'branch'), (COMMENT, 'comment')))


def check_required_args(arg_value_name_pairs):
  for pair in arg_value_name_pairs:
    if not pair[0]:
      print pair[1], 'is empty or invalid'
      sys.exit(1)


def get_issue_url(github_token, repo, branch_name):
  if github_token is None:
    print "WARNING: Can't post githib comment. Github token is not provided"
  if repo is None:
    print "WARNING: Can't post githib comment. Repository name is not provided"
  if branch_name is None:
    print "WARNING: Can't post githib comment. Branch name is not provided"
  if github_token is None or repo is None or branch_name is None:
    return None

  url = "https://api.github.com/repos/blacklane/{0}/pulls?head=blacklane:{1}".format(
      repo, branch_name)
  print "Get PR info from github url : " + url

  pull_requests_result = urllib2.urlopen(
      Request(url, headers={"Authorization": "token " + github_token})
  )
  pull_requests_json = json.load(pull_requests_result)

  if type(pull_requests_json) is list and 'issue_url' in pull_requests_json[0]:
    return pull_requests_json[0]['issue_url']
  else:
    print "Can't find pull request for branch " + branch_name
    return None


def send_comment(github_token, issue_url, comment):
  if issue_url is None:
    return

  url = issue_url + "/comments"
  body = '{{"body":"{0}"}}'.format(comment)

  print "Post comment : {0} Body : {1}".format(url, body)
  comment_result = urllib2.urlopen(
      Request(url, body, headers={
              "Authorization": "token " + github_token, "Content-Type": "application/json"})
  )

  if comment_result.getcode() == 201:
    print "Comment was successfully sent"
  else:
    print "Comment wasn't sent"


def submit_comment(github_token, repo, branch_name, comment):
    issue_url = get_issue_url(github_token, repo, branch_name)
    send_comment(github_token, issue_url, comment)


if __name__ == '__main__':
  read_args(sys.argv[1:])


submit_comment(GITHUB_TOKEN, REPO, BRANCH_NAME, COMMENT)
