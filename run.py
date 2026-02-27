import argparse
import json
import logging
import time
import sys
import os
import yaml
import pandas as pd
import numpy as np

def setup_logger(log_file):
    """Configures Python logging to output to a specified file."""
    logger = logging.getLogger("mlops_job")
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(log_file)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger

def write_output_and_exit(metrics_path, metrics_data, is_error=False):
    """Writes JSON to file, prints to stdout, and exits."""
    # Write to file for both success and error cases [cite: 70]
    with open(metrics_path, 'w') as f:
        json.dump(metrics_data, f, indent=4)
        
    # Print to stdout to satisfy Docker requirement [cite: 87]
    print(json.dumps(metrics_data, indent=4))
    
    # Exit code: 0 success, non-zero failure [cite: 88]
    sys.exit(1 if is_error else 0)

def main():
    start_time = int(time.time() * 1000)
    
    # 1. Parse CLI Arguments [cite: 18, 19, 20]
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--log-file", dest="log_file", required=True)
    args = parser.parse_args()

    # Initialize logger
    logger = setup_logger(args.log_file)
    logger.info("Job start timestamp recorded.") # [cite: 73]
    
    config_version = "unknown"

    try:
        # 2. Load + Validate Config [cite: 31]
        if not os.path.exists(args.config):
            raise FileNotFoundError("Config file is missing.") # [cite: 40]
            
        with open(args.config, 'r') as f:
            config = yaml.safe_load(f)
            
        for key in ['seed', 'window', 'version']:
            if key not in config:
                raise ValueError(f"Invalid config structure: Missing '{key}'") # [cite: 32, 40]
                
        config_version, seed, window = config['version'], config['seed'], config['window']
        
        # Set deterministic seed [cite: 5, 33]
        np.random.seed(seed)
        logger.info(f"Config loaded + validated (seed:{seed}, window:{window}, version:{config_version})") # [cite: 74]

        # 3. Load + Validate Dataset [cite: 34]
        if not os.path.exists(args.input):
            raise FileNotFoundError("Missing input file.") # [cite: 36]
        if os.path.getsize(args.input) == 0:
            raise ValueError("Empty file.") # [cite: 38]

        try:
            df = pd.read_csv(args.input)
        except Exception:
            raise ValueError("Invalid CSV format.") # [cite: 37]

        if 'close' not in df.columns:
            raise ValueError("Missing required column (close).") # [cite: 39]
            
        rows_processed = len(df)
        logger.info(f"Rows loaded: {rows_processed}") # [cite: 75]

        # 4. Processing: Rolling Mean & Signal [cite: 76]
        logger.info("Computing rolling mean...")
        # Compute rolling mean on close using window [cite: 42]
        df['rolling_mean'] = df['close'].rolling(window=window).mean()
        
        logger.info("Generating signals...")
        # Handling the first window-1 rows: np.where evaluates NaNs as False, setting signal to 0 [cite: 43]
        # signal = 1 if close > rolling_mean else signal = 0 [cite: 46, 47]
        df['signal'] = np.where(df['close'] > df['rolling_mean'], 1, 0)
        
        # 5. Metrics + Timing [cite: 48, 49]
        signal_rate = float(df['signal'].mean()) # [cite: 51]
        latency_ms = int(time.time() * 1000) - start_time # [cite: 52]
        
        logger.info(f"Metrics summary - Processed: {rows_processed}, Rate: {signal_rate:.4f}, Latency: {latency_ms}ms") # [cite: 77]
        
        # Exact success output structure [cite: 54, 55, 56, 57, 58, 59, 60, 61, 62, 63]
        success_metrics = {
            "version": config_version,
            "rows_processed": rows_processed,
            "metric": "signal_rate",
            "value": round(signal_rate, 4),
            "latency_ms": latency_ms,
            "seed": seed,
            "status": "success"
        }
        
        logger.info("Job end + status: success") # [cite: 78]
        write_output_and_exit(args.output, success_metrics, is_error=False)

    except Exception as e:
        logger.error(f"Exception / validation error: {str(e)}") # [cite: 79]
        
        # Exact error output structure [cite: 64, 65, 66, 67, 68, 69]
        error_metrics = {
            "version": config_version,
            "status": "error",
            "error_message": str(e)
        }
        logger.info("Job end + status: error") # [cite: 78]
        write_output_and_exit(args.output, error_metrics, is_error=True)

if __name__ == "__main__":
    main()