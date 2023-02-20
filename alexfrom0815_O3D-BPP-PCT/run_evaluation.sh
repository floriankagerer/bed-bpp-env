# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #  
# Script for evaluating the performance of the Online-§D-BPP-PCT solver.  #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
USED_DATASET=dataset/bed-bpp_v1.pkl
EVALUATION_EPISODES=10003
FNAME_EVAL=evaluation_output.log
FNAME_EVAL_RC=rollcontainer_evaluation_output.log
FNAME_EVAL_PAL=euro-pallet_evaluation_output.log

source activate_O3DBPP-PTC_venv.sh

# internal node holder must be greater or equal the maximum length of items an all orders
# note that the loaded dataset must start with [] and end with [], since otherwise not all orders are considered
cd Online-3D-BPP-PCT-main/


python3 evaluation.py --evaluate --load-model --model-path pt_models/PCT_rollcontainer_7200updates.pt --load-dataset --dataset-path $USED_DATASET --no-cuda --setting=1 --internal-node-holder=160 --evaluation-episodes=$EVALUATION_EPISODES
mv $FNAME_EVAL ../$FNAME_EVAL_RC

python3 evaluation.py --evaluate --load-model --model-path pt_models/PCT_euro-pallet_3200updates.pt --load-dataset --dataset-path $USED_DATASET --no-cuda --setting=1 --internal-node-holder=160 --evaluation-episodes=$EVALUATION_EPISODES
mv $FNAME_EVAL ../$FNAME_EVAL_PAL



cd ../..
# convert result
deactivate
echo "Convert the result."
echo "-------------------"
source activate_venv.sh
cd alexfrom0815_O3D-BPP-PCT/
python3 ../code/utils/o3dbpp_pct/resultConverter.py --src_solver $FNAME_EVAL_RC $FNAME_EVAL_PAL

deactivate
