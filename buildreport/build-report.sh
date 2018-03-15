#!/bin/bash

PACKAGE_NAME=""
REPO_NAME=""
REPORT_PATH="report"

# Handle arguments
while [[ $# > 0 ]]; do
    key="$1"

    case $key in
        -h|--help)
            echo "build-report --package package --repo repo"
            exit 0
        ;;
        --package)
            shift
            readonly PACKAGE_NAME="$1"
        ;;
        --repo)
            shift
            readonly REPO_NAME="$1"
        ;;
        *)
            echo "Unknown option $1"
            exit 1
        ;;
    esac
    shift
done

# Validate arguments
if [[ -z ${PACKAGE_NAME} ]]; then
    echo "package is empty or invalid."
    exit 1
elif [[ -z ${REPO_NAME} ]]; then
    echo "repo is empty or invalid."
    exit 1
fi

rm -R "$REPORT_PATH/current/"
rm -R "$REPORT_PATH/new/"

mkdir "$REPORT_PATH"
mkdir "$REPORT_PATH/localization"
mkdir "$REPORT_PATH/current"
mkdir "$REPORT_PATH/new"

echo "Copy checkstyle report"
cp app/build/reports/checkstyle/checkstyle.html "$REPORT_PATH/checkstyle.html"

echo "Copy lint report"
cp app/build/reports/lint-results-debug.html "$REPORT_PATH/lint.html"

echo "Copy unit tests report"
cp app/build/reports/tests/testDebugUnitTest/index.html "$REPORT_PATH/unittests.html"

echo "Copy android instrumented test results"
cp android-test-log.txt "$REPORT_PATH/android-test-log.txt"

echo "Fetching build_report.py"
curl https://raw.githubusercontent.com/blacklane/zulu-scripts/master/buildreport/build_report.py -o "$REPORT_PATH/build_report.py"

echo "Fetching phraseappdiff.py"
curl https://raw.githubusercontent.com/blacklane/zulu-scripts/master/buildreport/phraseappdiff.py -o "$REPORT_PATH/phraseappdiff.py"

echo "Fetching apk_info.py"
curl https://raw.githubusercontent.com/blacklane/zulu-scripts/master/buildreport/apk_info.py -o "$REPORT_PATH/apk_info.py"


RELEASE_APK="app/build/outputs/apk/app-release.apk"
if [ ! -f $RELEASE_APK ]; then
    RELEASE_APK="app/build/outputs/apk/release/app-release.apk"
fi

# copy new apk
echo "Copying new apk"
cp $RELEASE_APK "$REPORT_PATH/new/app.apk"
echo "Unzipping new apk"
unzip "$REPORT_PATH/new/app.apk" -d "$REPORT_PATH/new" > "$REPORT_PATH/new/log.txt"

# build apk from master and fetch apk info
git checkout master
echo "Building current apk"
./gradlew clean assembleRelease > "$REPORT_PATH/current/log.txt"
echo "Copying current apk"
cp $RELEASE_APK "$REPORT_PATH/current/app.apk"
echo "Unzipping current apk"
unzip "$REPORT_PATH/current/app.apk" -d "$REPORT_PATH/current" >> "$REPORT_PATH/current/log.txt"

# go back to original branch before build report
git checkout -

echo "Building report"
python "$REPORT_PATH/build_report.py" --report=$REPORT_PATH --package=$PACKAGE_NAME --githubtoken=$GITHUB_TOKEN --repo=$REPO_NAME --branch=$BRANCH_NAME --phraseapptoken=$PHRASEAPP_TOKEN
