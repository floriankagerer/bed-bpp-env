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

from xml.etree import ElementTree
import operator

def xmltodict(element):
    if not isinstance(element, ElementTree.Element):
        raise ValueError("must pass xml.etree.ElementTree.Element object")

    def xmltodict_handler(parent_element):
        result = dict()
        for element in parent_element:
            if len(element):
                obj = xmltodict_handler(element)
            else:
                obj = element.text

            if result.get(element.tag):
                if hasattr(result[element.tag], "append"):
                    result[element.tag].append(obj)
                else:
                    result[element.tag] = [result[element.tag], obj]
            else:
                result[element.tag] = obj
        return result

    return {element.tag: xmltodict_handler(element)}


def dicttoxml(element):
    if not isinstance(element, dict):
        raise ValueError("must pass dict type")
    if len(element) != 1:
        raise ValueError("dict must have exactly one root key")

    def dicttoxml_handler(result, key, value):
        if isinstance(value, list):
            for e in value:
                dicttoxml_handler(result, key, e)
        elif isinstance(value, basestring):
            elem = ElementTree.Element(key)
            elem.text = value
            result.append(elem)
        elif isinstance(value, int) or isinstance(value, float):
            elem = ElementTree.Element(key)
            elem.text = str(value)
            result.append(elem)
        elif value is None:
            result.append(ElementTree.Element(key))
        else:
            res = ElementTree.Element(key)
            for k, v in sorted(value.items(), key=operator.itemgetter(0)):
                dicttoxml_handler(res, k, v)
            result.append(res)

    result = ElementTree.Element(element.keys()[0])
    for key, value in sorted(element[list(element.keys())[0]].items(), key=operator.itemgetter(0)):
        dicttoxml_handler(result, key, value)
    return result

def xmlfiletodict(filename):
    return xmltodict(ElementTree.parse(filename).getroot())

def dicttoxmlfile(element, filename):
    ElementTree.ElementTree(dicttoxml(element)).write(filename)

def xmlstringtodict(xmlstring):
    return xmltodict(ElementTree.fromstring(xmlstring).getroot())

def dicttoxmlstring(element):
    return ElementTree.tostring(dicttoxml(element))

def get_pallet(orderline):
    p = orderline['Message']['PalletInit']['Pallets']['Pallet']
    return {
            'PalletNumber': int(p['PalletNumber']),
            'Description': p['Description'],
            'Dimensions': {
                'MaxLoadHeight': int(p['Dimensions']['MaxLoadHeight']),
                'MaxLoadWeight': int(p['Dimensions']['MaxLoadWeight']),
                'Length': int(p['Dimensions']['Length']),
                'Width': int(p['Dimensions']['Width']),
            }
        }

def get_articles(orderline):
    articles = list()
    for o in orderline['Message']['Order']['OrderLines']['OrderLine']:
        if isinstance(o['Barcodes']['Barcode'], basestring):
            barcodes = [o['Barcodes']['Barcode']]
        else:
            barcodes = o['Barcodes']['Barcode']
        for barcode in barcodes:
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
    return articles

def get_order_dict(pallet, articles):
    # create order file from article list
    # ignore article grouping into orderlines and have one orderline per article
    orderlines = list()

    for i, article in enumerate(articles):
        orderlines.append({
            'OrderLineNo': str(i),
            'Article': article['Article'],
            'Barcodes': { 'Barcode': article['Barcode'] }
        })

    return {'Message':
               {'PalletInit': {'Pallets': {'Pallet': {
                   'PalletNumber': int(pallet['PalletNumber']),
                   'Description': pallet['Description'],
                   'Dimensions': {
                       'MaxLoadHeight': int(pallet['Dimensions']['MaxLoadHeight']),
                       'MaxLoadWeight': int(pallet['Dimensions']['MaxLoadWeight']),
                       'Length': int(pallet['Dimensions']['Length']),
                       'Width': int(pallet['Dimensions']['Width'])
                   } } } },
                'Order':
                   {'ID': '1',
                    'Description': 'foobar',
                    'Restrictions': { 'FamilyGrouping': 'False', 'Ranking': 'False' },
                    'Orderlines': { 'OrderLine': orderlines }
                   }
               }
           }

def get_packlist_dict(pallet, articles):
    pallet['Packages'] = {'Package': articles}
    return {'Response':
               {'PackList':
                   {'OrderID': '1',
                    'PackPallets':
                        {'PackPallet': pallet }
                   }
               }
    }

def get_packlist_dict_multi(pallet, article_lists):
    pallets = []

    for articles in article_lists:
        pallets.append({
            'PalletNumber': int(pallet['PalletNumber']),
            'Description': pallet['Description'],
            'Dimensions': {
                'MaxLoadHeight': int(pallet['Dimensions']['MaxLoadHeight']),
                'MaxLoadWeight': int(pallet['Dimensions']['MaxLoadWeight']),
                'Length': int(pallet['Dimensions']['Length']),
                'Width': int(pallet['Dimensions']['Width'])
            },
            'Packages': {'Package': articles}
        })

    return {'Response':
               {'PackList':
                   {'OrderID': '1',
                    'PackPallets':
                        {'PackPallet': pallets }
                   }
               }
           }

def product_varlength(branch_factor):
    root = {"value": None, "parent": None, "children": []}
    current = root
    while True:
        if not current["children"]:
            current["children"] = [{"value":val, "parent":current, "children":[]}
                                    for val in range(branch_factor)]
        current = current["children"][0]
        if (yield current["value"]):
            current["parent"]["children"] = [] # only for the icra 2012
            current = current["parent"]        # bruteforce implementation
            while True:
                if current["parent"]:
                    current["parent"]["children"].pop(0)
                else:
                    return
                if current["parent"]["children"]:
                    current = root
                    break
                else:
                    current = current["parent"]

# cannot use itertools.cycle as it doesnt allow to send() to it
def cycle(iterable):
    saved = []
    for element in iterable:
        yield element
        saved.append(element)
    while saved:
        for element in saved:
              yield element

# cannot use itertools.starmap as it doesnt allow to send() to it
def starmap(function, iterable):
    for args in iterable:
        yield function(*args)

if __name__ == "__main__":
    it = product_var_repeat(3)
    while True:
        try:
            foo = it.send(True) # start a new combination
        except TypeError:
            foo = it.next() # can't send to a just-started generator
        except StopIteration:
            break # generator empty
        print foo, it.send(False), it.send(False)

    tree = ElementTree.parse('../icra2011TestFiles/GT/gt_d1r1.wpacklist.xml')
    #tree = ElementTree.parse('../icra2011TestFiles/palDay1R1Order.xml')
    root = tree.getroot()
    xmldict = xmltodict(root)
    
    from pprint import pprint
    #for package in xmldict['PackList']['PackPallets']['PackPallet']['Packages']['Package']:
    #    pprint(package)
    
    
    root = dicttoxml(xmldict)
    
    xmldict = xmltodict(root)
    pprint(xmldict)
    
    packages = [{'ApproachPoint1': {'X': '0',
                                    'Y': '0',
                                    'Z': '0'},
                 'ApproachPoint2': {'X': '0',
                                    'Y': '0',
                                    'Z': '0'},
                 'ApproachPoint3': {'X': '0',
                                    'Y': '0',
                                    'Z': '0'},
                 'Article': {'Description': '3',
                             'Family': '0',
                             'Height': '41',
                             'ID': '3',
                             'Length': '44',
                             'Type': '0',
                             'Weight': '500',
                             'Width': '132'},
                 'Barcode': None,
                 'Orientation': '1',
                 'PackSequence': '1',
                 'PlacePosition': {'X': '286',
                                   'Y': '330',
                                   'Z': '41'},
                 'StackHeightBefore': '0'},
                {'ApproachPoint1': {'X': '0',
                                    'Y': '0',
                                    'Z': '0'},
                 'ApproachPoint2': {'X': '0',
                                    'Y': '0',
                                    'Z': '0'},
                 'ApproachPoint3': {'X': '0',
                                    'Y': '0',
                                    'Z': '0'},
                 'Article': {'Description': '4',
                             'Family': '0',
                             'Height': '41',
                             'ID': '4',
                             'Length': '66',
                             'Type': '0',
                             'Weight': '550',
                             'Width': '132'},
                 'Barcode': None,
                 'Orientation': '1',
                 'PackSequence': '54',
                 'PlacePosition': {'X': '33',
                                   'Y': '66',
                                   'Z': '164'},
                 'StackHeightBefore': '0'}]
    
    packlist = {'Response': {'PackList': {'OrderID': '1',
                               'PackPallets': {'PackPallet': {'BruttoWeight': '63000',
                                                              'Description': None,
                                                              'Dimensions': {'Length': '308',
                                                                             'MaxLoadHeight': '406',
                                                                             'MaxLoadWeight': '99999',
                                                                             'Width': '396'},
                                                              'NumberofPackages': '54',
                                                              'Overhang': {'Length': '0',
                                                                           'Width': '0'},
                                                              'Packages': {'Package': packages},
                                                              'PalletNumber': '1'}}}}}
    
