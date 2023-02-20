#!/bin/bash
srcfile="../example_data/benchmark_data/bed-bpp_v1.json"


read -r -p "Is the source file correct: $srcfile? [Y/n]" response
case "$response" in
    [nN]) 
        echo "change the srcfile in this script!"
        ;;
    *)
        echo "Run the Java solver hschneid/xflp"
        echo "================================="
        cd xflp-master
        ./gradlew run --args="../"$srcfile
        mv java_output.txt ../java_output.txt


        echo "Convert the results"
        echo "==================="
        cd ..
        python3 ../code/utils/xflp/resultConverter.py --src_order $srcfile
        ;;
esac

