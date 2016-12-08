#!/bin/sh
date +%b-%dT%H.%M > timestamp.out

timestamp="$(cat timestamp.out)"
result_folder=results
destdir="$result_folder/Results-$timestamp"

mkdir -p "$destdir"
echo "Directory created: ${destdir##*/}"

echo "Starting Booking Tests"
./gradlew spoon -PspoonClassName=com.blacklane.passenger.test.acceptance.BookingTests
cp -r app/build/spoon "$destdir"/BookingTests
echo "Results saved to BookingTests folder"

echo "Starting Registration Tests"
./gradlew spoon -PspoonClassName=com.blacklane.passenger.test.acceptance.RegistrationTests
cp -r app/build/spoon "$destdir"/RegistrationTests
echo "Results saved to RegistrationTests folder"

echo "Starting Login Tests"
./gradlew spoon -PspoonClassName=com.blacklane.passenger.test.acceptance.LoginTests
cp -r app/build/spoon "$destdir"/LoginTests
echo "Results saved to LoginTests folder"

echo "Starting Rides Tests"
./gradlew spoon -PspoonClassName=com.blacklane.passenger.test.acceptance.RidesTests
cp -r app/build/spoon "$destdir"/RidesTests
echo "Results saved to RidesTests folder"

echo "Starting Profile Tests"
./gradlew spoon -PspoonClassName=com.blacklane.passenger.test.acceptance.ProfileTests
cp -r app/build/spoon "$destdir"/ProfileTests
echo "Results saved to ProfileTests folder"

echo "Starting Manage Payments Tests"
./gradlew spoon -PspoonClassName=com.blacklane.passenger.test.acceptance.ManagePaymentsTests
cp -r app/build/spoon "$destdir"/ManagePaymentsTests
echo "Results saved to ManagePaymentsTests folder"

echo "Starting Forgot Password Tests"
./gradlew spoon -PspoonClassName=com.blacklane.passenger.test.acceptance.ForgotPasswordTests
cp -r app/build/spoon "$destdir"/ForgotPasswordTests
echo "Results saved to ForgotPasswordTests folder"


