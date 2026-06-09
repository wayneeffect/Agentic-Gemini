import os
import sys
import json
import time
import re
import gc
import subprocess
from google import genai
from google.genai import types

# =====================================================================
# SYSTEM CONFIGURATION
# =====================================================================
# The SDK automatically draws the key from os.environ["GEMINI_API_KEY"]
MODEL_FLASH = "gemini-2.5-flash"
MODEL_PRO = "gemini-2.5-pro"

TARGET_FILE = "software_under_test.py"
EVALUATOR_FILE = "evaluator.py"
INSTRUCTIONS_FILE = "instructions.md"
STATUS_FILE = "status.json"

MAX_LOG_HISTORY = 12
COOLDOWN_DELAY_SECS = 45

# =====================================================================
# DEV-OPS UTILITIES
# =====================================================================
class TelemetryLogger:
    def __init__(self):
        self.logs = []

    def log(self, message: str):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        formatted_msg = f"[{timestamp}] {message}"
        print(formatted_msg)
        self.logs.append(formatted_msg)
        # Prevent log lists from expanding infinitely in RAM
        if len(self.logs) > MAX_LOG_HISTORY:
            self.logs.pop(0)

    def dump_status(self, run_num, delta, current_best, model_name):
        """Dumps internal telemetry metrics out as a static JSON block"""
        status_data = {
            "current_run": run_num,
            "active_model": model_name,
            "latency_delta": round(delta, 1),
            "current_best": current_best,
            "baseline_latency": 245, # Managed baseline tracker
            "logs": list(self.logs)
        }
        with open(STATUS_FILE, "w") as f:
            json.dump(status_data, f, indent=4)

        # Push to GitHub to actively update the Chrome Dashboard
        try:
            subprocess.run(["git", "add", STATUS_FILE], check=True, capture_output=True)
            subprocess.run(["git", "commit", "-m", f"Telemetry Run #{run_num}"], check=True, capture_output=True)
            subprocess.run(["git", "push", "origin", "main"], check=True, capture_output=True)
        except Exception as e:
            print(f"[Warning] Failed to route data through GitHub: {str(e)}")

def extract_python_code(markdown_text: str) -> str:
    """Safely strips markdown conversational blocks to harvest raw Python"""
    pattern = r"```python\s*(.*?)\s*```"
    match = re.search(pattern, markdown_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return markdown_text.strip()

# =====================================================================
# ORCHESTRATION PIPELINE
# =====================================================================
def run_optimization_loop():
    logger = TelemetryLogger()
    logger.log("Initializing Agentic Optimization Loop...")

    # Establish baseline tracking records
    current_best_latency = 245.0  # Safe initial placeholder metric
    baseline_latency = 245.0
    stagnation_counter = 0
    run_number = 0

    # Initialize the client context manager to automatically close sync handlers
    with genai.Client() as client:
        while True:
            run_number += 1
            # Explicit memory sweeps inside the infinite loop to shield our 1GB Cloud VM
            gc.collect()

            # Step 1: Dynamically determine processing model (Algorithmic Escalation)
            if stagnation_counter >= 5:
                active_model = MODEL_PRO
                logger.log(f"⚠️ Bottleneck detected. Escalating to {MODEL_PRO} (High Thinking mode)...")
                config = types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_level="medium")
                )
            else:
                active_model = MODEL_FLASH
                logger.log(f"🤖 Preparing execution run #{run_number} using {MODEL_FLASH}...")
                config = types.GenerateContentConfig(temperature=0.4)

            # Step 2: Ingest local context maps
            try:
                with open(INSTRUCTIONS_FILE, "r") as f:
                    system_directives = f.read()
                with open(TARGET_FILE, "r") as f:
                    current_code = f.read()
            except Exception as e:
                logger.log(f"❌ File system read execution failed: {str(e)}")
                time.sleep(10)
                continue

            # Appending current file status context straight to prompt array
            prompt = [
                f"Here is the current operational code layout:\n\n```python\n{current_code}\n```\n",
                f"Analyze performance bottlenecks and rewrite the module based on system goals."
            ]

            # Step 3: API Request Dispatch
            try:
                response = client.models.generate_content(
                    model=active_model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_directives,
                        **({} if active_model == MODEL_FLASH else {"thinking_config": config.thinking_config})
                    )
                )
                generated_payload = response.text
            except Exception as e:
                logger.log(f"💥 Gemini API Connection Error: {str(e)}")
                time.sleep(30)
                continue

            # Step 4: Sanitize and execute Atomic Workspace Swap
            mutated_code = extract_python_code(generated_payload)
            if not mutated_code or "def compute_heavy_logic" not in mutated_code:
                logger.log("❌ Response failed structural code checks. Purging cycle.")
                continue

            with open(TARGET_FILE, "w") as f:
                f.write(mutated_code)

            # Step 5: Subprocess Isolation Testing Gate
            logger.log("[Evaluator] Spawning isolated testing sub-process...")
            try:
                result = subprocess.run(
                    [sys.executable, EVALUATOR_FILE],
                    capture_output=True,
                    text=True,
                    timeout=35
                )
                
                # Safely attempt parsing JSON output out of standard out streams
                eval_data = json.loads(result.stdout.strip()) if result.returncode == 0 else {"status": "FAIL", "reason": "Runtime Crash"}
            except subprocess.TimeoutExpired:
                eval_data = {"status": "FAIL", "reason": "Execution timed out (infinite recursion fence breaker)"}
            except Exception as e:
                eval_data = {"status": "FAIL", "reason": f"Harness execution anomaly: {str(e)}"}

            # Step 6: Transaction Evaluation (Commit or Hard Rollback)
            if eval_data["status"] == "SUCCESS":
                new_latency = float(eval_data["latency_ms"])
                
                # Check if it actually beat our running global record
                if new_latency < current_best_latency:
                    latency_gain = ((baseline_latency - new_latency) / baseline_latency) * 100
                    current_best_latency = new_latency
                    stagnation_counter = 0 # Reset escalation tracking
                    
                    logger.log(f"✓ [SUCCESS] Code optimized to {new_latency}ms. Committing transaction checkpoint...")
                    
                    # Log real checkpoint commits to git memory tracking
                    subprocess.run(["git", "add", TARGET_FILE], capture_output=True)
                    subprocess.run(["git", "commit", "-m", f"Optimization Run #{run_number} (Latency: {new_latency}ms)"], capture_output=True)
                else:
                    logger.log(f"⚠️ Functional but stagnant. Execution: {new_latency}ms. Executing rollback...")
                    subprocess.run(["git", "checkout", "HEAD", "--", TARGET_FILE], capture_output=True)
                    stagnation_counter += 1
            else:
                logger.log(f"❌ [FAIL] {eval_data['reason']}. Wiping environment workspace...")
                # Clear invalid changes instantly via git tracking checks
                subprocess.run(["git", "checkout", "HEAD", "--", TARGET_FILE], capture_output=True)
                stagnation_counter += 1

            # Step 7: Push metrics to cloud and start cooldown sequence
            global_latency_reduction = ((baseline_latency - current_best_latency) / baseline_latency) * 100
            logger.dump_status(run_number, global_latency_reduction, current_best_latency, active_model)
            
            logger.log(f"[System] Cycle complete. Entering cooling delay for {COOLDOWN_DELAY_SECS}s...")
            time.sleep(COOLDOWN_DELAY_SECS)

if __name__ == "__main__":
    # Safety Check: Guarantee git tracking environment profile exists before looping
    try:
        subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("CRITICAL: This directory is not a Git repository. Run 'git init' first.")
        sys.exit(1)

    try:
        run_optimization_loop()
    except KeyboardInterrupt:
        print("\n[System] Graceful exit intercept received. Shutting down research pipeline.")
