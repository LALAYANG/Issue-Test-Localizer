model_name=claude-3-5-sonnet-20241022
dataset_name=princeton-nlp/SWE-bench_Verified

mkdir -p logs/${dataset_name}/${model_name}

python3 -u src/test_file_selection.py  \
    --suspicious_func_json files/agentless_verified_claude_trajs_suspicious_funcs.json   \
    --output_dir_base output  \
    --dataset_name ${dataset_name} \
    --model_name ${model_name}  |& tee logs/${dataset_name}/${model_name}/test_file_selection.log