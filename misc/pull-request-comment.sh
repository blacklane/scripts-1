#!/bin/bash

GITHUB_TOKEN=""
REPO_NAME=""
COMMENT=""
BRANCH=""

# Handle arguments
while [[ $# > 0 ]]; do
    key="$1"

    case $key in
        -h|--help)
            echo "pull-request-comment --githubtoken githubtoken --repo repo --branch branch --comment comment"
            exit 0
        ;;
        --githubtoken)
            shift
            readonly GITHUB_TOKEN="$1"
        ;;
        --repo)
            shift
            readonly REPO_NAME="$1"
        ;;
        --branch)
            shift
            readonly BRANCH="$1"
        ;;
        --comment)
            shift
            readonly COMMENT="$1"
        ;;
        *)
            echo "Unknown option $1"
            exit 1
        ;;
    esac
    shift
done

if [[ -z ${REPO_NAME} ]]; then
    echo "repo is empty or invalid."
    exit 1
elif [[ -z ${BRANCH} ]]; then
    echo "branch is empty or invalid."
    exit 1    
elif [[ -z ${COMMENT} ]]; then
    echo "comment is empty or invalid."
    exit 1
fi

echo "Fetching pull_request_comment.py"
curl https://raw.githubusercontent.com/blacklane/zulu-scripts/master/misc/pull_request_comment.py -o "pull_request_comment.py"

echo "Sending comment"
python pull_request_comment.py --githubtoken=$GITHUB_TOKEN --repo=$REPO_NAME --branch=$BRANCH --comment=$COMMENT