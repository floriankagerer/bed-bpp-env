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

import ctypes, sys
from util import xmlfiletodict, get_packlist_dict, dicttoxmlfile, get_order_dict
import os

if len(sys.argv) != 2:
    print "usage:", sys.argv[0], "packlist.xml"
    exit(1)

packlist = xmlfiletodict(sys.argv[1])

pallets = packlist['Response']['PackList']['PackPallets']['PackPallet']


if not isinstance(pallets, list):
    sys.stderr.write("this is not a multi-pallet packlist\n")
    exit(1)

article_lists = [ pallet['Packages']['Package'] for pallet in pallets ]

scores = list()
for i, (pallet, articles_to_pack) in enumerate(zip(pallets, article_lists)):
    partial_packlist = get_packlist_dict(pallet, articles_to_pack)
    dicttoxmlfile(partial_packlist, sys.argv[1]+"_"+str(i)+".xml")
    partial_order = get_order_dict(pallet, articles_to_pack)
    dicttoxmlfile(partial_order, sys.argv[1]+"_order_"+str(i)+".xml")
