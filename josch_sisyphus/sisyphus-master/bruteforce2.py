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
import itertools
from util import xmlfiletodict, get_pallet, get_articles, product_varlength, starmap
from arrange_spread2 import arrange_in_layer, spread_articles
import cPickle
from binascii import b2a_base64
import zlib
import os
import random

def rotate(node):
    if node is None:
        return

    if node['article']:
        # exchange x and y coordinate
        node['article']['PlacePosition']['X'], node['article']['PlacePosition']['Y'] = node['article']['PlacePosition']['Y'], node['article']['PlacePosition']['X']
        # rotate article
        node['article']['Orientation'] = node['article']['Orientation']%2+1

    rotate(node['right'])
    rotate(node['down'])

def get_layers(bins, pallet, rot_article=False, rot_pallet=False):
    for abin in bins:
        bins[abin] = sorted(bins[abin], key=lambda article: article['Article']['Length']*article['Article']['Width'], reverse=True)
        plength, pwidth = (pallet['Dimensions']['Length'], pallet['Dimensions']['Width'])
        if rot_pallet:
            root, layer, rest = arrange_in_layer(bins[abin], pwidth, plength, rot_article=rot_article)
        else:
            root, layer, rest = arrange_in_layer(bins[abin], plength, pwidth, rot_article=rot_article)
        while layer:
            spread_articles(root)
            if rot_pallet:
                rotate(root)

            occupied_area = 0
            for article in layer:
                length, width = article['Article']['Length'], article['Article']['Width']
                occupied_area += length*width

            # print "layer occupation:", occupied_area/float(plength*pwidth)
            if occupied_area/float(plength*pwidth) <= 0.7:
                rot_article, rot_pallet = (yield None, layer)
            else:
                rot_article, rot_pallet = (yield layer, None)

            if rot_pallet:
                root, layer, rest = arrange_in_layer(rest, pwidth, plength, rot_article=rot_article)
            else:
                root, layer, rest = arrange_in_layer(rest, plength, pwidth, rot_article=rot_article)

def get_bit(num, pos):
    return num>>pos&1

def get_bitmask(num, length):
    return tuple(( bool(num>>pos&1) for pos in xrange(length-1,-1,-1) ))

def main():
    if len(sys.argv) != 2:
        print "usage:", sys.argv[0], "order.xml"
        exit(1)

    orderline = xmlfiletodict(sys.argv[1])
    pallet = get_pallet(orderline)
    articles = get_articles(orderline)
    bins = dict()

    for article in articles:
        abin = bins.get(article['Article']['Height'])
        if abin:
            abin.append(article)
        else:
            bins[article['Article']['Height']] = [article]

    if os.environ.get("rot_article"):
        try_rot_article = bool(int(os.environ["rot_article"]))
    else:
        try_rot_article = True

    if os.environ.get("rot_pallet"):
        try_rot_pallet = bool(int(os.environ["rot_pallet"]))
    else:
        try_rot_pallet = True

    if os.environ.get("rot_article_default"):
        rot_article_default = bool(int(os.environ["rot_article_default"]))
    else:
        rot_article_default = False

    if os.environ.get("rot_pallet_default"):
        rot_pallet_default = bool(int(os.environ["rot_pallet_default"]))
    else:
        rot_pallet_default = False

    if os.environ.get("iterations"):
        max_iter = int(os.environ["iterations"])
    else:
        max_iter = -1

    if os.environ.get("randomize"):
        try_random = bool(int(os.environ["randomize"]))
    else:
        try_random = False

    if try_rot_article and try_rot_pallet:
        if try_random:
            product_it = starmap(random.randint, itertools.repeat((0,3)))
        else:
            product_it = product_varlength(4)
    elif try_rot_article or try_rot_pallet:
        if try_random:
            product_it = starmap(random.randint, itertools.repeat((0,1)))
        else:
            product_it = product_varlength(2)

    i = 0
    while True:
        rests = list()
        layers = list()
        try:
            if try_rot_article and try_rot_pallet:
                rot_article, rot_pallet = get_bitmask(product_it.send(True), 2)
            elif try_rot_article and not try_rot_pallet:
                rot_article = get_bitmask(product_it.send(True), 1)[0]
                rot_pallet = rot_pallet_default
            elif not try_rot_article and try_rot_pallet:
                rot_article = rot_article_default
                rot_pallet = get_bitmask(product_it.send(True), 1)[0]
            else:
                rot_article = rot_article_default
                rot_pallet = rot_pallet_default
        except TypeError:
            if try_rot_article and try_rot_pallet:
                rot_article, rot_pallet = get_bitmask(product_it.next(), 2)
            elif try_rot_article and not try_rot_pallet:
                rot_article = get_bitmask(product_it.next(), 1)[0]
                rot_pallet = rot_pallet_default
            elif not try_rot_article and try_rot_pallet:
                rot_article = rot_article_default
                rot_pallet = get_bitmask(product_it.next(), 1)[0]
            else:
                rot_article = rot_article_default
                rot_pallet = rot_pallet_default
        except StopIteration:
            break # generator empty
        it = get_layers(bins, pallet, rot_article, rot_pallet)
        layer, rest = it.next()
        if layer:
            layers.append(layer)
        if rest:
            rests.append(rest)

        while True:
            try:
                if try_rot_article and try_rot_pallet:
                    layer, rest = it.send(get_bitmask(product_it.send(False), 2))
                elif try_rot_article and not try_rot_pallet:
                    layer, rest = it.send((get_bitmask(product_it.send(False), 1)[0], rot_pallet_default))
                elif not try_rot_article and try_rot_pallet:
                    layer, rest = it.send((rot_article_default, get_bitmask(product_it.send(False), 1)[0]))
                else:
                    layer, rest = it.send((rot_article_default, rot_pallet_default))
                if layer:
                    layers.append(layer)
                if rest:
                    rests.append(rest)
            except StopIteration:
                break
        print b2a_base64(zlib.compress(cPickle.dumps((layers, rests, pallet)))),
        if not try_rot_article and not try_rot_pallet:
            break # only one iteration if both are deactivated
        i+=1
        if max_iter != -1 and i >= max_iter:
            break

if __name__ == "__main__":
    main()
