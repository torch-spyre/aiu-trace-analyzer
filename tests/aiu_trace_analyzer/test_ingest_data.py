# Copyright 2026 IBM Corporation

import zlib

from aiu_trace_analyzer.types import GlobalIngestData
from aiu_trace_analyzer.dialect import InputDialectFLEX, InputDialectTORCH


def _find_colliding_uris(prefix: str) -> tuple[str, str]:
    seen = {}
    for i in range(100000):
        uri = f"{prefix}_{i}.json"
        slot = zlib.crc32(uri.encode()) % GlobalIngestData._JOBHASH_RANGE
        if slot in seen:
            return seen[slot], uri
        seen[slot] = uri
    raise AssertionError("no collision found")


def test_same_uri_gives_same_jobhash():
    GlobalIngestData()
    assert GlobalIngestData.add_job_info("ingest_same.json") == GlobalIngestData.add_job_info("ingest_same.json")


def test_jobhash_is_stable_across_processes():
    GlobalIngestData()
    uri = "ingest_stable.json"
    jobhash = GlobalIngestData.add_job_info(uri)
    assert jobhash == zlib.crc32(uri.encode()) % GlobalIngestData._JOBHASH_RANGE


def test_colliding_uris_keep_their_own_dialect():
    GlobalIngestData()
    uri_a, uri_b = _find_colliding_uris("ingest_collide")
    flex, torch = InputDialectFLEX(), InputDialectTORCH()
    job_a = GlobalIngestData.add_job_info(uri_a, flex)
    job_b = GlobalIngestData.add_job_info(uri_b, torch)
    assert job_a != job_b
    assert GlobalIngestData.get_dialect(job_a) is flex
    assert GlobalIngestData.get_dialect(job_b) is torch
    assert GlobalIngestData.add_job_info(uri_b, torch) == job_b
