import sys
from util import xmlfiletodict, dicttoxmlstring

def main():
    if len(sys.argv) != 5:
        print "usage:", sys.argv[0], "packlist.xml x1,y1,z1 x2,y2,z2 x3,y3,z3"
        exit(1)

    x1, y1, z1 = map(int, sys.argv[2].split(','))
    x2, y2, z2 = map(int, sys.argv[3].split(','))
    x3, y3, z3 = map(int, sys.argv[4].split(','))

    d = xmlfiletodict(sys.argv[1])

    pallets = d["Response"]["PackList"]["PackPallets"]["PackPallet"]

    if not isinstance(pallets, list):
        pallets = [pallets]

    for pallet in pallets:
        for article in pallet["Packages"]["Package"]:
            x, y, z = int(article['PlacePosition']['X']), int(article['PlacePosition']['Y']), int(article['PlacePosition']['Z'])
            article['ApproachPoint1']['X'], article['ApproachPoint1']['Y'], article['ApproachPoint1']['Z'] = x+x1, y+y1, z+z1
            article['ApproachPoint2']['X'], article['ApproachPoint2']['Y'], article['ApproachPoint2']['Z'] = x+x2, y+y2, z+z2
            article['ApproachPoint3']['X'], article['ApproachPoint3']['Y'], article['ApproachPoint3']['Z'] = x+x3, y+y3, z+z3

    sys.stdout.write(dicttoxmlstring(packlist))

if __name__ == "__main__":
    main()
