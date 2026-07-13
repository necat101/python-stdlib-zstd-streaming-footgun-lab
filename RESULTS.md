# RESULTS – python-stdlib-zstd-streaming-footgun-lab

Python: CPython 3.14.6 (main, Jun 11 2026, 04:03:53) [Clang 22.1.3 ]
Executable: /home/ubuntu/.local/bin/python3.14
Platform: linux
compression.zstd available: True

Cases: 20
Methods: 4
Rows: 80

## Classification counts

- pass: 37
- expected_error: 1
- local_observation: 15
- version_skip: 0
- context_only: 5
- not_applicable: 22
- fail: 0

Roundtrip matches: 12
Total runtime: 0.004s

## Notes

This lab tests local Python stdlib API behavior (one-shot, incremental, framing, checksums, dictionaries, file-like streams). It does not train a classifier, compute accuracy percentages, or claim that compression measures semantic meaning.

Compressed-size observations in the lexical-overlap case reflect repeated words/phrases/substrings and text length / back-reference distance effects discussed on HN, not semantic understanding.
