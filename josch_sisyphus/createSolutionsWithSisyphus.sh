# !/bin/bash
INPUT_DATA="../example_data/benchmark_data/bed-bpp_v1.json"

echo "load the orders for which solutions are created"
echo "==============================================="
mapfile -t arr < <(jq -r 'keys[]' ${INPUT_DATA})
echo "available orders: ${arr[@]}"

for ORDER in "${arr[@]}"
do
    echo "convert input of ${ORDER} for sisyphus"
    python3 ../code/utils/sisyphus/orderConverter.py --src_order ${INPUT_DATA} --order_id ${ORDER}
    order="order_${ORDER}.xml"
    mv ${order} sisyphus-master/${order}

    packlist="packlist_${ORDER}.xml"
    echo "run sisyphus bash for order ${ORDER}"


    # change to sisyphus-master as working directory
    cd sisyphus-master/
    # run    INPUT.XML                            OUTPUT.XML  SCORE.XML
    ./run.sh ${order} ${packlist} examples/icra2011/scoreAsPlannedConfig1.xml
    mv ${packlist} ../${packlist} # move the packlist one level up
    
    # tidy up
    rm ${order}
    cd ..

done

echo "convert output of sisyphus of ${ORDER} for myopic palletizing"
python3 ../code/utils/sisyphus/packlistConverter.py --dir_solver . --src_order ${INPUT_DATA}

