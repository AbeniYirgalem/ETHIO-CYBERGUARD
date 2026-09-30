from scripts.benchmark_eps import run_benchmark

def test_benchmark_eps_execution():
    # Run a quick 1,000 event benchmark
    report = run_benchmark(total_events=1000, num_workers=2)
    assert report["status"] == "PASS"
    assert report["total_events"] == 1000
    assert report["sustained_eps"] > 0
    assert report["latency_p50_ms"] >= 0
