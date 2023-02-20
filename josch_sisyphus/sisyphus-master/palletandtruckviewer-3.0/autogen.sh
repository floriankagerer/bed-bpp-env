#!/bin/sh -x

aclocal && autoheader && automake --add-missing --copy && autoconf && exit 0

exit 0
