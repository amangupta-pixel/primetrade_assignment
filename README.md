# Trading Signal Pipeline

This project implements a simple trading signal generation pipeline using historical BTC market data.

The pipeline:

* Loads and validates configuration from `config.yaml`
* Loads and validates input data from `data.csv`
* Computes a rolling mean on the `close` price using the configured window size
* Generates trading signals:

  * 1 if `close > rolling_mean`
  * 0 otherwise
* Computes summary metrics
* Writes results to `metrics.json`
* Writes execution logs to `run.log`

---

## Local Run Instructions

### 1. Create and activate a virtual environment

``` CMD
conda create -p venv python=3.11 -y
conda activate venv
```

### 2. Install dependencies

``` CMD
pip install -r requirements.txt
```

### 3. Run the pipeline

``` CMD
python run.py
```

### 4. Generated Outputs

After successful execution:

```text
metrics.json
run.log
```

will be created in the project directory.

---

## Docker Build and Run Commands

### Build Docker Image

``` CMD
docker build -t mlops-task .
```

### Run Docker Container

``` CMD
docker run --rm mlops-task
```

The container will:

* Read `config.yaml`
* Read `data.csv`
* Generate `metrics.json`
* Generate `run.log`
* Print the final metrics JSON to stdout

---

## Example metrics.json

```json
{
  "version": "v1",
  "rows_processed": 10000,
  "metric": "signal_rate",
  "value": 0.4989,
  "latency_ms": 34,
  "seed": 42,
  "status": "success"
}