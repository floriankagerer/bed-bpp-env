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

# inspired by Jake Gordon's bin-packing algorithm
# https://github.com/jakesgordon/bin-packing/blob/master/js/packer.js
# http://codeincomplete.com/posts/2011/5/7/bin_packing/
# Jake Gordon was inspired by Jim Scott's solution on how to pack lightmaps
# http://www.blackpawn.com/texts/lightmaps/default.html

import random

# rounds to the next biggest even number
def roundeven(num):
    return (num+1)/2*2

def arrange_in_layer(abin, pwidth, pheight, rot_article=False):
    # articles are longer than wider
    # default rotation: width: x-direction
    #                   height:  y-direction

    layer = list()
    rest = list()
    root = {'x': 0, 'y': 0,
            'width': pwidth, 'height': pheight,
            'article': None,
            'down': None,
            'right': None}

    # traverse the tree until a node is found that is big enough for article
    # with size width x height and return this node or None if not found
    def find_node(root, width, height):
        if root is None:
            return None
        elif root['article']:
            return (find_node(root['right'], width, height)
                 or find_node(root['down'], width, height))
        elif width <= root['width'] and height <= root['height']:
            return root
        else:
            return None

    # after finding a node where an article fits, put article into the node and
    # create childnodes
    def split_node(node, width, height, article):
        node['article'] = article
        node['article']['PlacePosition']['X'] = node['x']+width/2
        node['article']['PlacePosition']['Y'] = node['y']+height/2
        if node['width'] > 0 and node['height']-height > 0:
            node['down'] = {'x': node['x'], 'y': node['y']+height,
                            'width': node['width'],
                            'height': node['height']-height,
                            'article': None,
                            'down': None,
                            'right': None}
        else:
            node['down'] = None
        if node['width']-width > 0 and height > 0:
            node['right'] = {'x': node['x']+width, 'y': node['y'],
                             'width': node['width']-width,
                             'height': height,
                             'article': None,
                             'down': None,
                             'right': None}
        else:
            node['right'] = None
        return node

    # for each article in abin, check and place article at a node. If it doesnt
    # fit, try to rotate. If it still doesnt fit, append to rest
    for article in abin:
        # output format only accepts integer positions, round article sizes up
        # to even numbers
        owidth, oheight = article['Article']['Length'], article['Article']['Width']
        if rot_article:
            article['Orientation'] = 2
            width, height = roundeven(oheight), roundeven(owidth)
        else:
            article['Orientation'] = 1
            width, height = roundeven(owidth), roundeven(oheight)

        node = find_node(root, width, height)
        if (node):
            node = split_node(node, width, height, article)
        else:
            # rotate article
            # output format only accepts integer positions, round article sizes up
            # to even numbers
            if rot_article:
                article['Orientation'] = 1
                width, height = roundeven(owidth), roundeven(oheight)
            else:
                article['Orientation'] = 2
                width, height = roundeven(oheight), roundeven(owidth)
            node = find_node(root, width, height)
            if (node):
                node = split_node(node, width, height, article)
            else:
                # rotate back
                if rot_article:
                    article['Orientation'] = 2
                else:
                    article['Orientation'] = 1
                rest.append(article)

    # gather all articles that were
    def find_articles(node):
        if not node['article']:
            return
        layer.append(node['article'])
        if node['right']:
            find_articles(node['right'])
        if node['down']:
            find_articles(node['down'])

    find_articles(root)

    return root, layer, rest

# generate a list of random articles of three different type
# each type is of the same size and color
# numbers of articles of each type linearly depend on their area
# articles are generated with more width that height
def generate_bin():
    abin = []
    for i in 1,2,3:
        w, h = random.randint(20,150), random.randint(20,150)
        if h > w:
            w, h = h, w
        color = random.randint(0,255), random.randint(0,255), random.randint(0,255)
        for j in range(200000/(w*h)):
            abin.append({'x':0, 'y':0, 'width':w, 'height':h, 'color':color})
    return abin

# given a node tree with articles inside, spread them out over the full
# available area evenly
def spread_articles(root):
    def get_width(article):
        if article['Orientation'] == 1:
            return article['Article']['Length']
        else:
            return article['Article']['Width']

    def get_height(article):
        if article['Orientation'] == 1:
            return article['Article']['Width']
        else:
            return article['Article']['Length']

    # get only nodes on the left branch of the tree. This is all nodes below
    def get_down_nodes(node):
        if node is None or not node['article']:
            return []
        else:
            return [node] + get_down_nodes(node['down'])

    # move this node and its whole subtree down
    def move_tree_down(node, y):
        if not node['article']:
            return
        node['article']['PlacePosition']['Y'] += y
        if node['right']:
            move_tree_down(node['right'], y)
        if node['down']:
            move_tree_down(node['down'], y)

    # for each child on the very left, spread vertically and adjust subtree y
    # position accordingly
    def spread_vertically(node):
        downnodes = get_down_nodes(node)
        # process innermost nodes before outer nodes
        for n in downnodes:
            if n['right']:
                spread_vertically(n['right'])
        if len(downnodes) == 0:
            return
        elif len(downnodes) == 1:
            # arrange them in the center of parent
            # treat the article height as even and round the gap size to the
            # next smallest even number
            gap = (node['height']-roundeven(get_height(downnodes[0]['article'])))/4*2
            move_tree_down(node, gap)
        else:
            # get the sum of all heights of the leftmodes articles as if they
            # had even heights
            sumdownnodes = sum([roundeven(get_height(n['article'])) for n in downnodes])
            # do some fancy math to figure out even gap sizes between
            # the nodes
            d, m = divmod((node['height']-sumdownnodes)/2, len(downnodes)-1)
            gaps = (m)*[(d+1)*2]+((len(downnodes)-1)-m)*[d*2]
            # iteratively move trees down by vgap except for first row
            for node, gap in zip(downnodes[1:], gaps):
                move_tree_down(node, gap)

    # for a given node, return a tuple consisting of a list of nodes that
    # make out the longest row in horizontal direction and a list of nodes that
    # start a shorter end
    def get_max_horiz_nodes(node):
        if node is None or not node['article']:
            return [], []
        elif node['down'] and node['down']['article']:
            # if the node has an article below, check out the rightbranch
            rightbranch, sr = get_max_horiz_nodes(node['right'])
            rightbranch = [node] + rightbranch
            # as well as the down branch
            downbranch, sd = get_max_horiz_nodes(node['down'])
            # get information about the last article in each branch
            ar = rightbranch[len(rightbranch)-1]['article']
            ad = downbranch[len(downbranch)-1]['article']
            # and return as the first tuple entry the branch that stretches the
            # longest while having as the second tuple entry the nodes that
            # were dismissed as starting shorter branches
            if ar['PlacePosition']['X']+get_width(ar)/2 > ad['PlacePosition']['X']+get_width(ad)/2:
                return rightbranch, sr+[downbranch[0]]
            else:
                return downbranch, sd+[rightbranch[0]]
        else:
            # if there is no article below, just recursively call itself on the
            # next node to the right
            rightbranch, short = get_max_horiz_nodes(node['right'])
            return [node] + rightbranch, short

    # move a node and the article inside to the right and reduce node width
    # recursively call for children
    def move_tree_right(node, x):
        if not node['article']:
            return
        node['article']['PlacePosition']['X'] += x
        node['x'] += x
        node['width'] -= x
        if node['right']:
            move_tree_right(node['right'], x)
        if node['down']:
            move_tree_right(node['down'], x)

    # for each child on the very right, spread horizontally and adjust subtree
    # x position accordingly
    def spread_horizontally(node):
        maxhoriznodes, short = get_max_horiz_nodes(node['right'])
        maxhoriznodes = [node] + maxhoriznodes
        if len(maxhoriznodes) == 0:
            return
        elif len(maxhoriznodes) == 1:
            # arrange them in the center of parent
            # treat article width as even and round the gap size to the next
            # smallest even number
            gap = (node['width']-roundeven(get_width(maxhoriznodes[0]['article'])))/4*2
            maxhoriznodes[0]['article']['PlacePosition']['X'] += gap
        else:
            # get the sum of all widths of the articles that make the longest
            # row of articles as if they had even widths
            summaxhoriznodes= sum([roundeven(get_width(n['article'])) for n in maxhoriznodes])
            # do some fancy math to figure out even gap sizes between the nodes
            d, m = divmod((node['width']-summaxhoriznodes)/2, len(maxhoriznodes)-1)
            gaps = (m)*[(d+1)*2]+((len(maxhoriznodes)-1)-m)*[d*2]
            # iteratively move trees right by hgap except for first node
            for node, gap in zip(maxhoriznodes[1:], gaps):
                move_tree_right(node, gap)
            # recursively call for all nodes starting a shorter subtree
            for node in short:
                spread_horizontally(node)

    # spread nodes vertically
    spread_vertically(root)

    # and horizontally
    for node in get_down_nodes(root):
        spread_horizontally(node)

# sanity checks
def sanity_check(layer):
    def intersects(a1, a2):
        return (a1['x']              < a2['x']+a2['width']
            and a1['x']+a1['width']  > a2['x']
            and a1['y']              < a2['y']+a2['height']
            and a1['y']+a1['height'] > a2['y'])
    odds = list()
    overhangs = list()
    inters = list()
    for article1 in layer:
        if (article1['x']%2 != 0
         or article1['y']%2 != 0):
            odds.append(article1)
        if (article1['x'] < 0
         or article1['y'] < 0
         or article1['x']+article1['width'] > pwidth
         or article1['y']+article1['height'] > pheight):
            overhangs.append(article1)
        for article2 in layer:
            if article1 == article2:
                continue
            if intersects(article1, article2):
                inters.append((article1, article2))
    for odd in odds:
        print "odd:", odd
    for overhang in overhangs:
        print "overhang:", overhang
    for inter in inters:
        print "intersect:", inter
    if len(odds) or len(overhangs) or len(inters):
        print layer
        exit(1)

# draw layer of articles
def draw_layer(filename, layer):
    import svg
    scene = svg.Scene(filename, (pwidth, pheight))
    for a in layer:
        scene.add(svg.Rectangle((a['x'], a['y']),(a['width'], a['height']),a['color']))
    scene.write()

# return all articles in a node tree
def find_articles(node):
    if node is None or not node['article']:
        return []
    else:
        return [node['article']] + find_articles(node['right']) + find_articles(node['down'])

if __name__ == "__main__":
    abin = generate_bin()
    pwidth, pheight = 800, 600
    abin = sorted(abin, key=lambda article: article['width']*article['height'], reverse=True)
    root, layer, rest = arrange_in_layer(abin, pwidth, pheight)
    draw_layer('test1', layer)
    spread_articles(root)
    layer = find_articles(root)
    draw_layer('test2', layer)
    sanity_check(layer)
