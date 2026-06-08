import sys
import numpy as np
import pandas as pd
import yaml
import time
import json
import logging
import os
from datetime import datetime

LOG_FILE = "run.log"

logging.basicConfig(
    filename=LOG_FILE,
    format="[ %(asctime)s ] %(lineno)d %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logging.info(f"Job Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

start = time.perf_counter()

'''

1) Load + validate config
● Parse YAML, validate required fields (seed, window, version)
● Set seed: numpy.random.seed(seed) (or equivalent)

'''

def load_config(config_file) -> dict:

    with open(config_file,"r") as file:
        config = yaml.safe_load(file)

    np.random.seed(config["seed"])

    required_keys = ["seed","window","version"]

    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing key: {key}")
        
    logging.info("Config loading and validation done")
    return config
            
'''

2) Load + validate dataset
Handle these cases cleanly:
● Missing input file
● Invalid CSV format
● Empty file
● Missing required column (close)
● Invalid config structure

'''

def load_dataset(file) -> pd.DataFrame:
    try:
        df = pd.read_csv(file)

        if len(df.columns)==1:
            df = df[df.columns[0]].str.split(",", expand=True)

        df.columns = ["timestamp","open","high","low","close","volume_btc","volume_usd"]

        if df.empty:
            raise ValueError("Empty File")

        required_cols = ["close"]

        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")

        logging.info("Rows loading done")    
        return df

    except FileNotFoundError:
        raise FileNotFoundError("File not found")
    
    except Exception as e:
        raise ValueError(str(e))
    


try:
        
    config = load_config("config.yaml")
    print(config)
    df = load_dataset("data.csv")

    print(df["close"].isnull().sum()) # 0
    print(df['close'].dtype) # str

    df['close'] = pd.to_numeric(df['close'])
    print(df['close'].dtype) # float64

    '''
    3) Rolling mean
    Compute rolling mean on close using window from config.
    Important: define how you handle the first window-1 rows (e.g., allow NaNs and exclude from
    signal computation, or fill—just be consistent)
    '''

    df["rolling_mean"] = df["close"].rolling(window=config["window"]).mean()

    '''
    4) Signal
    For each row:
    ● signal = 1 if close > rolling_mean
    ● else signal = 0

    '''

    df["signal"] = (df['close']>df['rolling_mean']).astype(int)

    logging.info("Rolling mean and signal generation steps done")

    '''
    5) Metrics + timing
    Compute:
    ● rows_processed
    ● signal_rate = mean(signal)
    ● latency_ms = total runtime in milliseconds
    
    '''

    rows_processed = len(df)

    signal_rate = float(df['signal'].mean())

    latency_ms = int((time.perf_counter()-start)*1000)

    metrics = {
"version": config["version"],
"rows_processed": rows_processed,
"metric": "signal_rate",
"value": signal_rate,
"latency_ms": latency_ms,
"seed": config['seed'],
"status": "success"
}
    
    logging.info("Metrics obtained and metrics.json generated")
    logging.info("Trading Signal Pipeline Completed Successfully")

    exit_code = 0

except Exception as e:
    metrics = {
"version": "v1",
"status": "error",
"error_message": str(e)
}
    
    logging.exception("Pipeline Execution Failed")

    exit_code = 1
    
finally:
    with open("metrics.json","w") as file:
        json.dump(metrics,file)

    print(json.dumps(metrics))
    sys.exit(exit_code)
