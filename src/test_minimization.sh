COV_DIR='coverage_results_SWE-bench_Verified_claude/'
TEST_LOG_DIR='logs/run_evaluation/coverage_results_SWE-bench_Verified_claude/gold/'
SUSPICIOUS_JSON='files/agentless_verified_claude_trajs_suspicious_funcs.json'

python3 src/test_minimization.py \
                    --coverage_dir ${COV_DIR} \
                    --test_log_dir ${TEST_LOG_DIR} \
                    --suspicious_json ${SUSPICIOUS_JSON} \
                    --datasetname princeton-nlp/SWE-bench_Verified \
                    --log_dir minimization_logs \
                    --model_name claude-3-5-sonnet-20241022 \