import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import time
import config
from data_generator.generator import SyntheticDataGenerator
from warehouse.load_data import load_all_csvs_to_warehouse
from analytics.run_all_models import main as run_models

def main():
    """
    Live Demo End-to-End Orchestrator for CLARA.
    Executes data generation, warehouse load, ML analytics, and GenAI recommendations.
    """
    print("\n" + "=" * 45)
    print("=== CLARA Full Pipeline Run ===")
    print("=" * 45 + "\n")
    
    start_time = time.time()
    
    # Step 1: Synthetic Data Generation
    print("[1/5] Generating synthetic cloud data...")
    gen_start = time.time()
    generator = SyntheticDataGenerator()
    shapes = generator.export_all()
    print(f"Generated {shapes['instances_shape'][0]} instances, {shapes['metrics_shape'][0]} metrics, {len(generator.anomaly_manifest)} anomalies.")
    print(f"Data generation complete (Duration: {time.time() - gen_start:.2f}s)\n")
    
    print("[2/5] Loading data into warehouse...")
    load_start = time.time()
    load_all_csvs_to_warehouse()
    print(f"Warehouse ingest complete (Duration: {time.time() - load_start:.2f}s)\n")
    
    # Step 3: ML Risk Scoring Models
    print("[3/5] Running ML risk scoring models...")
    models_start = time.time()
    run_models()
    print(f"ML risk modeling complete (Duration: {time.time() - models_start:.2f}s)\n")
    
    # Step 4: GenAI & Remediation Recommendations
    print("[4/5] Generating remediation recommendations...")
    genai_start = time.time()
    try:
        from genai.run_recommendations import main as run_recs
        recs = run_recs()
        rec_count = len(recs) if recs is not None else 0
        print(f"Remediation recommendations complete ({rec_count} generated, Duration: {time.time() - genai_start:.2f}s)\n")
    except Exception as e:
        print(f"\nRecommendation generation recovered from error: {e}\n")
            
    # Step 5: Pipeline completion message
    elapsed = time.time() - start_time
    print("=" * 45)
    print(f"[5/5] Pipeline complete. Total elapsed time: {elapsed:.2f}s")
    print("Run 'streamlit run dashboard/app.py' to view results.")
    print("=" * 45 + "\n")

if __name__ == "__main__":
    main()
