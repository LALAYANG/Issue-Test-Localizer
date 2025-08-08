python3 -u src/generate_cov_batch.py \
    'princeton-nlp/SWE-bench_Verified' \
    'test_results_collected_merged' \
    'result_files/confirmed_suspicious_funcs.json' \
    'result_files/test_selection_merged.json' |& tee test_results_collected_merged.log