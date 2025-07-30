import subprocess

class DeployHook:
    """
    Export pipeline to Docker or schedule retrains.
    """
    def __init__(self, pipeline):
        self.pipeline = pipeline

    def to_docker(self, image_name: str = "finance_automl_pipeline"): 
        cmd = ["docker", "build", ".", "-t", image_name]
        subprocess.run(cmd, check=True)

    def schedule_retrain(self, cron_expr: str, script_path: str = "run_pipeline.py"): 
        # Example: write to crontab
        entry = f"{cron_expr} python {script_path}"
        subprocess.run(["bash", "-c", f"(crontab -l; echo '{entry}') | crontab -"], check=True)
