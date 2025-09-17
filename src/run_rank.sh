set -euo pipefail

timestamp=$(date +%Y%m%d_%H%M%S)
mkdir -p final_ranks_lite_gpt4o_add/all_repro_rerank_${timestamp}
# test_logs_gpt4o_lite
#test_logs_gpt4o_lite_add
#gpt4o_lite_only_regression
for summary in test_logs_gpt4o_lite_add/*_summary.json; do
    # extract instance id (remove dir + suffix)
    base=$(basename "$summary")
    id="${base%_summary.json}"

    out="final_ranks_lite_gpt4o_add/all_repro_rerank_${timestamp}/${id}.json"
    echo "Ranking $summary -> $out"

    # python3 src/rank.py --summary_json "$summary" --out "$out"

    python src/rank_tie.py \
    --summary_json "$summary" \
    --seed 8 \
    --pick_one_from_tie \
    --out "$out"
done

#  python3 src/rank_model.py --summary_json test_logs/astropy__astropy-13236_summary.json --out ranked_model_new/astropy__astropy-13236.json \
#       --hf-dataset princeton-nlp/SWE-bench_Verified \
#         --hf-split test \
#         --api-base https://api.openai.com \
#         --model gpt-4o \
#         --log-raw-response \
#         --log-prompts