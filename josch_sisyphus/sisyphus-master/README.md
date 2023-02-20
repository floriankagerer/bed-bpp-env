about
=====

sisyphus is a piece of software I wrote the context of my graduate automation
project. My class was taking part in the IEEE ICRA 2012 Virtual Manufacturing
Automation Competition and part of the competition, was to efficiently stack
boxes of different sizes on a pallet.

As the knapsack problem is NP hard, sisyphus implements hybrid between
heuristic and bruteforce approach.

The heuristic is, to group articles of same height into layers, and then stack
those layers on top of each other.

Different techniques to form layers and different orderings of stacking them
are then tried out in a bruteforce manner.

get the code
============

	$ git clone git@github.com:josch/sisyphus.git
	$ cd sisyphus


compile evaluation library
==========================

	$ wget http://sourceforge.net/projects/moast/files/Pallet%20Viewer/Version%203/palletandtruckviewer-3.0.tar.gz
	$ tar xf palletandtruckviewer-3.0.tar.gz
	$ cd palletandtruckviewer-3.0
	$ patch -p0 < ../palletViewer-sharedlib.diff
	$ autoreconf -fi
	$ ./configure --libdir=`pwd`/..
	$ make
	$ make install-strip
	$ cd ..

test evaluation library (optional)
==================================

	$ python evaluate_multi.py examples/icra2012/packlist_R1.xml examples/icra2012/scorecog.xml

	$ python evaluate.py examples/icra2012/Challenge2.order.xml examples/icra2012/packlist_R2.xml examples/icra2012/scorecog.xml

	$ python evaluate.py examples/icra2012/Challenge2.order.xml examples/icra2012/packlist_R3.xml examples/icra2012/scorecogoverlap.xml

generate packlist files
=======================

	$ ./run.sh examples/icra2011/palDay1R1Order.xml packlist.xml examples/icra2011/scoreAsPlannedConfig1.xml

Usage
=====

bruteforce2.py takes an order.xml and tries different strategies to create many
lists of layerlists. Each layerlist is built with a different selection of
strategies. Available strategies are article rotation and pallet rotation which
can both be either true or false. Per default, bruteforce2.py tries all
combinations of article and pallet rotations, which means that for each new
layer, there are four possibilities how articles can be arranged in it.

A layerlist is the result of one specific combinations of strategies. For
example: first layer with article rotation and pallet rotation, second layer
without article rotation but with pallet rotation, third layer with neither and
so forth.

bruteforce2.py outputs those layerlists one per line in python pickle gzipped
and base64 encoded format. Python pickle is used as a fast serialization
format. The data is gzipped because it is given to bruteforce3.py as a
commandline argument and those must not exceed an OS specific value. The data
is base64 encoded to avoid zero bytes, newlines and other whitespace characters
in them.

As a result, the output of bruteforce2.py can not only be saved in a file, but
you can also used split(1) on it to distribute it onto many machines for
evaluations. You can also use head(1), tail(1), sort(1) or uniq(1) on the
output.

bruteforce3.py takes as arguments an order.xml, a packlist.xml output file, a
scoring.xml file and a number of layerlists, encoded as described above. For
each layerlist it will try every possible permutation of how to place them on
top of each other and evaluate each of them by using palletViewer.

Multiple instances of bruteforce3.py can be run on the same machine. Before
bruteforce3.py exits, it will put a file lock on score_max.lock and read the
currently highest score from score_max. If the just calculated score is higher,
it will write its own score into score_max and update the contents of
packlist.xml as well.

Since score_max always contains the currently highest score, it can always
easily be checked during a run, what the currently highest score achieved is.

Since packlist.xml always contains the best packlist found so far,
bruteforce3.py can always be aborted in the middle of execution, should it take
too long to evaluate while still maintaining the current best packlist. One
does not need to wait until run.sh finished execution.

Since score_max contains the highest score, it should be removed before each
new run. This is already done by run.sh.

environment variables
=====================

bruteforce2
-----------

    rot_article         - try different article rotations (default: True)
    rot_pallet          - try different pallet rotations (default: True)
    rot_article_default - default article rotation (default: False)
    rot_pallet_default  - default pallet rotation (default: False)
    iterations          - maximum number of iterations (default: -1)
    randomize           - try random strategies instead of sequential (default: False)

bruteforce3
-----------

    multi_pallet        - respect pallet max height and spread over multiple pallets (default: False)
    permutations        - whether to try all layer permutations or not permute at all (default: True)
    iterations          - maximum number of iterations (default: -1)
    randomize           - try random strategies instead of sequential (default: False)

For orders that are too big to enumerate all possible permutations of layer
strategies and orderings, using randomize and iterations for bruteforce2.py and
bruteforce3.py is recommended.

The according line in run.sh could be changed to:

	iterations=100 randomize=1 python bruteforce2.py $1 | randomize=1 iterations=1000 xargs --max-procs=4 --max-args=1 python bruteforce3.py $1 $2 $3

utility scripts
===============

    add_approach_points.py

        takes a single or multi pallet packlist.xml and adds the three approach
        points to all the articles in it, relative to each articles position

    barcodes.py

        takes an order.xml and prints all barcodes in it

    densities.py

        takes an order.xml and prints the density of all articles

    descriptions.py

        takes an order.xml and prints a table with the description, ID, type,
        family, size and weight of every article

    evaluate_multi.py

        takes a multiple pallet packlist.xml and a scoring.xml and prints out
        the score that this packlist achieves

    evaluate.py

        takes an order.xml, a single pallet packlist.xml and a scoring.xml and
        prints out the score that this packlist achieves

    num_articles_order.py

        takes an order.xml and prints the number of articles within

    num_articles_packlist.py

        takes a single or multi pallet packlist.xml and prints the number of
        articles within

    pallets.py

        takes an order.xml and prints a table with the length, width, maximum
        load height and maximum load weight

    split_multi.py

        takes a multiple pallet packlist.xml and outputs pairs of single pallet
        packlist.xml and order.xml files by appending _$i.xml and _order_$i.xml
        to the original packlist.xml filename, respectively. The integer $i
        starts at 0 and	will be incremented with each subsequent pallet.

evaluation of multi pallet packlists
====================================

palletViewer cannot parse multi pallet packlists, hence the packlists have to
be split into several single pallet packlists. Each of those packlists is then
given to palletViewer for evaluation. The individual results are averaged for a
final score. To avoid each of the palletViewer instances complain about missing
articles, an according order.xml file is created for each single pallet
packlist.xml.

Multi pallet packlists can evaluated like this:

	python evaluate_multi.py packlist.xml scoring.xml

Or manually like this:

	python split_multi.py packlist.xml
	python evaluate.py packlist.xml_order_0.xml packlist_R1.xml_0.xml scoring.xml
	python evaluate.py packlist.xml_order_1.xml packlist_R1.xml_1.xml scoring.xml
	...

bugs
====

there is a "memory leak" in bruteforce3.py. Every loop iteration where a new
permutation is tried out will stay in memory. This is not needed and should not
be the case. This is the reason why run.sh supplies bruteforce3.py with only
one layerlist at a time because otherwise, memory consumption would grow too
big.

ICRA 2012 VMAC
==============

Sisyphus won the IEEE ICRA 2012 Virtual Manufacturing Automation Competition.
Here is some media about our submission:

Round1: ./examples/icra2012/packlist_R1.xml

Round2: ./examples/icra2012/packlist_R2.xml

Round3: ./examples/icra2012/packlist_R3.xml

announcement: http://youtu.be/8fYF-Ldi1NQ

presentation: http://youtu.be/FSqjGiVt50I
