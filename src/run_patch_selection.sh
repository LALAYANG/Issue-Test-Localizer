python src/patch_selection_multi.py \
    --instances-file regression_reproduction_data/instances_257.json \
  --reproduction-tests-json regression_reproduction_data/reproduction_tests.json \
  --tests-file minimization_logs_fixed/SWE-bench_Verified/coverage_results_SWE-bench_Verified_gpt4o/minimized_tests.json \
  --repo-path /testbed \
  --log-dir test_logs \
  --max-workers 6 \
  --run-id-prefix test00 \


