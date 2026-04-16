"""
Retrieval evaluation script for the Travel RAG pipeline.

Loads eval_queries.json, runs each query through the live Pinecone
retriever, compares returned results to ground truth expected IDs,
and calculates four standard retrieval metrics:

  Precision@k — of the k results returned, how many are relevant?
  Recall@k    — of all relevant results, how many appeared in top k?
  MRR         — where does the first relevant result appear?
  Hit Rate@k  — did at least one relevant result appear in top k?

Usage:
  python scripts/run_eval.py
  python scripts/run_eval.py --top_k 10
"""

import argparse
import json
import os
import sys
import time

# add the project root to sys.path so we can import from app/
PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, PROJECT_ROOT)

from app.models import TravelIntent
from app.retriever import search


# ---------------------------------------------------------------------------
# paths
# ---------------------------------------------------------------------------
EVAL_PATH = os.path.join(PROJECT_ROOT, "data", "eval_queries.json")
RESULTS_PATH = os.path.join(PROJECT_ROOT, "data", "eval_results.json")


# ---------------------------------------------------------------------------
# metric calculations
# ---------------------------------------------------------------------------
def precision_at_k(retrieved_ids: list[str], relevant_ids: set[str], k: int) -> float:
    """
    Of the top k results returned, how many are in the relevant set?
    Formula: count(relevant in top k) / k
    """
    if k == 0:
        return 0.0
    top_k = retrieved_ids[:k]
    hits = sum(1 for rid in top_k if rid in relevant_ids)
    return hits / k


def recall_at_k(retrieved_ids: list[str], relevant_ids: set[str], k: int) -> float:
    """
    Of ALL relevant results in the database, how many appeared in top k?
    Formula: count(relevant in top k) / total_relevant
    """
    if len(relevant_ids) == 0:
        return 1.0  # nothing to find — trivially perfect recall
    top_k = retrieved_ids[:k]
    hits = sum(1 for rid in top_k if rid in relevant_ids)
    return hits / len(relevant_ids)


def mean_reciprocal_rank(retrieved_ids: list[str], relevant_ids: set[str]) -> float:
    """
    Where does the FIRST relevant result appear?
    Formula: 1 / position_of_first_relevant (1-indexed)
    Returns 0 if no relevant result is found at all.
    """
    for i, rid in enumerate(retrieved_ids):
        if rid in relevant_ids:
            return 1.0 / (i + 1)
    return 0.0


def hit_rate_at_k(retrieved_ids: list[str], relevant_ids: set[str], k: int) -> float:
    """
    Did at LEAST one relevant result appear in top k?
    Returns 1.0 if yes, 0.0 if no.
    """
    top_k = retrieved_ids[:k]
    for rid in top_k:
        if rid in relevant_ids:
            return 1.0
    return 0.0


# ---------------------------------------------------------------------------
# run evaluation
# ---------------------------------------------------------------------------
def run_evaluation(top_k: int = 5) -> dict:
    """
    Load eval queries, run each through Pinecone, calculate metrics.
    Returns a dict with per-query scores and overall averages.
    """
    # load evaluation set
    with open(EVAL_PATH, "r") as f:
        eval_queries = json.load(f)

    print(f"\nRETRIEVAL EVALUATION — {len(eval_queries)} queries, top_k={top_k}")
    print("=" * 80)

    # accumulators for overall averages
    all_scores = {
        "hotel_precision": [],
        "hotel_recall": [],
        "hotel_mrr": [],
        "hotel_hit": [],
        "flight_precision": [],
        "flight_recall": [],
        "flight_mrr": [],
        "flight_hit": [],
    }

    query_results = []

    for i, q in enumerate(eval_queries):
        query_id = q["query_id"]
        description = q["description"]
        intent_data = q["intent"]
        expected_hotels = set(q["expected_hotel_ids"])
        expected_flights = set(q["expected_flight_ids"])

        # build TravelIntent from the query data
        intent = TravelIntent(**intent_data)

        # run the actual Pinecone search
        start = time.time()
        try:
            results = search(intent, top_k=top_k)
        except Exception as e:
            print(f"\n  ERROR on query {query_id}: {e}")
            query_results.append({
                "query_id": query_id,
                "error": str(e),
            })
            continue
        elapsed_ms = round((time.time() - start) * 1000, 1)

        # extract returned IDs
        returned_hotel_ids = [m["id"] for m in results.get("hotels", [])]
        returned_flight_ids = [m["id"] for m in results.get("flights", [])]

        # calculate metrics for hotels
        h_prec = precision_at_k(returned_hotel_ids, expected_hotels, top_k)
        h_rec = recall_at_k(returned_hotel_ids, expected_hotels, top_k)
        h_mrr = mean_reciprocal_rank(returned_hotel_ids, expected_hotels)
        h_hit = hit_rate_at_k(returned_hotel_ids, expected_hotels, top_k)

        # calculate metrics for flights
        f_prec = precision_at_k(returned_flight_ids, expected_flights, top_k)
        f_rec = recall_at_k(returned_flight_ids, expected_flights, top_k)
        f_mrr = mean_reciprocal_rank(returned_flight_ids, expected_flights)
        f_hit = hit_rate_at_k(returned_flight_ids, expected_flights, top_k)

        # store
        all_scores["hotel_precision"].append(h_prec)
        all_scores["hotel_recall"].append(h_rec)
        all_scores["hotel_mrr"].append(h_mrr)
        all_scores["hotel_hit"].append(h_hit)
        all_scores["flight_precision"].append(f_prec)
        all_scores["flight_recall"].append(f_rec)
        all_scores["flight_mrr"].append(f_mrr)
        all_scores["flight_hit"].append(f_hit)

        query_result = {
            "query_id": query_id,
            "description": description,
            "elapsed_ms": elapsed_ms,
            "expected_hotel_count": len(expected_hotels),
            "expected_flight_count": len(expected_flights),
            "returned_hotel_ids": returned_hotel_ids,
            "returned_flight_ids": returned_flight_ids,
            "hotel_precision": round(h_prec, 4),
            "hotel_recall": round(h_rec, 4),
            "hotel_mrr": round(h_mrr, 4),
            "hotel_hit": h_hit,
            "flight_precision": round(f_prec, 4),
            "flight_recall": round(f_rec, 4),
            "flight_mrr": round(f_mrr, 4),
            "flight_hit": f_hit,
        }
        query_results.append(query_result)

        # print per-query results
        print(f"\nQuery {i+1:2d}: {query_id}")
        print(f"  {description}")
        print(f"  Time: {elapsed_ms}ms | Expected — hotels: {len(expected_hotels)}, flights: {len(expected_flights)}")
        print(f"  Hotels  — P@{top_k}: {h_prec:.2f} | R@{top_k}: {h_rec:.4f} | MRR: {h_mrr:.2f} | Hit: {'YES' if h_hit else 'NO'}")
        print(f"  Flights — P@{top_k}: {f_prec:.2f} | R@{top_k}: {f_rec:.4f} | MRR: {f_mrr:.2f} | Hit: {'YES' if f_hit else 'NO'}")

    # -----------------------------------------------------------------------
    # overall averages
    # -----------------------------------------------------------------------
    def avg(lst):
        return round(sum(lst) / len(lst), 4) if lst else 0.0

    averages = {
        "hotel_precision": avg(all_scores["hotel_precision"]),
        "hotel_recall": avg(all_scores["hotel_recall"]),
        "hotel_mrr": avg(all_scores["hotel_mrr"]),
        "hotel_hit_rate": avg(all_scores["hotel_hit"]),
        "flight_precision": avg(all_scores["flight_precision"]),
        "flight_recall": avg(all_scores["flight_recall"]),
        "flight_mrr": avg(all_scores["flight_mrr"]),
        "flight_hit_rate": avg(all_scores["flight_hit"]),
    }

    print("\n" + "=" * 80)
    print("OVERALL AVERAGES")
    print("=" * 80)
    print(f"  Hotel  Precision@{top_k}:  {averages['hotel_precision']:.4f}")
    print(f"  Hotel  Recall@{top_k}:     {averages['hotel_recall']:.4f}")
    print(f"  Hotel  MRR:            {averages['hotel_mrr']:.4f}")
    print(f"  Hotel  Hit Rate@{top_k}:   {averages['hotel_hit_rate']:.4f}")
    print()
    print(f"  Flight Precision@{top_k}:  {averages['flight_precision']:.4f}")
    print(f"  Flight Recall@{top_k}:     {averages['flight_recall']:.4f}")
    print(f"  Flight MRR:            {averages['flight_mrr']:.4f}")
    print(f"  Flight Hit Rate@{top_k}:   {averages['flight_hit_rate']:.4f}")

    # -----------------------------------------------------------------------
    # quality assessment — simple pass/fail thresholds
    # -----------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("QUALITY ASSESSMENT")
    print("=" * 80)

    # thresholds — these are reasonable for a RAG system with metadata filters
    PRECISION_THRESHOLD = 0.60
    HIT_RATE_THRESHOLD = 0.80
    MRR_THRESHOLD = 0.70

    checks = [
        ("Hotel Precision@k >= 0.60", averages["hotel_precision"] >= PRECISION_THRESHOLD),
        ("Hotel Hit Rate@k >= 0.80", averages["hotel_hit_rate"] >= HIT_RATE_THRESHOLD),
        ("Hotel MRR >= 0.70", averages["hotel_mrr"] >= MRR_THRESHOLD),
        ("Flight Precision@k >= 0.60", averages["flight_precision"] >= PRECISION_THRESHOLD),
        ("Flight Hit Rate@k >= 0.80", averages["flight_hit_rate"] >= HIT_RATE_THRESHOLD),
        ("Flight MRR >= 0.70", averages["flight_mrr"] >= MRR_THRESHOLD),
    ]

    all_pass = True
    for label, passed in checks:
        status = "PASS" if passed else "FAIL"
        marker = "+" if passed else "X"
        print(f"  [{marker}] {label}: {status}")
        if not passed:
            all_pass = False

    if all_pass:
        print("\n  RESULT: ALL CHECKS PASSED — retrieval quality meets thresholds")
    else:
        print("\n  RESULT: SOME CHECKS FAILED — retrieval needs investigation")

    # -----------------------------------------------------------------------
    # save full results to JSON
    # -----------------------------------------------------------------------
    full_report = {
        "evaluation_config": {
            "top_k": top_k,
            "num_queries": len(eval_queries),
            "precision_threshold": PRECISION_THRESHOLD,
            "hit_rate_threshold": HIT_RATE_THRESHOLD,
            "mrr_threshold": MRR_THRESHOLD,
        },
        "averages": averages,
        "all_pass": all_pass,
        "query_results": query_results,
    }

    with open(RESULTS_PATH, "w") as f:
        json.dump(full_report, f, indent=2)
    print(f"\n  Full results saved to {RESULTS_PATH}")

    return full_report


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Run retrieval evaluation against Pinecone")
    parser.add_argument("--top_k", type=int, default=5, help="Number of results per query (default: 5)")
    args = parser.parse_args()

    run_evaluation(top_k=args.top_k)


if __name__ == "__main__":
    main()
