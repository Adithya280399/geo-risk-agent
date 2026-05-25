import logging, time
from agents.monitor_agent  import run as monitor_run
from agents.country_agent  import run as country_run
from agents.report_agent   import run as report_run

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

TARGET_COUNTRIES = ["Iran", "China", "Russia", "Ukraine", "U.S."]

def run(query: str) -> dict:
    log.info(f"Orchestrator starting for query: '{query}'")
    start = time.time()

    log.info("Step 1/3 — MonitorAgent scanning for high-risk events...")
    monitor_result = monitor_run(threshold=5)

    log.info("Step 2/3 — CountryAgent profiling key nations...")
    country_results = []
    for country in TARGET_COUNTRIES:
        result = country_run(country)
        country_results.append(result)
        log.info(f"  {country}: avg_score={result['avg_risk_score']} "
                 f"category={result['top_risk_category']} "
                 f"articles={result['article_count']}")

    log.info("Step 3/3 — ReportAgent compiling final intelligence report...")
    report_result = report_run(query, monitor_result, country_results)

    total_ms = int((time.time() - start) * 1000)

    log.info(f"Orchestrator complete in {total_ms}ms")

    return {
        "query":           query,
        "monitor_alerts":  monitor_result["count"],
        "countries_profiled": len(country_results),
        "report":          report_result["report"],
        "total_duration_ms": total_ms,
    }

if __name__ == "__main__":
    queries = [
        "What is the current global geopolitical risk landscape?",
        "What are the biggest threats to energy security and global trade?",
    ]

    for query in queries:
        print("\n" + "="*70)
        result = run(query)
        print(f"\nQUERY: {result['query']}")
        print(f"Alerts found: {result['monitor_alerts']}")
        print(f"Countries profiled: {result['countries_profiled']}")
        print(f"Time: {result['total_duration_ms']}ms")
        print("\n" + "="*70)
        print(result["report"])