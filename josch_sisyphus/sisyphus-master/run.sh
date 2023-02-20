#!/bin/sh -e

if [ $# -ne 3 ]; then
	echo usage: $0 order.xml packlist.xml scoring.xml
	exit 1
fi

rm -f score_max

# place temporary files in tmpfs instead of disk
if [ -d /dev/shm ]; then
	export TMPDIR=/dev/shm
fi

# generate the results
# python bruteforce2.py $1 | sort -r | xargs --max-procs=4 --max-args=1 python bruteforce3.py $1 $2 $3
iterations=1000 randomize=1 python bruteforce2.py $1 | randomize=1 iterations=10000 xargs --max-procs=6 --max-args=1 python bruteforce3.py $1 $2 $3
# format the result nicely
if type xmllint > /dev/null 2>&1; then
	mv $2 $2.tmp
	xmllint --output $2 --format $2.tmp
	rm -f $2.tmp
fi

echo
echo maximum score is: `cat score_max`
echo
echo final packlist is ready in: $2
echo
echo to view it in palletViewer, run:
echo
echo palletViewer -o $1 -p $2 -s $3
echo
echo to check the final score, run:
echo
echo python evaluate.py $1 $2 $3
