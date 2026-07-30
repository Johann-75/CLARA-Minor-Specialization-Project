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
    
    # Step 4: GenAI Recommendations
    print("[4/5] Generating GenAI recommendations...")
    genai_start = time.time()
    no_key_msg = "Skipping GenAI step: no API key configured. Set gemini api key in .env to enable this step."
    try:
        # Check if API key is missing or dummy
        if not config.GEMINI_API_KEY or config.GEMINI_API_KEY == "your_key_here":
            print(no_key_msg)
        else:
            from genai.run_recommendations import main as run_recs
            run_recs()
            print(f"GenAI recommendations complete (Duration: {time.time() - genai_start:.2f}s)\n")
    except Exception as e:
        # Skip gracefully if it looks like an API key or configuration error
        if "API key" in str(e) or "GEMINI_API_KEY" in str(e) or isinstance(e, ValueError):
            print(f"\n{no_key_msg}")
        else:
            print(f"\nGenAI recommendations failed with unexpected error: {e}")
            
    # Step 5: Pipeline completion message
    elapsed = time.time() - start_time
    print("=" * 45)
    print(f"[5/5] Pipeline complete. Total elapsed time: {elapsed:.2f}s")
    print("Run 'streamlit run dashboard/app.py' to view results.")
    print("=" * 45 + "\n")

if __name__ == "__main__":
    main()
