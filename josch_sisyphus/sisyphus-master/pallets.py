#!/usr/bin/env python
#
# Copyright 2012 Johannes 'josch' Schauer <j.schauer@email.de>
#
# This file is part of Sisyphus.
#
# Sisyphus is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Sisyphus is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sisyphus.  If not, see <http://www.gnu.org/licenses/>.

import sys
from util import xmlfiletodict, get_articles

def main():
    if len(sys.argv) != 2:
        print "usage:", sys.argv[0], "order.xml"
        exit(1)

    d = xmlfiletodict(sys.argv[1])

    pallets = d['Message']['PalletInit']['Pallets']['Pallet']

    if not isinstance(pallets, list):
        pallets = [pallets]

    for p in pallets:
        print "\t".join([
            p['Dimensions']['Length'],
            p['Dimensions']['Width'],
            p['Dimensions']['MaxLoadHeight'],
            p['Dimensions']['MaxLoadWeight']
            ])

if __name__ == "__main__":
    main()
