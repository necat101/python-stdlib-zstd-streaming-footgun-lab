# VERIFY.md

## Implementation commit

Repository: https://github.com/necat101/python-stdlib-zstd-streaming-footgun-lab

Verified implementation commit: `a7f72d50cce4a11b01ef3bfe73b8b5f90a6b1bed`

## Clean-clone verification (Python 3.14 + compression.zstd)

```sh
git clone https://github.com/necat101/python-stdlib-zstd-streaming-footgun-lab.git zstd_verify
cd zstd_verify
git checkout a7f72d50cce4a11b01ef3bfe73b8b5f90a6b1bed

/home/ubuntu/.local/bin/python3.14 -m py_compile run_lab.py test_lab.py
# exit 0

/home/ubuntu/.local/bin/python3.14 run_lab.py
# rows=80 pass=37 fail=0 expected_error=1 version_skip=0 elapsed=0.00s
# exit 0

/home/ubuntu/.local/bin/python3.14 -m unittest -v
# Ran 15 tests in 0.007s
# OK
# exit 0
```

Python executable: `/home/ubuntu/.local/bin/python3.14`
Python version: 3.14.6 (main, Jun 11 2026, 04:03:53) [Clang 22.1.3 ]
compression.zstd available: True

Cases: 20
Methods: 4
Rows: 80

Classification counts (actual):
- pass: 37
- expected_error: 1
- local_observation: 15
- version_skip: 0
- context_only: 5
- not_applicable: 22
- fail: 0

Expected == actual for all 80 rows.

Verification wall-clock time: ~1 second (clone + checkout + py_compile + run_lab + unittest)

Structured artifacts (`results_rows.json`, `results_rows.csv`) agree with `RESULTS.md` counts.

No sensitive paths (random /tmp paths, OpenClaw internal paths, tokens, API keys) found in committed text artifacts: `cases.json`, `results_rows.json`, `results_rows.csv`, `README.md`, `RESULTS.md`, `hn_thread_evidence.md`, `hn_comments_sanitized.json`.

## What was fixed vs the initial submission

The initial submission (commit `72151902f3021002d82ad97ed95b93e8b477fd2b`) ran under Python 3.12 without `compression.zstd`, producing 31 version_skip rows and 0 Zstandard-validated observations. Static review then found several defects in the unexecuted Python 3.14 branches, all fixed in commit `a7f72d50cce4a11b01ef3bfe73b8b5f90a6b1bed`:

1. **inspect_api**: now actually calls `hasattr()` for each claimed symbol instead of selecting descriptive strings
2. **checksum case**: enables `CompressionParameter.checksum_flag` via `options={checksum_flag: 1}` before corrupting – previously compressed without checksum, causing corruption to go undetected
3. **flush constants**: use `ZstdCompressor.CONTINUE / FLUSH_BLOCK / FLUSH_FRAME` directly instead of guessing 0/1/2
4. **pledged_size / dict API missing**: classify as `version_skip` not `pass`
5. **expected_error**: require `ZstdError` specifically for `pledged_size_mismatch` case
6. **test_lab**: added dedicated tests for `checksum_rejection`, `concatenated_frames`, `pledged_size_mismatch`
7. **test_lab**: relaxed sensitive-path filter to allow legitimate `python_executable` paths

All Zstandard API branches have now been executed and validated under Python 3.14.6 with `compression.zstd` available.

## Documentation commit

This `VERIFY.md` file was committed after the clean-clone verification, as a later documentation commit. The implementation commit verified above (`a7f72d50cce4a11b01ef3bfe73b8b5f90a6b1bed`) does NOT contain this `VERIFY.md`.

The later documentation commit containing `VERIFY.md` was NOT itself fresh-clone verified unless another verification cycle is performed and committed.
