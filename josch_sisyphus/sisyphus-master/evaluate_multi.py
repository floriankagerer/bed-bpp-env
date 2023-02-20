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
import tempfile
import os

if len(sys.argv) != 3:
    print "usage:", sys.argv[0], "packlist.xml scoring.xml"
    exit(1)

libpallet = ctypes.cdll.LoadLibrary('./libpallet.so.0.0.0')
libpallet.evaluate.restype = ctypes.c_double

packlist = xmlfiletodict(sys.argv[1])

pallets = packlist['Response']['PackList']['PackPallets']['PackPallet']

article_lists = [ pallet['Packages']['Package'] for pallet in pallets ]

scores = list()
for pallet, articles_to_pack in zip(pallets, article_lists):
    partial_packlist = get_packlist_dict(pallet, articles_to_pack)
    tmp_fh, tmp = tempfile.mkstemp()
    tmp_order_fh, tmp_order = tempfile.mkstemp()
    dicttoxmlfile(partial_packlist, tmp)
    dicttoxmlfile(get_order_dict(pallet, articles_to_pack), tmp_order)
    scores.append(libpallet.evaluate(tmp_order, tmp, sys.argv[2]))
    os.close(tmp_fh)
    os.close(tmp_order_fh)
    os.remove(tmp)
    os.remove(tmp_order)
    #print tmp_order, tmp
print scores

print sum(scores)/len(scores)
