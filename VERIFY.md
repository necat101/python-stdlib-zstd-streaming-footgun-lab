# VERIFY.md

## Implementation commit

Repository: https://github.com/necat101/python-stdlib-zstd-streaming-footgun-lab

Verified implementation commit: `72151902f3021002d82ad97ed95b93e8b477fd2b`

## Clean-clone verification

```sh
git clone https://github.com/necat101/python-stdlib-zstd-streaming-footgun-lab.git zstd_verify
cd zstd_verify
# HEAD is 72151902f3021002d82ad97ed95b93e8b477fd2b (only commit at time of verification)

python3 -m py_compile run_lab.py test_lab.py
# exit 0

python3 run_lab.py
# rows=80 pass=7 fail=0 version_skip=31 elapsed=0.00s
# exit 0

python3 -m unittest -v
# Ran 12 tests in 0.014s
# OK
# exit 0
```

Python executable: `/usr/bin/python3`
Python version: 3.12.3 (main, Jun 19 2026, 12:46:00) [GCC 13.3.0]
compression.zstd available: False
Reason: Python 3.12 < 3.14, compression.zstd does not exist

Cases: 20
Methods: 4
Rows: 80

Classification counts (actual):
- pass: 7
- expected_error: 0
- local_observation: 15
- version_skip: 31
- context_only: 5
- not_applicable: 22
- fail: 0

Verification wall-clock time: ~1 second (clone + py_compile + run_lab + unittest)

Structured artifacts (`results_rows.json`, `results_rows.csv`) agree with `RESULTS.md` counts.

No sensitive paths (home directories, temp paths, tokens, `/openclaw` internal paths) found in committed text artifacts: `cases.json`, `results_rows.json`, `results_rows.csv`, `README.md`, `RESULTS.md`, `hn_thread_evidence.md`, `hn_comments_sanitized.json`.

## Skips

`compression.zstd` was unavailable (Python 3.12 < 3.14). 31 Zstandard-dependent rows classified as `version_skip` with precise reason: "Python 3.12 < 3.14, compression.zstd does not exist".

The `zlib` comparison case (`zlib_dictionary_and_copy_comparison_marker`) and the lexical-overlap case (with `zlib.compress` fallback) produced meaningful results without `compression.zstd`.

This is a **version-sensitive stdlib API lab with honest skips**, NOT a "Zstandard-validated" run.

## Documentation commit

This `VERIFY.md` file was committed after the clean-clone verification, as a later documentation commit. The implementation commit verified above (72151902f3021002d82ad97ed95b93e8b477fd2b) does NOT contain this `VERIFY.md`.

The later documentation commit containing `VERIFY.md` was NOT itself fresh-clone verified unless another verification cycle is performed and committed.
