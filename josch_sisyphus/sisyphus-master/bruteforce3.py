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
import subprocess
import itertools
from util import dicttoxmlfile, get_packlist_dict, get_packlist_dict_multi, dicttoxmlstring, get_order_dict
from arrange_spread2 import arrange_in_layer
import cPickle
from binascii import a2b_base64
import tempfile
import os
import zlib
import fcntl
import ctypes
import random

libpallet = ctypes.cdll.LoadLibrary('palletandtruckviewer-3.0/.libs/libpallet.so.0.0.0')
libpallet.evaluate.restype = ctypes.c_double

if os.environ.get("multi_pallet"):
    try_multi_pallet = bool(int(os.environ["multi_pallet"]))
else:
    try_multi_pallet = False

if os.environ.get("permutations"):
    try_permutations = bool(int(os.environ["permutations"]))
else:
    try_permutations = True

if os.environ.get("iterations"):
    max_iter = int(os.environ["iterations"])
else:
    max_iter = -1

if os.environ.get("randomize"):
    try_random = bool(int(os.environ["randomize"]))
else:
    try_random = False

def pack_single_pallet(permut_layers, rest_layers, pallet):
    pack_sequence = 1
    pack_height = 0

    articles_to_pack = list()

    for layer in permut_layers+rest_layers:
        pack_height += layer[0]['Article']['Height']
        #if pack_height > pallet['Dimensions']['MaxLoadHeight']:
        #    break
        for article in layer:
            article['PackSequence'] = pack_sequence
            article['PlacePosition']['Z'] = pack_height
            articles_to_pack.append(article)
            pack_sequence += 1

    return get_packlist_dict(pallet, articles_to_pack)

def pack_multi_pallet(permut_layers, rest_layers, pallet):
    sum_all_article_height = sum([layer[0]['Article']['Height'] for layer in permut_layers+rest_layers])

    number_of_pallets = int(sum_all_article_height/pallet['Dimensions']['MaxLoadHeight'])+1

    article_lists = [ list() for i in range(number_of_pallets) ]
    pack_heights = [ 0 for i in range(number_of_pallets) ]
    pack_sequences = [ 1 for i in range(number_of_pallets) ]

    # spread over pallets in order
    for layer in permut_layers+rest_layers:
        # select as current, the pallet with the lowest height
        current_pallet = pack_heights.index(min(pack_heights))
        pack_heights[current_pallet] += layer[0]['Article']['Height']
        for article in layer:
            article['PackSequence'] = pack_sequences[current_pallet]
            article['PlacePosition']['Z'] = pack_heights[current_pallet]
            article_lists[current_pallet].append(article)
            pack_sequences[current_pallet] += 1

    return get_packlist_dict_multi(pallet, article_lists)

def evaluate_single_pallet(packlist):
    tmp_fh, tmp = tempfile.mkstemp()
    dicttoxmlfile(packlist, tmp)
    result = libpallet.evaluate(sys.argv[1], tmp, sys.argv[3])
    os.close(tmp_fh)
    os.remove(tmp)
    return result

def evaluate_multi_pallet(packlist):
    pallets = packlist['Response']['PackList']['PackPallets']['PackPallet']

    article_lists = [ pallet['Packages']['Package'] for pallet in pallets ]

    scores = list()
    for pallet, articles_to_pack in zip(pallets, article_lists):
        partial_packlist = get_packlist_dict(pallet, articles_to_pack)
        tmp_fh, tmp = tempfile.mkstemp()
        tmp_order_fh, tmp_order = tempfile.mkstemp()
        dicttoxmlfile(partial_packlist, tmp)
        dicttoxmlfile(get_order_dict(pallet, articles_to_pack), tmp_order)
        scores.append(libpallet.evaluate(tmp_order, tmp, sys.argv[3]))
        os.close(tmp_fh)
        os.close(tmp_order_fh)
        os.remove(tmp)
        os.remove(tmp_order)

    return sum(scores)/len(scores)

def evaluate_layers_rests(layers, rests, score_max, pallet, result_max):
    rest_layers = list()
    # sort rests by space they cover and move them to the center of the pile
    # append them to the layer list
    for rest in sorted(rests, key=lambda rest: sum([article['Article']['Length']*article['Article']['Width'] for article in rest]), reverse=True):
        plength, pwidth = (pallet['Dimensions']['Length'], pallet['Dimensions']['Width'])
        root, layer, rest = arrange_in_layer(rest, plength, pwidth)

        com_x = 0
        com_y = 0
        leftmost = pallet['Dimensions']['Length']
        rightmost = 0
        bottommost = pallet['Dimensions']['Width']
        topmost = 0
        for article in layer:
            com_x += article['PlacePosition']['X']
            com_y += article['PlacePosition']['Y']
            if article['PlacePosition']['X']-article['Article']['Length']/2 < leftmost:
                leftmost = article['PlacePosition']['X']-article['Article']['Length']/2
            if article['PlacePosition']['X']+article['Article']['Length']/2 > rightmost:
                rightmost = article['PlacePosition']['X']+article['Article']['Length']/2
            if article['PlacePosition']['Y']-article['Article']['Width']/2 < bottommost:
                bottommost = article['PlacePosition']['Y']-article['Article']['Width']/2
            if article['PlacePosition']['Y']+article['Article']['Width']/2 > topmost:
                topmost = article['PlacePosition']['Y']+article['Article']['Width']/2
        com_x, com_y = com_x/len(layer), com_y/len(layer)

        llength = rightmost - leftmost
        lwidth = topmost - bottommost

        if com_x < llength-plength/2:
            com_x = llength-plength/2
        elif com_x > plength/2:
            com_x = plength/2
        if com_y < lwidth-pwidth/2:
            com_y = lwidth-pwidth/2
        elif com_y > pwidth/2:
            com_y = pwidth/2

        diff_x, diff_y = plength*0.5-com_x, pwidth*0.5-com_y

        for article in layer:
            article['PlacePosition']['X'] += diff_x
            article['PlacePosition']['Y'] += diff_y

        rest_layers.append(layer)

    if try_permutations:
        permutations = itertools.permutations(layers)
    else:
        #permutations = [tuple(sorted(layers, key=lambda layer: sum([article['Article']['Weight'] for article in layer]), reverse=True))]
        #permutations = [tuple(sorted(layers, key=lambda layer: sum([article['Article']['Length']*article['Article']['Width'] for article in layer]), reverse=True))]
        #permutations = (layers for i in xrange(1000))
        permutations = [layers]

    i = 0
    for permut_layers in permutations:
        permut_layers = list(permut_layers)
        if try_random:
            random.shuffle(permut_layers)
        if try_multi_pallet:
            packlist = pack_multi_pallet(permut_layers, rest_layers, pallet)
            score = evaluate_multi_pallet(packlist)
        else:
            packlist = pack_single_pallet(permut_layers, rest_layers, pallet)
            score = evaluate_single_pallet(packlist)

        if score >= score_max[0]:
            result_max[0] = dicttoxmlstring(packlist)
            score_max[0] = score

        i+=1
        if max_iter != -1 and i >= max_iter:
            break

def main():
    if len(sys.argv) < 5:
        print "usage:", sys.argv[0], "order.xml packlist.xml scoring.xml LAYER [LAYER..]"
        exit(1)

    score_max = [0]
    result_max = [None]
    for arg in sys.argv[4:]:
        layers, rests, pallet = cPickle.loads(zlib.decompress(a2b_base64(arg)))
        evaluate_layers_rests(layers, rests, score_max, pallet, result_max)

    print score_max[0]

    lock = open("score_max.lock", "w")
    fcntl.lockf(lock, fcntl.LOCK_EX)
    if os.path.isfile("score_max"):
        with open("score_max", "r") as f:
            score_max_f = float(f.read())
    else:
        score_max_f = 0.0
    if score_max[0] > score_max_f:
        with open(sys.argv[2], "w+") as f:
            f.write(result_max[0])
        with open("score_max", "w+") as f:
            f.write(str(score_max[0]))
    lock.close()

if __name__ == "__main__":
    main()
