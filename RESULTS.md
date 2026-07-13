# RESULTS – python-stdlib-zstd-streaming-footgun-lab

Python: CPython 3.12.3 (main, Jun 19 2026, 12:46:00) [GCC 13.3.0]
Executable: /usr/bin/python3
Platform: linux
compression.zstd available: False
Reason: Python 3.12 < 3.14, compression.zstd does not exist

Cases: 20
Methods: 4
Rows: 80

## Classification counts

- pass: 7
- expected_error: 0
- local_observation: 15
- version_skip: 31
- context_only: 5
- not_applicable: 22
- fail: 0

Roundtrip matches: 0
Total runtime: 0.003s

## Notes

compression.zstd was unavailable in this Python build. Zstandard-dependent observations are classified as version_skip with a precise reason. This is a version-sensitive stdlib API lab, not a Zstandard-validated run.

This lab tests local Python stdlib API behavior (one-shot, incremental, framing, checksums, dictionaries, file-like streams). It does not train a classifier, compute accuracy percentages, or claim that compression measures semantic meaning.

Compressed-size observations in the lexical-overlap case reflect repeated words/phrases/substrings and text length / back-reference distance effects discussed on HN, not semantic understanding.
