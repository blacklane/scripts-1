#!/bin/bash

PACKAGE_NAME=$1
REPORT_PATH="report"

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

echo "Fetching apk_info.py"
curl https://raw.githubusercontent.com/blacklane/zulu-scripts/master/buildreport/apk_info.py -o "$REPORT_PATH/apk_info.py"

echo "Fetching localization report scripts"
curl https://raw.githubusercontent.com/blacklane/zulu-scripts/master/buildreport/localization/__init__.py -o "$REPORT_PATH/localization/__init__.py"
curl https://raw.githubusercontent.com/blacklane/zulu-scripts/master/buildreport/localization/strings_resources_comparator.py -o "$REPORT_PATH/localization/strings_resources_comparator.py"
curl https://raw.githubusercontent.com/blacklane/zulu-scripts/master/buildreport/localization/localization_report.py -o "$REPORT_PATH/localization/localization_report.py"
curl https://raw.githubusercontent.com/blacklane/zulu-scripts/master/buildreport/localization/html_report_generator.py -o "$REPORT_PATH/localization/html_report_generator.py"


# copy strings resources
mkdir "$REPORT_PATH/localization/values"
mkdir "$REPORT_PATH/localization/values-de"
mkdir "$REPORT_PATH/localization/values-fr"
cp "app/src/main/res/values/strings.xml" "$REPORT_PATH/localization/values/strings.xml"
cp "app/src/main/res/values-de/strings.xml" "$REPORT_PATH/localization/values-de/strings.xml"
cp "app/src/main/res/values-fr/strings.xml" "$REPORT_PATH/localization/values-fr/strings.xml"

# copy new apk
echo "Copying new apk"
cp "app/build/outputs/apk/app-release.apk" "$REPORT_PATH/new/app.apk"
echo "Unzipping new apk"
unzip "$REPORT_PATH/new/app.apk" -d "$REPORT_PATH/new" > "$REPORT_PATH/new/log.txt"

# build apk from master and fetch apk info
git checkout master
echo "Building current apk"
./gradlew clean assembleRelease > "$REPORT_PATH/current/log.txt"
echo "Copying current apk"
cp "app/build/outputs/apk/app-release.apk" "$REPORT_PATH/current/app.apk"
echo "Unzipping current apk"
unzip "$REPORT_PATH/current/app.apk" -d "$REPORT_PATH/current" >> "$REPORT_PATH/current/log.txt"

# go back to original branch before build report
git checkout -

echo "Building report"
python "$REPORT_PATH/build_report.py" $REPORT_PATH $PACKAGE_NAME $PHRASEAPP_TOKEN
