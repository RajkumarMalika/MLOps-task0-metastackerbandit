#  MetaStackerBandit - MLOps Task 0

Hi there! 👋 Welcome to my submission for the MLOps Engineering Internship (Task 0). 

This repository contains a production-ready, minimal batch job written in Python. It takes standard OHLCV trading data, calculates a rolling mean on the `close` price, and generates a binary trading signal. 

I designed this pipeline to mirror real-world trading systems, focusing on three core MLOps principles:
* **Reproducibility:** You'll get the exact same results every time. The pipeline relies entirely on an external `config.yaml` and enforces a strict random seed.
* **Observability:** You'll never have to guess what the script is doing. It generates detailed lifecycle logs (`run.log`) and structured, machine-readable metrics (`metrics.json`).
* **Deployment Readiness:** The entire application is Dockerized for a frictionless, "it just works" execution. 

---

##  Running Locally

Want to spin this up on your local machine? Here is how to do it:

1. **Install the dependencies:**
   Make sure you have Python 3.9+ installed, then grab the required packages:
   ```bash
   pip install -r requirements.txt
Execute the batch job:
Run the following command from the root folder. (Everything is parameterized; there are no hard-coded paths here!):

Bash
python run.py --input data.csv --config config.yaml --output metrics.json --log-file run.log
🐳 Docker Setup (Evaluation Commands)
As requested, the application is fully containerized. To evaluate the deployment, run these exact commands in your terminal:

Build the Docker image:

Bash
docker build -t mlops-task .
Run the container:

Bash
docker run --rm mlops-task
Note: The container is configured to automatically pull in the dataset and config, execute the job, print the final metrics JSON directly to stdout, and cleanly exit with a 0 success code.

 Example Outputs
Here is a look at the metrics.json file generated after a successful run:

JSON
{
    "version": "v1",
    "rows_processed": 10000,
    "metric": "signal_rate",
    "value": 0.0,
    "latency_ms": 17,
    "seed": 42,
    "status": "success"
}
Because real-world data is rarely perfect, I also built in robust validation. If the script encounters an issue (like a missing file, an empty CSV, or a missing close column), it catches the exception without crashing and outputs a clear error state:

JSON
{
    "version": "v1",
    "status": "error",
    "error_message": "Missing required column (close)."
}