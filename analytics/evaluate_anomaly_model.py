import os
import json
import argparse
from datetime import datetime
import duckdb
import numpy as np
import pandas as pd
from warehouse.db_connection import get_connection
from data_generator.generator import SyntheticDataGenerator
from analytics.anomaly_model import AnomalyDetector

def evaluate_predictions(preds_df: pd.DataFrame, manifest: list) -> dict:
    """
    Computes classification evaluation metrics given model predictions and ground-truth manifest.

    Parameters:
        preds_df (pd.DataFrame): Columns [instance_id, anomaly_score, is_anomaly].
        manifest (list): Ground truth records with keys 'instance_id' and 'anomaly_type'.

    Returns:
        dict: Evaluation metrics and per-type recall statistics.
    """
    manifest_df = pd.DataFrame(manifest)
    true_anomaly_ids = set(manifest_df["instance_id"])
    all_instances = set(preds_df["instance_id"])
    pred_anomaly_ids = set(preds_df[preds_df["is_anomaly"]]["instance_id"])

    tp = len(pred_anomaly_ids & true_anomaly_ids)
    fp = len(pred_anomaly_ids - true_anomaly_ids)
    fn = len(true_anomaly_ids - pred_anomaly_ids)
    tn = len(all_instances - (pred_anomaly_ids | true_anomaly_ids))

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    # Recall breakdown per anomaly type
    type_recall = {}
    for atype, grp in manifest_df.groupby("anomaly_type"):
        type_targets = set(grp["instance_id"])
        caught = len(type_targets & pred_anomaly_ids)
        total = len(type_targets)
        type_recall[atype] = {
            "caught": caught,
            "total": total,
            "recall": caught / total if total > 0 else 0.0
        }

    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "total_instances": len(all_instances),
        "total_manifest_anomalies": len(true_anomaly_ids),
        "total_predicted_anomalies": len(pred_anomaly_ids),
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "type_recall": type_recall,
        "predicted_anomaly_ids": sorted(list(pred_anomaly_ids)),
        "false_positive_ids": sorted(list(pred_anomaly_ids - true_anomaly_ids)),
        "false_negative_ids": sorted(list(true_anomaly_ids - pred_anomaly_ids))
    }

def print_evaluation_report(results: dict, title: str = "EVALUATION REPORT"):
    """
    Prints a formatted, human-readable terminal report.
    """
    print("\n" + "=" * 65)
    print(f" {title} ")
    print("=" * 65)
    print(f" Timestamp        : {results['timestamp']}")
    print(f" Target Seed      : {results.get('seed', 'Default (42)')}")
    print(f" Decision Thresh  : {results['decision_threshold']}")
    print(f" Total Instances  : {results['total_instances']}")
    print(f" Ground Truth Anom: {results['total_manifest_anomalies']}")
    print(f" Predicted Anom   : {results['total_predicted_anomalies']}")
    print("-" * 65)
    print(" CONFUSION MATRIX:")
    print("                        Predicted Anomaly    Predicted Normal")
    print(f"   Actual Anomaly (P) :        {results['tp']:<15}      {results['fn']:<15}")
    print(f"   Actual Normal  (N) :        {results['fp']:<15}      {results['tn']:<15}")
    print("-" * 65)
    print(f" Precision        : {results['precision']:.4f} ({results['precision']*100:.2f}%)")
    print(f" Recall           : {results['recall']:.4f} ({results['recall']*100:.2f}%)")
    print(f" F1 Score         : {results['f1']:.4f}")
    print("-" * 65)
    print(" RECALL BREAKDOWN BY ANOMALY CATEGORY:")
    for atype, stats in results["type_recall"].items():
        bar = "#" * int(stats["recall"] * 10) + "." * (10 - int(stats["recall"] * 10))
        print(f"   - {atype:<22}: {stats['caught']:>2}/{stats['total']:<2} [{bar}] {stats['recall']*100:>5.1f}%")
    print("-" * 65)
    if results["false_positive_ids"]:
        print(f" False Positives ({len(results['false_positive_ids'])}): {', '.join(results['false_positive_ids'])}")
    if results["false_negative_ids"]:
        print(f" False Negatives ({len(results['false_negative_ids'])}): {', '.join(results['false_negative_ids'])}")
    print("=" * 65 + "\n")

def evaluate_seed_in_memory(seed: int, detector: AnomalyDetector = None) -> dict:
    """
    Generates an in-memory synthetic dataset for the given seed, trains and evaluates
    the production AnomalyDetector without modifying the persistent database or root CSV files.
    """
    if detector is None:
        detector = AnomalyDetector()

    gen = SyntheticDataGenerator(seed=seed)
    instances_df = gen.generate_instances(count=300)
    metrics_df = gen.generate_metrics(instances_df, days=90)
    sec_df = gen.generate_security_configs(instances_df)
    cost_df = gen.generate_cost_data(instances_df, metrics_df)
    events_df = gen.generate_security_events(instances_df, days=90)
    manifest = gen.anomaly_manifest

    # Use isolated in-memory DuckDB connection
    mem_conn = duckdb.connect(":memory:")
    mem_conn.register("instances", instances_df)
    mem_conn.register("metrics_daily", metrics_df)
    mem_conn.register("security_configurations", sec_df)
    mem_conn.register("cost_data", cost_df)
    mem_conn.register("security_events", events_df)

    detector.train(mem_conn)
    preds = detector.predict(mem_conn)
    mem_conn.close()

    res = evaluate_predictions(preds, manifest)
    res["seed"] = seed
    res["timestamp"] = datetime.now().isoformat()
    res["decision_threshold"] = detector.decision_threshold
    return res

def evaluate_default_database(db_conn=None) -> dict:
    """
    Evaluates the currently loaded database warehouse against data/synthetic/anomaly_manifest.json
    using the active default production AnomalyDetector configuration.
    """
    close_after = False
    if db_conn is None:
        db_conn = get_connection()
        close_after = True

    try:
        manifest_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "data", "synthetic", "anomaly_manifest.json")
        )
        if not os.path.exists(manifest_path):
            raise FileNotFoundError(f"Anomaly manifest ground truth not found at {manifest_path}")

        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        detector = AnomalyDetector()
        detector.train(db_conn)
        preds = detector.predict(db_conn)

        res = evaluate_predictions(preds, manifest)
        res["seed"] = 42
        res["timestamp"] = datetime.now().isoformat()
        res["decision_threshold"] = detector.decision_threshold
        return res
    finally:
        if close_after:
            db_conn.close()

def main():
    parser = argparse.ArgumentParser(
        description="CLARA Multi-Modal Anomaly Detection Model Evaluator"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Specific random seed to evaluate in-memory (e.g. 42, 43, 44, 100)."
    )
    parser.add_argument(
        "--all-seeds",
        action="store_true",
        help="Evaluate default seed plus additional seeds (43, 44, 100) to verify generalization."
    )
    args = parser.parse_args()

    if args.seed is not None:
        print(f"Evaluating in-memory synthetic corpus for Seed {args.seed}...")
        results = evaluate_seed_in_memory(args.seed)
        print_evaluation_report(results, title=f"SEED {args.seed} EVALUATION REPORT")
        return

    # Default evaluation: Persistent warehouse against data/synthetic/anomaly_manifest.json
    print("Evaluating default database warehouse (Seed 42 ground truth)...")
    default_results = evaluate_default_database()
    print_evaluation_report(default_results, title="DEFAULT REPRODUCIBLE CORPUS (SEED 42) EVALUATION")

    if args.all_seeds:
        benchmark_seeds = [42, 43, 44, 100]
        print("\n" + "#" * 65)
        print(" MULTI-SEED GENERALIZATION BENCHMARK (In-Memory Diagnostic)")
        print("#" * 65)
        seed_summary = []
        precisions = []
        recalls = []
        f1s = []

        for s in benchmark_seeds:
            res = evaluate_seed_in_memory(s)
            precisions.append(res["precision"])
            recalls.append(res["recall"])
            f1s.append(res["f1"])
            seed_summary.append({
                "Seed": s,
                "TP": res["tp"],
                "FP": res["fp"],
                "FN": res["fn"],
                "TN": res["tn"],
                "Precision": f"{res['precision']*100:.2f}%",
                "Recall": f"{res['recall']*100:.2f}%",
                "F1": f"{res['f1']:.4f}",
                "Categories Detected": f"{sum(1 for v in res['type_recall'].values() if v['caught'] > 0)}/5"
            })
            print_evaluation_report(res, title=f"SEED {s} BENCHMARK REPORT")

        summary_df = pd.DataFrame(seed_summary)
        print("\n=== MULTI-SEED GENERALIZATION SUMMARY ===")
        print(summary_df.to_string(index=False))
        print("-" * 65)
        print(f" Aggregate Mean Precision: {np.mean(precisions)*100:.2f}% (Worst-Case: {np.min(precisions)*100:.2f}%)")
        print(f" Aggregate Mean Recall   : {np.mean(recalls)*100:.2f}% (Worst-Case: {np.min(recalls)*100:.2f}%)")
        print(f" Aggregate Mean F1       : {np.mean(f1s):.4f} (Worst-Case: {np.min(f1s):.4f})")
        print("=" * 65 + "\n")

if __name__ == "__main__":
    main()
