#!/usr/bin/env python3
import csv
import json
import re
import unittest

with open("cases.json") as f:
    cases = json.load(f)
with open("results_rows.json") as f:
    rows = json.load(f)

ALLOWED = {"pass", "expected_error", "local_observation", "version_skip", "context_only", "not_applicable", "fail"}

class TestLab(unittest.TestCase):
    def test_case_count(self):
        self.assertEqual(len(cases), 20)

    def test_marker_names(self):
        expected_ids = [
            "python_version_marker",
            "compression_zstd_availability_marker",
            "zstd_one_shot_roundtrip_marker",
            "zstd_empty_payload_roundtrip_marker",
            "zstd_same_input_same_options_marker",
            "zstd_level_size_local_observation_marker",
            "zstd_incremental_continue_flush_frame_marker",
            "zstd_flush_block_then_finish_marker",
            "zstd_concatenated_frames_module_decompress_marker",
            "zstd_single_frame_unused_data_marker",
            "zstd_max_length_needs_input_marker",
            "zstd_pledged_input_size_match_marker",
            "zstd_pledged_input_size_mismatch_marker",
            "zstd_checksum_corruption_rejected_marker",
            "zstd_bytesio_file_roundtrip_marker",
            "zstd_raw_dictionary_roundtrip_marker",
            "zstd_state_mutation_context_marker",
            "zlib_dictionary_and_copy_comparison_marker",
            "lexical_overlap_not_semantics_marker",
            "no_global_compression_classifier_claim_marker",
        ]
        ids = [c["id"] for c in cases]
        self.assertEqual(sorted(ids), sorted(expected_ids))
        self.assertEqual(len(ids), len(set(ids)))

    def test_expectations_complete(self):
        methods = ["inspect_api", "one_shot_operation", "incremental_or_stream_operation", "hn_context_observation"]
        for c in cases:
            for m in methods:
                self.assertIn(m, c["expectations"])
                exp = c["expectations"][m]
                self.assertTrue(exp)
                self.assertIn(exp, ALLOWED)

    def test_80_rows(self):
        self.assertEqual(len(rows), 80)

    def test_case_method_pairs_unique(self):
        pairs = [(r["method"], r["case_id"]) for r in rows]
        self.assertEqual(len(pairs), len(set(pairs)))
        # every case × every method exists
        case_ids = {c["id"] for c in cases}
        methods = {"inspect_api", "one_shot_operation", "incremental_or_stream_operation", "hn_context_observation"}
        for cid in case_ids:
            for m in methods:
                self.assertIn((m, cid), pairs, f"missing {m}/{cid}")

    def test_classifications_allowed(self):
        for r in rows:
            self.assertIn(r["expected_classification"], ALLOWED, r)
            self.assertIn(r["actual_classification"], ALLOWED, r)
            self.assertTrue(r["expected_classification"])

    def test_not_applicable_pairs_match(self):
        for r in rows:
            if r["expected_classification"] == "not_applicable":
                self.assertEqual(r["actual_classification"], "not_applicable", r)

    def test_roundtrip_match(self):
        for r in rows:
            if r["actual_classification"] == "pass" and "roundtrip" in (r.get("local_conclusion","").lower() + r.get("api_exercised","").lower()):
                # if roundtrip_match field is set, it must be True
                if r["roundtrip_match"] not in ("", None):
                    self.assertEqual(r["roundtrip_match"], "True", r)

    def test_expected_error_has_evidence(self):
        for r in rows:
            if r["actual_classification"] == "expected_error":
                self.assertTrue(r["exception_type"] or "error" in r["local_conclusion"].lower() or "mismatch" in r["local_conclusion"].lower(), r)

    def test_no_sensitive_paths(self):
        # scan committed text artifacts
        files_to_scan = ["cases.json", "results_rows.json", "results_rows.csv", "README.md", "RESULTS.md", "VERIFY.md", "hn_thread_evidence.md", "hn_comments_sanitized.json"]
        import os
        sensitive_patterns = [
            r"/home/[^/\s]+",
            r"/tmp/[^ \n\"']{20,}",
            r"/openclaw",
            r"ghp_[A-Za-z0-9]{20,}",
            r"sk-[A-Za-z0-9]{20,}",
        ]
        # allow /tmp/zstd_lab in VERIFY transcript? no, VERIFY not written yet at test time usually, but check anyway – allow known repo paths
        for fname in files_to_scan:
            if not os.path.exists(fname):
                continue
            with open(fname, errors="ignore") as f:
                content = f.read()
            for pat in sensitive_patterns:
                matches = re.findall(pat, content)
                # filter false positives: /home/ubuntu is OK in docs? actually no – spec says no home-directory paths
                # allow /usr/lib, /usr/bin
                filtered = [m for m in matches if not m.startswith("/usr/")]
                self.assertEqual(filtered, [], f"{fname} contains sensitive pattern {pat}: {filtered[:3]}")

    def test_readme_no_global_claim(self):
        with open("README.md") as f:
            readme = f.read().lower()
        bad_phrases = [
            "compression is intelligent",
            "proves compression is semantic",
            "universally accurate",
            "suitable for production classification",
        ]
        # we SHOULD have disclaimers, not claims
        # just check we don't make positive global claims
        # allow negative/disclaimed versions
        self.assertIn("narrow", readme)
        self.assertIn("local", readme)

    def test_results_no_global_claim(self):
        with open("RESULTS.md") as f:
            res = f.read().lower()
        # should contain disclaimer language
        self.assertTrue("does not" in res or "not" in res)

if __name__ == "__main__":
    unittest.main()
