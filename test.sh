#!/bin/bash

python manage.py test --testrunner "Net640.testing.runners.UnitTestRunner" -v 2
simpletests=$?
python manage.py test --testrunner "Net640.testing.runners.TransactionTestRunner" -v 2
transactiontests=$?
if [[ $simpletests -ne 0 || $transactiontests -ne 0 ]]
then
	echo -e "Unittests have failed"
	exit 1
else
	echo -e "Unittests were successful"
fi
