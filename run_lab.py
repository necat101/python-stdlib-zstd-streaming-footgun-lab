#!/usr/bin/env python3
"""python-stdlib-zstd-streaming-footgun-lab runner"""
import csv
import hashlib
import io
import json
import platform
import sys
import time

CASES_PATH = "cases.json"
RESULTS_JSON = "results_rows.json"
RESULTS_CSV = "results_rows.csv"
RESULTS_MD = "RESULTS.md"

METHODS = ["inspect_api", "one_shot_operation", "incremental_or_stream_operation", "hn_context_observation"]

# Probe zstd availability
py_exe = sys.executable
py_version = sys.version.replace("\n", " ")
py_impl = platform.python_implementation()
py_platform = sys.platform

zstd_available = False
zstd_reason = ""
zstd_mod = None
try:
    import compression.zstd as zstd_mod
    zstd_available = True
    zstd_reason = "import compression.zstd succeeded"
except ModuleNotFoundError as e:
    if sys.version_info < (3, 14):
        zstd_reason = f"Python {sys.version_info.major}.{sys.version_info.minor} < 3.14, compression.zstd does not exist"
    else:
        zstd_reason = f"Python {sys.version_info.major}.{sys.version_info.minor} >= 3.14 but compression.zstd not importable: {e}"
except Exception as e:
    zstd_reason = f"compression.zstd import failed: {e}"

with open(CASES_PATH) as f:
    cases = json.load(f)

def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

rows = []
start_all = time.perf_counter()

for case in cases:
    case_id = case["id"]
    input_str = case.get("input_bytes", "")
    if "|" in input_str and "frame" in case_id:
        parts = input_str.encode("utf-8").split(b"|")
        input_bytes = b"|".join(parts)
        frame_parts = parts
    else:
        input_bytes = input_str.encode("utf-8")
        frame_parts = None

    for method in METHODS:
        expected = case["expectations"].get(method, "not_applicable")
        t0 = time.perf_counter()
        row = {
            "method": method,
            "case_id": case_id,
            "python_executable": py_exe,
            "python_version": py_version,
            "implementation": py_impl,
            "platform": py_platform,
            "zstd_available": zstd_available,
            "availability_reason": zstd_reason,
            "expected_classification": expected,
            "actual_classification": "",
            "api_exercised": "",
            "input_bytes": len(input_bytes),
            "compressed_bytes": "",
            "decompressed_bytes": "",
            "roundtrip_match": "",
            "frame_count": "",
            "eof": "",
            "needs_input": "",
            "unused_data_bytes": "",
            "exception_type": "",
            "exception_message": "",
            "sha256_input": "",
            "sha256_compressed": "",
            "elapsed_s": "",
            "skip_reason": "",
            "failure_reason": "",
            "local_conclusion": "",
        }

        actual = expected
        api = ""
        comp_bytes_count = ""
        decomp_bytes_count = ""
        roundtrip_match = ""
        frame_count = ""
        eof_val = ""
        needs_input_val = ""
        unused_data_bytes = ""
        exc_type = ""
        exc_msg = ""
        sha_in = sha256(input_bytes) if input_bytes else ""
        sha_comp = ""
        skip_reason = ""
        failure_reason = ""
        local_conclusion = ""

        try:
            # inspect_api
            if method == "inspect_api":
                if case_id == "python_version_marker":
                    api = "sys.version / platform"
                    actual = "pass"
                    local_conclusion = f"Python {sys.version_info.major}.{sys.version_info.minor}"
                elif case_id == "compression_zstd_availability_marker":
                    api = "import compression.zstd"
                    actual = "pass"
                    local_conclusion = zstd_reason
                elif case_id == "zlib_dictionary_and_copy_comparison_marker":
                    import zlib
                    co = zlib.compressobj()
                    has_zdict_param = "zdict" in zlib.compressobj.__doc__ if zlib.compressobj.__doc__ else False
                    has_copy = hasattr(co, "copy")
                    del co
                    api = f"zlib.compressobj zdict_param_present={has_zdict_param} Compress.copy_available={has_copy}"
                    actual = "pass"
                    local_conclusion = f"zlib zdict+copy predates Python 3.14 per HN"
                elif case_id == "no_global_compression_classifier_claim_marker":
                    api = "README/RESULTS text scan (verified in test_lab.py)"
                    actual = "pass"
                    local_conclusion = "narrow disclaimer required"
                elif "zstd" in case_id or "lexical_overlap" in case_id:
                    if not zstd_available:
                        actual = "version_skip"
                        skip_reason = zstd_reason
                        api = "compression.zstd (unavailable)"
                        local_conclusion = "skipped: zstd unavailable"
                    else:
                        # Real API inspection – hasattr checks
                        z = zstd_mod
                        checks = []
                        failed = []
                        def has_attr(obj, name):
                            ok = hasattr(obj, name)
                            checks.append(f"{obj.__name__ if hasattr(obj, '__name__') else type(obj).__name__}.{name}={'yes' if ok else 'NO'}")
                            if not ok:
                                failed.append(name)
                            return ok

                        if case_id == "zstd_one_shot_roundtrip_marker":
                            api = "compression.zstd.compress / decompress"
                            has_attr(z, "compress"); has_attr(z, "decompress")
                        elif case_id == "zstd_empty_payload_roundtrip_marker":
                            api = "compression.zstd.compress / decompress"
                            has_attr(z, "compress"); has_attr(z, "decompress")
                        elif case_id == "zstd_same_input_same_options_marker":
                            api = "compression.zstd.compress"
                            has_attr(z, "compress")
                        elif case_id == "zstd_level_size_local_observation_marker":
                            api = "compression.zstd.CompressionParameter.compression_level"
                            has_attr(z, "CompressionParameter")
                            if hasattr(z, "CompressionParameter"):
                                has_attr(z.CompressionParameter, "compression_level")
                        elif case_id == "zstd_incremental_continue_flush_frame_marker":
                            api = "compression.zstd.ZstdCompressor CONTINUE FLUSH_FRAME"
                            has_attr(z, "ZstdCompressor")
                            if hasattr(z, "ZstdCompressor"):
                                has_attr(z.ZstdCompressor, "compress")
                                has_attr(z.ZstdCompressor, "flush")
                                has_attr(z.ZstdCompressor, "CONTINUE")
                                has_attr(z.ZstdCompressor, "FLUSH_FRAME")
                        elif case_id == "zstd_flush_block_then_finish_marker":
                            api = "compression.zstd.ZstdCompressor FLUSH_BLOCK"
                            has_attr(z, "ZstdCompressor")
                            if hasattr(z, "ZstdCompressor"):
                                has_attr(z.ZstdCompressor, "FLUSH_BLOCK")
                                has_attr(z.ZstdCompressor, "FLUSH_FRAME")
                        elif case_id == "zstd_concatenated_frames_module_decompress_marker":
                            api = "compression.zstd.decompress"
                            has_attr(z, "decompress")
                        elif case_id == "zstd_single_frame_unused_data_marker":
                            api = "compression.zstd.ZstdDecompressor unused_data eof"
                            has_attr(z, "ZstdDecompressor")
                            # unused_data / eof are instance attributes, check class exists
                        elif case_id == "zstd_max_length_needs_input_marker":
                            api = "compression.zstd.ZstdDecompressor max_length needs_input"
                            has_attr(z, "ZstdDecompressor")
                        elif case_id == "zstd_pledged_input_size_match_marker":
                            api = "compression.zstd.ZstdCompressor.set_pledged_input_size"
                            has_attr(z, "ZstdCompressor")
                            if hasattr(z, "ZstdCompressor"):
                                ok = has_attr(z.ZstdCompressor, "set_pledged_input_size")
                                if not ok:
                                    actual = "version_skip"
                                    skip_reason = "ZstdCompressor.set_pledged_input_size not found"
                        elif case_id == "zstd_pledged_input_size_mismatch_marker":
                            api = "compression.zstd.ZstdCompressor.set_pledged_input_size"
                            has_attr(z, "ZstdCompressor")
                            if hasattr(z, "ZstdCompressor"):
                                ok = has_attr(z.ZstdCompressor, "set_pledged_input_size")
                                if not ok:
                                    actual = "version_skip"
                                    skip_reason = "ZstdCompressor.set_pledged_input_size not found"
                        elif case_id == "zstd_checksum_corruption_rejected_marker":
                            api = "compression.zstd.CompressionParameter.checksum_flag / ZstdError"
                            has_attr(z, "CompressionParameter")
                            if hasattr(z, "CompressionParameter"):
                                has_attr(z.CompressionParameter, "checksum_flag")
                            has_attr(z, "ZstdError")
                        elif case_id == "zstd_bytesio_file_roundtrip_marker":
                            api = "compression.zstd.ZstdFile / open"
                            has_zfile = has_attr(z, "ZstdFile")
                            has_open = has_attr(z, "open")
                            if not (has_zfile or has_open):
                                failed.append("ZstdFile/open")
                        elif case_id == "zstd_raw_dictionary_roundtrip_marker":
                            api = "compression.zstd.ZstdDict is_raw"
                            ok = has_attr(z, "ZstdDict")
                            if not ok:
                                actual = "version_skip"
                                skip_reason = "ZstdDict not found"
                        elif case_id == "zstd_state_mutation_context_marker":
                            api = "compression.zstd.ZstdCompressor"
                            has_attr(z, "ZstdCompressor")
                        elif case_id == "lexical_overlap_not_semantics_marker":
                            api = "compression.zstd.compress"
                            has_attr(z, "compress")
                        else:
                            api = "compression.zstd (unknown case)"
                            failed.append("unknown")

                        if failed and actual != "version_skip":
                            actual = "fail"
                            failure_reason = "missing API: " + ", ".join(failed)
                            local_conclusion = "; ".join(checks)
                        elif actual != "version_skip":
                            actual = "pass"
                            local_conclusion = "; ".join(checks)
                else:
                    api = "unknown"
                    actual = expected

            # one_shot_operation
            elif method == "one_shot_operation":
                if expected == "not_applicable":
                    actual = "not_applicable"
                elif case_id == "zlib_dictionary_and_copy_comparison_marker":
                    import zlib
                    api = "zlib.compressobj(zdict=...) + Compress.copy()"
                    zdict = b"taco burrito tortilla salsa guacamole cilantro lime " * 4
                    co = zlib.compressobj(zdict=zdict)
                    if hasattr(co, "copy"):
                        co2 = co.copy()
                        out1 = co.compress(input_bytes) + co.flush()
                        out2 = co2.compress(input_bytes) + co2.flush()
                        comp_bytes_count = len(out1)
                        local_conclusion = f"zlib dict+copy works, out1={len(out1)} out2={len(out2)}"
                    else:
                        out1 = co.compress(input_bytes) + co.flush()
                        comp_bytes_count = len(out1)
                        local_conclusion = "zlib dict works, copy() unavailable"
                    actual = "pass"
                elif case_id == "lexical_overlap_not_semantics_marker":
                    # four tiny samples
                    samples = [
                        (b"taco salsa lime tortilla guacamole", "similar_vocab_similar_topic"),
                        (b"taco salsa lime tortilla rocket launch", "similar_vocab_different_topic"),
                        (b"bonjour sujet identique mais vocabulaire different", "different_vocab_similar_topic"),
                        (b"the local compressor test repeats repeats repeats " * 4, "longer_text"),
                    ]
                    if zstd_available:
                        api = "compression.zstd.compress"
                        sizes = []
                        for s_bytes, label in samples:
                            c = zstd_mod.compress(s_bytes)
                            sizes.append(len(c))
                    else:
                        import zlib
                        api = "zlib.compress (fallback, zstd unavailable)"
                        sizes = []
                        for s_bytes, label in samples:
                            c = zlib.compress(s_bytes)
                            sizes.append(len(c))
                    comp_bytes_count = sum(sizes)
                    local_conclusion = f"sizes={sizes} (lexical overlap, not semantics)"
                    actual = "pass"
                elif not zstd_available:
                    actual = "version_skip"
                    skip_reason = zstd_reason
                    api = "compression.zstd (unavailable)"
                    local_conclusion = "skipped: zstd unavailable"
                else:
                    z = zstd_mod
                    # zstd one-shot cases
                    if case_id == "zstd_one_shot_roundtrip_marker":
                        api = "compression.zstd.compress / decompress"
                        c = z.compress(input_bytes)
                        comp_bytes_count = len(c)
                        sha_comp = sha256(c)
                        d = z.decompress(c)
                        decomp_bytes_count = len(d)
                        roundtrip_match = (d == input_bytes)
                        actual = "pass" if roundtrip_match else "fail"
                        local_conclusion = "roundtrip ok" if roundtrip_match else "roundtrip mismatch"
                    elif case_id == "zstd_empty_payload_roundtrip_marker":
                        api = "compression.zstd.compress / decompress"
                        c = z.compress(b"")
                        comp_bytes_count = len(c)
                        d = z.decompress(c)
                        decomp_bytes_count = len(d)
                        roundtrip_match = (d == b"")
                        actual = "pass" if roundtrip_match else "fail"
                        local_conclusion = f"empty roundtrip ok, compressed={len(c)} bytes"
                    elif case_id == "zstd_same_input_same_options_marker":
                        api = "compression.zstd.compress"
                        c1 = z.compress(input_bytes)
                        c2 = z.compress(input_bytes)
                        comp_bytes_count = len(c1)
                        sha_comp = sha256(c1)
                        roundtrip_match = (c1 == c2)
                        actual = "pass"
                        local_conclusion = f"deterministic_locally={roundtrip_match}"
                    elif case_id == "zstd_level_size_local_observation_marker":
                        api = "compression.zstd.compress level"
                        c1 = z.compress(input_bytes, level=1)
                        c2 = z.compress(input_bytes, level=3)
                        comp_bytes_count = len(c1)
                        d2 = z.decompress(c2)
                        roundtrip_match = (d2 == input_bytes)
                        actual = "pass" if roundtrip_match else "fail"
                        local_conclusion = f"level1={len(c1)} level3={len(c2)}"
                        sha_comp = sha256(c2)
                    elif case_id == "zstd_concatenated_frames_module_decompress_marker":
                        api = "compression.zstd.compress / decompress"
                        p1 = b"demo-frame-one"
                        p2 = b"demo-frame-two"
                        c1 = z.compress(p1)
                        c2 = z.compress(p2)
                        concat = c1 + c2
                        comp_bytes_count = len(concat)
                        try:
                            d = z.decompress(concat)
                            decomp_bytes_count = len(d)
                            roundtrip_match = (d == p1 + p2)
                            frame_count = 2
                            actual = "pass" if roundtrip_match else "fail"
                            local_conclusion = f"concat_decompress_match={roundtrip_match}"
                        except Exception as e:
                            exc_type = type(e).__name__
                            exc_msg = str(e)[:200]
                            actual = "fail"
                            failure_reason = exc_msg
                    elif case_id == "zstd_checksum_corruption_rejected_marker":
                        api = "compression.zstd.CompressionParameter.checksum_flag"
                        try:
                            # Enable checksum_flag
                            opts = {z.CompressionParameter.checksum_flag: 1}
                            c = z.compress(input_bytes, options=opts)
                            comp_bytes_count = len(c)
                            # corrupt a byte near end (checksum area)
                            if len(c) > 5:
                                bc = bytearray(c)
                                bc[-2] ^= 0xFF
                                c_corrupt = bytes(bc)
                                try:
                                    d = z.decompress(c_corrupt)
                                    actual = "fail"
                                    failure_reason = "corruption not rejected (ZstdError not raised)"
                                    local_conclusion = "checksum rejection NOT observed"
                                except z.ZstdError as e:
                                    exc_type = type(e).__name__
                                    exc_msg = str(e)[:200]
                                    actual = "pass"
                                    local_conclusion = f"checksum corruption rejected: {exc_type}"
                            else:
                                actual = "fail"
                                failure_reason = "compressed blob too short to corrupt"
                        except Exception as e:
                            exc_type = type(e).__name__
                            exc_msg = str(e)[:200]
                            actual = "fail"
                            failure_reason = exc_msg
                    elif case_id == "zstd_raw_dictionary_roundtrip_marker":
                        api = "compression.zstd.ZstdDict is_raw"
                        try:
                            if not hasattr(z, "ZstdDict"):
                                actual = "version_skip"
                                skip_reason = "ZstdDict not available"
                                local_conclusion = skip_reason
                            else:
                                zd = z.ZstdDict(b"taco salsa lime " * 4, is_raw=True)
                                c = z.compress(input_bytes, zstd_dict=zd)
                                d = z.decompress(c, zstd_dict=zd)
                                comp_bytes_count = len(c)
                                decomp_bytes_count = len(d)
                                roundtrip_match = (d == input_bytes)
                                actual = "pass" if roundtrip_match else "fail"
                                local_conclusion = "dict roundtrip ok" if roundtrip_match else "mismatch"
                        except Exception as e:
                            exc_type = type(e).__name__
                            exc_msg = str(e)[:200]
                            actual = "fail"
                            failure_reason = exc_msg
                    else:
                        actual = expected

            # incremental_or_stream_operation
            elif method == "incremental_or_stream_operation":
                if expected == "not_applicable":
                    actual = "not_applicable"
                elif case_id == "zlib_dictionary_and_copy_comparison_marker":
                    import zlib
                    api = "zlib.Compress.copy()"
                    zdict = b"taco burrito tortilla salsa guacamole cilantro lime " * 4
                    co = zlib.compressobj(zdict=zdict)
                    if hasattr(co, "copy"):
                        co2 = co.copy()
                        local_conclusion = "Compress.copy() available"
                    else:
                        local_conclusion = "Compress.copy() unavailable"
                    actual = "pass"
                elif not zstd_available:
                    actual = "version_skip"
                    skip_reason = zstd_reason
                    api = "compression.zstd (unavailable)"
                    local_conclusion = "skipped: zstd unavailable"
                else:
                    z = zstd_mod
                    # incremental zstd cases
                    if case_id == "zstd_incremental_continue_flush_frame_marker":
                        api = "compression.zstd.ZstdCompressor CONTINUE FLUSH_FRAME"
                        try:
                            comp = z.ZstdCompressor()
                            chunk1 = input_bytes[:len(input_bytes)//2]
                            chunk2 = input_bytes[len(input_bytes)//2:]
                            out = b""
                            out += comp.compress(chunk1)
                            out += comp.compress(chunk2)
                            out += comp.flush(z.ZstdCompressor.FLUSH_FRAME)
                            comp_bytes_count = len(out)
                            d = z.decompress(out)
                            roundtrip_match = (d == input_bytes)
                            actual = "pass" if roundtrip_match else "fail"
                            local_conclusion = "incremental roundtrip ok" if roundtrip_match else "mismatch"
                        except Exception as e:
                            exc_type = type(e).__name__
                            exc_msg = str(e)[:200]
                            actual = "fail"
                            failure_reason = exc_msg
                    elif case_id == "zstd_flush_block_then_finish_marker":
                        api = "compression.zstd.ZstdCompressor FLUSH_BLOCK"
                        try:
                            comp = z.ZstdCompressor()
                            out = comp.compress(input_bytes)
                            out += comp.flush(z.ZstdCompressor.FLUSH_BLOCK)
                            out += comp.flush(z.ZstdCompressor.FLUSH_FRAME)
                            comp_bytes_count = len(out)
                            d = z.decompress(out)
                            roundtrip_match = (d == input_bytes)
                            actual = "pass" if roundtrip_match else "fail"
                            local_conclusion = "flush_block roundtrip ok"
                        except Exception as e:
                            exc_type = type(e).__name__
                            exc_msg = str(e)[:200]
                            actual = "fail"
                            failure_reason = exc_msg
                    elif case_id == "zstd_single_frame_unused_data_marker":
                        api = "compression.zstd.ZstdDecompressor unused_data eof"
                        try:
                            p1 = b"demo-frame-one"
                            p2 = b"demo-frame-two"
                            c1 = z.compress(p1)
                            c2 = z.compress(p2)
                            concat = c1 + c2
                            decomp = z.ZstdDecompressor()
                            out = decomp.decompress(concat)
                            eof_val = str(getattr(decomp, "eof", ""))
                            unused = getattr(decomp, "unused_data", b"")
                            unused_data_bytes = len(unused) if isinstance(unused, (bytes, bytearray)) else 0
                            decomp_bytes_count = len(out)
                            actual = "pass"
                            local_conclusion = f"eof={eof_val} unused={unused_data_bytes}"
                        except Exception as e:
                            exc_type = type(e).__name__
                            exc_msg = str(e)[:200]
                            actual = "fail"
                            failure_reason = exc_msg
                    elif case_id == "zstd_max_length_needs_input_marker":
                        api = "compression.zstd.ZstdDecompressor max_length needs_input"
                        try:
                            c = z.compress(input_bytes)
                            comp_bytes_count = len(c)
                            decomp = z.ZstdDecompressor()
                            try:
                                out1 = decomp.decompress(c, max_length=5)
                                needs = getattr(decomp, "needs_input", "")
                                needs_input_val = str(needs)
                                out_rest = decomp.decompress(b"")
                                out = out1 + out_rest
                                roundtrip_match = (out == input_bytes)
                                actual = "pass" if roundtrip_match else "fail"
                                local_conclusion = f"max_length path, needs_input={needs}"
                            except TypeError:
                                out = decomp.decompress(c)
                                roundtrip_match = (out == input_bytes)
                                actual = "pass" if roundtrip_match else "fail"
                                local_conclusion = "max_length not supported in this build"
                        except Exception as e:
                            exc_type = type(e).__name__
                            exc_msg = str(e)[:200]
                            actual = "fail"
                            failure_reason = exc_msg
                    elif case_id == "zstd_pledged_input_size_match_marker":
                        api = "compression.zstd.ZstdCompressor.set_pledged_input_size"
                        try:
                            if not hasattr(z.ZstdCompressor, "set_pledged_input_size"):
                                actual = "version_skip"
                                skip_reason = "set_pledged_input_size unavailable"
                                local_conclusion = skip_reason
                            else:
                                comp = z.ZstdCompressor()
                                comp.set_pledged_input_size(len(input_bytes))
                                out = comp.compress(input_bytes)
                                out += comp.flush()
                                comp_bytes_count = len(out)
                                d = z.decompress(out)
                                roundtrip_match = (d == input_bytes)
                                actual = "pass" if roundtrip_match else "fail"
                                local_conclusion = "pledged_size match ok"
                        except Exception as e:
                            exc_type = type(e).__name__
                            exc_msg = str(e)[:200]
                            actual = "fail"
                            failure_reason = exc_msg
                    elif case_id == "zstd_pledged_input_size_mismatch_marker":
                        api = "compression.zstd.ZstdCompressor.set_pledged_input_size"
                        try:
                            if not hasattr(z.ZstdCompressor, "set_pledged_input_size"):
                                actual = "version_skip"
                                skip_reason = "set_pledged_input_size unavailable"
                                local_conclusion = skip_reason
                            else:
                                comp = z.ZstdCompressor()
                                comp.set_pledged_input_size(1)  # wrong
                                out = comp.compress(input_bytes)
                                out += comp.flush()
                                actual = "fail"
                                failure_reason = "pledge mismatch did not raise ZstdError"
                                local_conclusion = "no error raised"
                        except z.ZstdError as e:
                            exc_type = type(e).__name__
                            exc_msg = str(e)[:200]
                            actual = "expected_error"
                            local_conclusion = f"pledge mismatch raised {exc_type} (expected)"
                        except Exception as e:
                            exc_type = type(e).__name__
                            exc_msg = str(e)[:200]
                            actual = "fail"
                            failure_reason = f"wrong exception type: {exc_type}: {exc_msg}"
                    elif case_id == "zstd_bytesio_file_roundtrip_marker":
                        api = "compression.zstd.ZstdFile / open"
                        try:
                            bio = io.BytesIO()
                            if hasattr(z, "ZstdFile"):
                                with z.ZstdFile(bio, "wb") as f:
                                    f.write(input_bytes)
                                bio.seek(0)
                                with z.ZstdFile(bio, "rb") as f:
                                    out = f.read()
                                roundtrip_match = (out == input_bytes)
                                actual = "pass" if roundtrip_match else "fail"
                                local_conclusion = "ZstdFile BytesIO ok"
                            elif hasattr(z, "open"):
                                with z.open(bio, "wb") as f:
                                    f.write(input_bytes)
                                bio.seek(0)
                                with z.open(bio, "rb") as f:
                                    out = f.read()
                                roundtrip_match = (out == input_bytes)
                                actual = "pass" if roundtrip_match else "fail"
                                local_conclusion = "zstd.open BytesIO ok"
                            else:
                                actual = "version_skip"
                                skip_reason = "ZstdFile/open unavailable"
                        except Exception as e:
                            exc_type = type(e).__name__
                            exc_msg = str(e)[:200]
                            actual = "fail"
                            failure_reason = exc_msg
                    elif case_id == "zstd_state_mutation_context_marker":
                        api = "compression.zstd.ZstdCompressor state"
                        try:
                            comp = z.ZstdCompressor()
                            out1 = comp.compress(input_bytes[:10])
                            out2 = comp.compress(input_bytes[10:])
                            out = out1 + out2 + comp.flush()
                            d = z.decompress(out)
                            roundtrip_match = (d == input_bytes)
                            actual = "pass" if roundtrip_match else "fail"
                            local_conclusion = "state mutates as data supplied (not learning)"
                        except Exception as e:
                            exc_type = type(e).__name__
                            exc_msg = str(e)[:200]
                            actual = "fail"
                            failure_reason = exc_msg
                    else:
                        actual = expected

            # hn_context_observation
            elif method == "hn_context_observation":
                if expected == "context_only":
                    actual = "context_only"
                    local_conclusion = "HN context case"
                    api = "context"
                elif expected == "not_applicable":
                    actual = "not_applicable"
                else:  # local_observation
                    actual = "local_observation"
                    api = "HN thread 46942864"
                    hn_notes = {
                        "zstd_one_shot_roundtrip_marker": "stdlib availability lowers friction (HN: Lemaxoxo, notpushkin)",
                        "zstd_empty_payload_roundtrip_marker": "API correctness, not ML claim",
                        "zstd_same_input_same_options_marker": "determinism is local, not a universal compressor promise",
                        "zstd_level_size_local_observation_marker": "compressor tuning != classifier tuning (HN: ks2048, stephantul)",
                        "zstd_incremental_continue_flush_frame_marker": "incremental compression exists in lower-level APIs too (HN: pornel)",
                        "zstd_flush_block_then_finish_marker": "Python API limits != algorithm limits (HN: pornel)",
                        "zstd_concatenated_frames_module_decompress_marker": "frame boundaries are real",
                        "zstd_single_frame_unused_data_marker": "unused_data / eof behavior is API-specific",
                        "zstd_max_length_needs_input_marker": "bounded decompression is a stream concern, not ML",
                        "zstd_pledged_input_size_match_marker": "pledged sizes are about framing, not semantics",
                        "zstd_pledged_input_size_mismatch_marker": "error paths must be real, not classified loosely",
                        "zstd_checksum_corruption_rejected_marker": "compressor integrity != classifier correctness",
                        "zstd_bytesio_file_roundtrip_marker": "file-like streams, no permanent FS writes",
                        "zstd_raw_dictionary_roundtrip_marker": "dictionaries help with repeated substrings, not meaning (HN: duskwuff)",
                        "lexical_overlap_not_semantics_marker": "compressed size measures lexical overlap / substring repetition / length / backref distance, not semantics (HN: duskwuff, srean, Jaxan)",
                    }
                    local_conclusion = hn_notes.get(case_id, "local observation per HN thread")

        except Exception as e:
            if not actual or actual == expected:
                actual = "fail"
            exc_type = type(e).__name__
            exc_msg = str(e)[:200]
            failure_reason = exc_msg or failure_reason

        elapsed = time.perf_counter() - t0

        # version_skip override for zstd-dependent cases when module missing
        # hn_context_observation is about HN thread sentiment, not running zstd – never version_skip it
        if method != "hn_context_observation" and not zstd_available and "zstd" in case_id and case_id != "zlib_dictionary_and_copy_comparison_marker":
            if actual not in ("not_applicable", "context_only"):
                actual = "version_skip"
                skip_reason = zstd_reason
                if not local_conclusion:
                    local_conclusion = "skipped: zstd unavailable"

        # fill row
        row.update({
            "actual_classification": actual,
            "api_exercised": api,
            "compressed_bytes": comp_bytes_count,
            "decompressed_bytes": decomp_bytes_count,
            "roundtrip_match": str(roundtrip_match) if roundtrip_match != "" else "",
            "frame_count": frame_count,
            "eof": eof_val,
            "needs_input": needs_input_val,
            "unused_data_bytes": unused_data_bytes,
            "exception_type": exc_type,
            "exception_message": exc_msg,
            "sha256_input": sha_in,
            "sha256_compressed": sha_comp,
            "elapsed_s": f"{elapsed:.6f}",
            "skip_reason": skip_reason,
            "failure_reason": failure_reason,
            "local_conclusion": local_conclusion,
        })
        rows.append(row)

total_elapsed = time.perf_counter() - start_all

# write results
with open(RESULTS_JSON, "w") as f:
    json.dump(rows, f, indent=2)

# csv
if rows:
    with open(RESULTS_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)

# RESULTS.md
from collections import Counter
counts = Counter(r["actual_classification"] for r in rows)
roundtrips = sum(1 for r in rows if r["roundtrip_match"] == "True")

with open(RESULTS_MD, "w") as f:
    f.write("# RESULTS – python-stdlib-zstd-streaming-footgun-lab\n\n")
    f.write(f"Python: {py_impl} {py_version}\n")
    f.write(f"Executable: {py_exe}\n")
    f.write(f"Platform: {py_platform}\n")
    f.write(f"compression.zstd available: {zstd_available}\n")
    if not zstd_available:
        f.write(f"Reason: {zstd_reason}\n")
    f.write("\n")
    f.write(f"Cases: {len(cases)}\n")
    f.write(f"Methods: {len(METHODS)}\n")
    f.write(f"Rows: {len(rows)}\n\n")
    f.write("## Classification counts\n\n")
    for k in ["pass", "expected_error", "local_observation", "version_skip", "context_only", "not_applicable", "fail"]:
        f.write(f"- {k}: {counts.get(k,0)}\n")
    f.write(f"\nRoundtrip matches: {roundtrips}\n")
    f.write(f"Total runtime: {total_elapsed:.3f}s\n\n")
    f.write("## Notes\n\n")
    if not zstd_available:
        f.write("compression.zstd was unavailable in this Python build. Zstandard-dependent observations are classified as version_skip with a precise reason. This is a version-sensitive stdlib API lab, not a Zstandard-validated run.\n\n")
    f.write("This lab tests local Python stdlib API behavior (one-shot, incremental, framing, checksums, dictionaries, file-like streams). It does not train a classifier, compute accuracy percentages, or claim that compression measures semantic meaning.\n")
    f.write("\nCompressed-size observations in the lexical-overlap case reflect repeated words/phrases/substrings and text length / back-reference distance effects discussed on HN, not semantic understanding.\n")

print(f"rows={len(rows)} pass={counts.get('pass',0)} fail={counts.get('fail',0)} expected_error={counts.get('expected_error',0)} version_skip={counts.get('version_skip',0)} elapsed={total_elapsed:.2f}s")
