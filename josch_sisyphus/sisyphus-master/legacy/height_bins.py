from util import xmlfiletodict, dicttoxmlfile
from collections import OrderedDict
import sys
import math

if len(sys.argv) != 3:
    print "usage:", sys.argv[0], "order.xml packlist.xml"
    exit(0)

orderline = xmlfiletodict(sys.argv[1])

# important: assuming only one pallet in input!!
p = orderline['Message']['PalletInit']['Pallets']['Pallet']
pallet = {
        'PalletNumber': int(p['PalletNumber']),
        'Description': p['Description'],
        'Dimensions': {
            'MaxLoadHeight': int(p['Dimensions']['MaxLoadHeight']),
            'MaxLoadWeight': int(p['Dimensions']['MaxLoadWeight']),
            'Length': int(p['Dimensions']['Length']),
            'Width': int(p['Dimensions']['Width']),
        }
    }

articles = list()

for o in orderline['Message']['Order']['OrderLines']['OrderLine']:
    for barcode in o['Barcodes']['Barcode']:
        articles.append(
            {'ApproachPoint1': {'X': 0, 'Y': 0, 'Z': 0},
             'ApproachPoint2': {'X': 0, 'Y': 0, 'Z': 0},
             'ApproachPoint3': {'X': 0, 'Y': 0, 'Z': 0},
             'Article': { 'Description': o['Article']['Description'],
                          'ID': int(o['Article']['ID']),
                          'Type': int(o['Article']['Type']), # currently only Type=1 is allowed
                          'Family': int(o['Article']['Family']),
                          'Length': int(o['Article']['Length']), # should be larger than width
                          'Width': int(o['Article']['Width']),
                          'Height': int(o['Article']['Height']),
                          'Weight': int(o['Article']['Weight']) # in grams
                        },
             'Barcode': barcode,
             'Orientation': 1, # 1: 0 deg the long side parallel to X direction
                               # 2: 90 deg the long side parallel to Y direction
             'PackSequence': 0,
             'PlacePosition': {'X': 0, 'Y': 0, 'Z': 0}
            }
        )

bins = OrderedDict()

# sort into bins of equal height, have bins ordered by height of contents
for article in sorted(articles, key=lambda article: article['Article']['Height'], reverse = True):
    abin = bins.get(article['Article']['Height'])
    if abin:
        abin.append(article)
    else:
        bins[article['Article']['Height']] = [article]

def arrange_in_layer(abin, plength, pwidth):
    # articles are longer than wider
    # default rotation: length: x-direction
    #                   width:  y-direction

    layer = list()
    rest = list()
    root = {'x': 0, 'y': 0, 'length': plength, 'width': pwidth, 'used': False, 'up': None, 'right': None}

    def find_node(root, length, width):
        if root['used']:
            return find_node(root['right'], length, width) or find_node(root['up'], length, width)
        elif length <= root['length'] and width <= root['width']:
            return root
        else:
            return None

    def split_node(node, length, width):
        node['used'] = True
        node['up'] =    {'x': node['x'], 'y': node['y']+width, 'length': node['length'], 'width': node['width']-width, 'used': None, 'up': None, 'right': None}
        node['right'] = {'x': node['x']+length, 'y': node['y'], 'length': node['length']-length, 'width': width, 'used': None, 'up': None, 'right': None}
        return node

    for article in abin:
        # output format only accepts integer positions, round package sizes up to even numbers
        length, width = (article['Article']['Length'], article['Article']['Width'])
        if length%2 != 0:
            length += 1
        if width%2 != 0:
            width +=1

        node = find_node(root, length, width)
        if (node):
            node = split_node(node, length, width)
            article['PlacePosition']['X'] = node['x']+length/2
            article['PlacePosition']['Y'] = node['y']+width/2
            layer.append(article)
        else:
            # TODO: try again with article rotated
            # print "didnt fit"
            rest.append(article)

    return layer, rest

layers = list()
rests = list()

for abin in bins:
    # TODO: if there is a rest, maybe taking a few items away from former layers can fill up the rest
    # TODO: sort by something different and see what gives better result
    # TODO: try to rotate result 180 degrees
    # TODO: try to build with pallet rotated 90 or 270 degrees
    # TODO: try to rotate boxes by 90 degrees beforehand
    # TODO: check if articles from to-be-processed bins fits inbetween current layer articles
    # TODO: divide pallet horizontally, vertically and both and fill parts equally and connect afterwards
    bins[abin] = sorted(bins[abin], key=lambda article: article['Article']['Length']*article['Article']['Width'], reverse=True)
    plength, pwidth = (pallet['Dimensions']['Length'], pallet['Dimensions']['Width'])
    layer, rest = arrange_in_layer(bins[abin], plength, pwidth)
    while layer:
        occupied_area = 0
        for article in layer:
            length, width = article['Article']['Length'], article['Article']['Width']
            occupied_area += length*width

        # print "layer occupation:", occupied_area/float(plength*pwidth)
        if occupied_area/float(plength*pwidth) <= 0.7:
            rests.append(layer)
        else:
            layers.append(layer)

        layer, rest = arrange_in_layer(rest, plength, pwidth)

    if rest:
        rests.append(rest)

# sort rests by their occupied area and stack them by it
# TODO: continuously try to cram all the to-be-stacked rest into a single layer
# TODO: divide pallet horizontally and/or vertically and make two or four separate stacks
for rest in sorted(rests, key=lambda rest: sum([article['Article']['Length']*article['Article']['Width'] for article in rest]), reverse=True):
    plength, pwidth = (pallet['Dimensions']['Length'], pallet['Dimensions']['Width'])
    layer, rest = arrange_in_layer(rest, plength, pwidth)

    com_x = 0
    com_y = 0
    for article in layer:
        com_x += article['PlacePosition']['X']
        com_y += article['PlacePosition']['Y']
    com_x, com_y = com_x/len(layer), com_y/len(layer)

    diff_x, diff_y = plength*0.5-com_x, pwidth*0.5-com_y

    for article in layer:
        article['PlacePosition']['X'] += diff_x
        article['PlacePosition']['Y'] += diff_y

    layers.append(layer)

pack_sequence = 1
pack_height = 0
articles_to_pack = list()
# TODO sort them by covered area or not?
# TODO sort them by weight?
for layer in sorted(layers, key=lambda layer: sum([article['Article']['Length']*article['Article']['Width'] for article in layer]), reverse=True):
    # TODO: spread layers across available space
    pack_height += layer[0]['Article']['Height']
    for article in layer:
        article['PackSequence'] = pack_sequence
        article['PlacePosition']['Z'] = pack_height
        articles_to_pack.append(article)
        pack_sequence += 1
        #print "barcode:", article['Barcode']

# TODO: are multiple pallets allowed?
packlist = {'Response':
                {'PackList':
                    {'OrderID': '1',
                     'PackPallets':
                        {'PackPallet':
                            {'Description': pallet['Description'],
                             'Dimensions': {'Length': pallet['Dimensions']['Length'],
                                            'MaxLoadHeight': pallet['Dimensions']['MaxLoadHeight'],
                                            'MaxLoadWeight': pallet['Dimensions']['MaxLoadWeight'],
                                            'Width': pallet['Dimensions']['Width']},
                             'Packages': {'Package': articles_to_pack},
                             'PalletNumber': pallet['PalletNumber']
                            }
                        }
                    }
                }
            }

# following the code for multiple pallets
#
# pack_sequence = 1
# pack_height = 0
# pack_weight = 0
# pallets = [
#                             {'Description': pallet['Description'],
#                              'Dimensions': {'Length': pallet['Dimensions']['Length'],
#                                             'MaxLoadHeight': pallet['Dimensions']['MaxLoadHeight'],
#                                             'MaxLoadWeight': pallet['Dimensions']['MaxLoadWeight'],
#                                             'Width': pallet['Dimensions']['Width']},
#                              'Packages': {'Package': []},
#                              'PalletNumber': pallet['PalletNumber']
#                             }
# ]
# 
# # TODO sort them by covered area or not?
# for layer in sorted(layers, key=lambda layer: sum([article['Article']['Length']*article['Article']['Width'] for article in layer]), reverse=True):
#     # TODO: spread layers across available space
# 
#     pack_height += layer[0]['Article']['Height']
# 
#     if pack_height > pallet['Dimensions']['MaxLoadHeight']:
#         pallets.append(
#                             {'Description': pallet['Description'],
#                              'Dimensions': {'Length': pallet['Dimensions']['Length'],
#                                             'MaxLoadHeight': pallet['Dimensions']['MaxLoadHeight'],
#                                             'MaxLoadWeight': pallet['Dimensions']['MaxLoadWeight'],
#                                             'Width': pallet['Dimensions']['Width']},
#                              'Packages': {'Package': []},
#                              'PalletNumber': pallet['PalletNumber']
#                             }
#         )
#         pack_height = layer[0]['Article']['Height']
#         pack_weight = 0
# 
#     for article in layer:
#         pack_weight += article['Article']['Weight']
# 
#         if pack_weight > pallet['Dimensions']['MaxLoadWeight']:
#             pallets.append(
#                             {'Description': pallet['Description'],
#                              'Dimensions': {'Length': pallet['Dimensions']['Length'],
#                                             'MaxLoadHeight': pallet['Dimensions']['MaxLoadHeight'],
#                                             'MaxLoadWeight': pallet['Dimensions']['MaxLoadWeight'],
#                                             'Width': pallet['Dimensions']['Width']},
#                              'Packages': {'Package': []},
#                              'PalletNumber': pallet['PalletNumber']
#                             }
#             )
#             pack_height = layer[0]['Article']['Height']
#             pack_weight = article['Article']['Weight']
# 
#         article['PackSequence'] = pack_sequence
#         article['PlacePosition']['Z'] = pack_height
#         pallets[len(pallets)-1]['Packages']['Package'].append(article)
#         pack_sequence += 1
#         #print "barcode:", article['Barcode']
# 
# # TODO: are multiple pallets allowed?
# packlist = {'Response':
#                 {'PackList':
#                     {'OrderID': '1',
#                      'PackPallets':
#                         {'PackPallet': pallets
#                         }
#                     }
#                 }
#             }

dicttoxmlfile(packlist, sys.argv[2])
