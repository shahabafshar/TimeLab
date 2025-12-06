"""
ARTFIMA Full Workflow Test - API Version
=========================================
Replicates the EXACT workflow of the UI when:
1. Selecting CO2 sample dataset
2. Going through all 5 steps (clicking Next)
3. Choosing ARTFIMA model type with default parameters
4. Generating forecasts

This makes actual HTTP API calls just like the frontend does.
"""
import sys
import json
import time
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "http://localhost:8000/api/v1"  # Backend API URL with prefix
TIMEOUT = 60  # Request timeout in seconds

# UI Default Settings (matching frontend)
CONFIG = {
    "dataset_file": "co2_levels.csv",
    "date_column": "date",
    "target_column": "co2",
    "frequency": "Monthly",
    "model_type": "ARTFIMA",  # "SARIMAX" or "ARTFIMA"
    "artfima_glp": "ARTFIMA",  # "ARTFIMA", "ARFIMA", or "ARIMA"
    "forecast_periods": 12,
}


class WorkflowTester:
    """Replicates the exact UI workflow via API calls"""

    def __init__(self):
        self.project_id: Optional[str] = None
        self.dataset_id: Optional[str] = None
        self.stationarity_result: Optional[Dict] = None
        self.acf_pacf_result: Optional[Dict] = None
        self.trained_model: Optional[Dict] = None
        self.forecast_result: Optional[Dict] = None

    def make_request(self, method: str, endpoint: str, data: dict = None) -> Dict:
        """Make HTTP request to API"""
        url = f"{BASE_URL}{endpoint}"
        try:
            if method == "GET":
                response = requests.get(url, timeout=TIMEOUT)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=TIMEOUT)
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError:
            raise Exception(f"Cannot connect to backend at {BASE_URL}. Is the server running?")
        except requests.exceptions.HTTPError as e:
            error_detail = "Unknown error"
            try:
                error_detail = response.json().get("detail", str(e))
            except:
                error_detail = response.text or str(e)
            raise Exception(f"HTTP {response.status_code}: {error_detail}")

    def setup_project_and_dataset(self) -> bool:
        """Find or create a project with the CO2 sample dataset"""
        print("\n" + "=" * 80)
        print("SETUP: Finding project with CO2 dataset")
        print("=" * 80)

        # First, check if co2_levels dataset already exists
        try:
            datasets = self.make_request("GET", "/datasets/")
            for ds in datasets:
                if CONFIG["dataset_file"] in ds.get("name", ""):
                    self.dataset_id = ds["id"]
                    print(f"   Found existing dataset: {ds['name']} (ID: {self.dataset_id})")
                    break
        except Exception as e:
            print(f"   Could not list datasets: {e}")

        # If no dataset, load the sample dataset
        if not self.dataset_id:
            print("   Dataset not found, loading sample...")
            # Use the sample loading endpoint (expects "filename")
            result = self.make_request("POST", "/datasets/samples/load", {
                "filename": CONFIG["dataset_file"]  # "co2_levels.csv"
            })
            # Response is wrapped: {"dataset": {...}, "message": "..."}
            dataset_info = result.get("dataset", result)
            self.dataset_id = dataset_info["id"]
            print(f"   Loaded sample dataset: {dataset_info['name']} (ID: {self.dataset_id})")

        # Find or create a project that uses this dataset
        try:
            projects = self.make_request("GET", "/projects/")
            for proj in projects:
                if proj.get("dataset_id") == self.dataset_id:
                    self.project_id = proj["id"]
                    print(f"   Found existing project: {proj['name']} (ID: {self.project_id})")
                    break
        except Exception as e:
            print(f"   Could not list projects: {e}")

        if not self.project_id:
            # Create a new project
            project_data = {
                "name": f"ARTFIMA Test - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "description": "Test project for ARTFIMA workflow",
                "dataset_id": self.dataset_id
            }
            result = self.make_request("POST", "/projects/", project_data)
            self.project_id = result["id"]
            print(f"   Created new project: {result['name']} (ID: {self.project_id})")

        print(f"\n   Dataset ID: {self.dataset_id}")
        print(f"   Project ID: {self.project_id}")
        return True

    def step1_test_stationarity(self) -> bool:
        """
        Step 1: Test Stationarity
        Calls: POST /preprocessing/test-stationarity
        """
        print("\n" + "=" * 80)
        print("STEP 1: TEST STATIONARITY")
        print("=" * 80)

        request_body = {
            "dataset_id": self.dataset_id,
            "date_column": CONFIG["date_column"],
            "target_column": CONFIG["target_column"],
            "frequency": CONFIG["frequency"],
        }

        print(f"   Request: POST /preprocessing/test-stationarity")
        print(f"   Body: {json.dumps(request_body, indent=2)}")

        try:
            self.stationarity_result = self.make_request(
                "POST", "/preprocessing/test-stationarity", request_body
            )

            print(f"\n   RESPONSE:")
            print(f"     Is Stationary: {self.stationarity_result.get('is_stationary')}")
            print(f"     Test Statistic: {self.stationarity_result.get('test_statistic', 'N/A')}")
            print(f"     P-value: {self.stationarity_result.get('p_value', 'N/A')}")
            print(f"     Seasonality: {self.stationarity_result.get('seasonality', 'N/A')}")

            if self.stationarity_result.get('transformation'):
                trans = self.stationarity_result['transformation']
                print(f"     Transformation:")
                print(f"       Type: {trans.get('type', 'N/A')}")
                print(f"       d: {trans.get('d', 'N/A')}")
                print(f"       D: {trans.get('D', 'N/A')}")

            if self.stationarity_result.get('warnings'):
                print(f"     Warnings: {self.stationarity_result['warnings']}")

            return True
        except Exception as e:
            print(f"   ERROR: {e}")
            return False

    def step2_select_model_type(self) -> bool:
        """
        Step 2: Review Stationarity Results & Select Model Type
        This is a UI-only step - no API call, just state selection
        """
        print("\n" + "=" * 80)
        print("STEP 2: SELECT MODEL TYPE")
        print("=" * 80)

        print(f"   Selected Model Type: {CONFIG['model_type']}")
        if CONFIG['model_type'] == "ARTFIMA":
            print(f"   ARTFIMA Variant (GLP): {CONFIG['artfima_glp']}")

        print("\n   (This step is UI-only - clicking 'Continue to ACF/PACF Analysis')")
        return True

    def step3_calculate_acf_pacf(self) -> bool:
        """
        Step 3: Calculate ACF/PACF
        Calls: POST /analysis/acf-pacf
        """
        print("\n" + "=" * 80)
        print("STEP 3: CALCULATE ACF/PACF")
        print("=" * 80)

        # Get seasonality from stationarity result or use default
        seasonality = self.stationarity_result.get('seasonality', 12)
        if CONFIG["frequency"] == "Monthly":
            seasonality = seasonality or 12
        elif CONFIG["frequency"] == "Quarterly":
            seasonality = seasonality or 4
        elif CONFIG["frequency"] == "Daily":
            seasonality = seasonality or 7

        request_body = {
            "dataset_id": self.dataset_id,
            "date_column": CONFIG["date_column"],
            "target_column": CONFIG["target_column"],
            "seasonality": seasonality,
        }

        print(f"   Request: POST /analysis/acf-pacf")
        print(f"   Body: {json.dumps(request_body, indent=2)}")

        try:
            self.acf_pacf_result = self.make_request(
                "POST", "/analysis/acf-pacf", request_body
            )

            print(f"\n   RESPONSE:")
            if self.acf_pacf_result.get('suggested_parameters'):
                params = self.acf_pacf_result['suggested_parameters']
                print(f"     Suggested Parameters:")
                print(f"       p (AR order): {params.get('p', 'N/A')}")
                print(f"       q (MA order): {params.get('q', 'N/A')}")
                print(f"       P (Seasonal AR): {params.get('P', 'N/A')}")
                print(f"       Q (Seasonal MA): {params.get('Q', 'N/A')}")

            if self.acf_pacf_result.get('confidence_interval'):
                ci = self.acf_pacf_result['confidence_interval']
                print(f"     Confidence Interval: [{ci.get('lower', 'N/A')}, {ci.get('upper', 'N/A')}]")

            acf_vals = self.acf_pacf_result.get('acf', [])
            pacf_vals = self.acf_pacf_result.get('pacf', [])
            print(f"     ACF (first 5): {[round(v, 4) for v in acf_vals[:5]]}")
            print(f"     PACF (first 5): {[round(v, 4) for v in pacf_vals[:5]]}")

            return True
        except Exception as e:
            print(f"   ERROR: {e}")
            return False

    def step4_train_model(self) -> bool:
        """
        Step 4: Train Model
        Calls: POST /models/train
        This is where the ARTFIMA training happens
        """
        print("\n" + "=" * 80)
        print("STEP 4: TRAIN MODEL")
        print("=" * 80)

        # Get seasonality
        seasonality = self.stationarity_result.get('seasonality', 12)
        if CONFIG["frequency"] == "Monthly":
            seasonality = seasonality or 12

        # Get suggested parameters from ACF/PACF
        suggested = self.acf_pacf_result.get('suggested_parameters', {})
        p = suggested.get('p', 1)
        q = suggested.get('q', 1)
        P = suggested.get('P', 1)
        Q = suggested.get('Q', 1)

        # Adjust q to avoid conflicts (as UI does)
        if q >= seasonality:
            q = max(0, seasonality - 1)

        # Cap p to reasonable value
        p = min(p, 5)

        # Get d from stationarity transformation
        trans = self.stationarity_result.get('transformation', {})
        d = trans.get('d', 0)
        D = trans.get('D', 0)

        # Build request body - exactly as UI does
        request_body = {
            "dataset_id": self.dataset_id,
            "date_column": CONFIG["date_column"],
            "target_column": CONFIG["target_column"],
            "model_type": CONFIG["model_type"],
            "parameters": {
                "p": p,
                "d": d,
                "q": q,
                "P": P,
                "D": D,
                "Q": Q,
                "s": seasonality,
            },
        }

        # Add ARTFIMA-specific parameters if ARTFIMA is selected
        if CONFIG["model_type"] == "ARTFIMA":
            request_body["artfima_parameters"] = {
                "p": p,
                "d": float(d),  # fractional d
                "q": q,
                "glp": CONFIG["artfima_glp"],
                "lambda_param": None,  # Let the model estimate
                "fixd": None,  # Let the model estimate
            }

        print(f"   Request: POST /models/train")
        print(f"   Body: {json.dumps(request_body, indent=2)}")

        try:
            start_time = time.time()
            self.trained_model = self.make_request(
                "POST", "/models/train", request_body
            )
            elapsed = time.time() - start_time

            print(f"\n   RESPONSE (training took {elapsed:.2f}s):")
            print(f"     Model ID: {self.trained_model.get('id', 'N/A')}")
            print(f"     Model Name: {self.trained_model.get('name', 'N/A')}")
            print(f"     Model Type: {self.trained_model.get('type', 'N/A')}")

            if self.trained_model.get('parameters'):
                params = self.trained_model['parameters']
                print(f"     Estimated Parameters:")
                for key, value in params.items():
                    if isinstance(value, float):
                        print(f"       {key}: {value:.6f}")
                    else:
                        print(f"       {key}: {value}")

            if self.trained_model.get('metrics'):
                metrics = self.trained_model['metrics']
                print(f"     Metrics:")
                print(f"       AIC: {metrics.get('aic', 'N/A')}")
                print(f"       BIC: {metrics.get('bic', 'N/A')}")
                print(f"       HQIC: {metrics.get('hqic', 'N/A')}")

            return True
        except Exception as e:
            print(f"   ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False

    def step5_generate_forecast(self) -> bool:
        """
        Step 5: Generate Forecast
        Calls: POST /models/{model_id}/forecast
        """
        print("\n" + "=" * 80)
        print("STEP 5: GENERATE FORECAST")
        print("=" * 80)

        if not self.trained_model or not self.trained_model.get('id'):
            print("   ERROR: No trained model available")
            return False

        model_id = self.trained_model['id']

        # Determine transformation type
        trans = self.stationarity_result.get('transformation', {})
        trans_type = trans.get('type', 'none')
        if 'log' in str(trans_type).lower():
            transformation_type = "log"
        else:
            transformation_type = "none"

        request_body = {
            "periods": CONFIG["forecast_periods"],
            "transformation_type": transformation_type,
        }

        print(f"   Request: POST /models/{model_id}/forecast")
        print(f"   Body: {json.dumps(request_body, indent=2)}")

        try:
            start_time = time.time()
            self.forecast_result = self.make_request(
                "POST", f"/models/{model_id}/forecast", request_body
            )
            elapsed = time.time() - start_time

            print(f"\n   RESPONSE (forecast took {elapsed:.2f}s):")

            if self.forecast_result.get('forecasts'):
                forecasts = self.forecast_result['forecasts']
                dates = forecasts.get('dates', [])
                values = forecasts.get('values', [])

                print(f"     Forecast Periods: {len(dates)}")
                print(f"\n     Forecast Values:")
                print(f"     {'Date':<20} {'Value':<15} {'Lower CI':<15} {'Upper CI':<15}")
                print(f"     {'-'*65}")

                ci = self.forecast_result.get('confidence_intervals', {})
                lower = ci.get('lower', [])
                upper = ci.get('upper', [])

                for i in range(min(len(dates), 12)):
                    date_str = dates[i][:10] if dates[i] else "N/A"
                    value = values[i] if i < len(values) else "N/A"
                    lo = lower[i] if i < len(lower) else "N/A"
                    up = upper[i] if i < len(upper) else "N/A"

                    if isinstance(value, (int, float)):
                        print(f"     {date_str:<20} {value:<15.4f} {lo:<15.4f} {up:<15.4f}")
                    else:
                        print(f"     {date_str:<20} {value:<15} {lo:<15} {up:<15}")

            return True
        except Exception as e:
            print(f"   ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False

    def run_full_workflow(self) -> bool:
        """Run the complete 5-step workflow"""
        print("\n" + "#" * 80)
        print("#" + " " * 78 + "#")
        print("#" + " ARTFIMA FULL WORKFLOW TEST (API VERSION) ".center(78) + "#")
        print("#" + f" Model: {CONFIG['model_type']} - Dataset: {CONFIG['dataset_file']} ".center(78) + "#")
        print("#" + " " * 78 + "#")
        print("#" * 80)

        # Setup
        if not self.setup_project_and_dataset():
            print("\n[FAIL] Setup failed - cannot proceed")
            return False

        # Step 1: Test Stationarity
        if not self.step1_test_stationarity():
            print("\n[FAIL] Step 1 failed - cannot proceed")
            return False

        # Step 2: Select Model Type (UI-only step)
        if not self.step2_select_model_type():
            print("\n[FAIL] Step 2 failed - cannot proceed")
            return False

        # Step 3: Calculate ACF/PACF
        if not self.step3_calculate_acf_pacf():
            print("\n[FAIL] Step 3 failed - cannot proceed")
            return False

        # Step 4: Train Model
        if not self.step4_train_model():
            print("\n[FAIL] Step 4 failed - cannot proceed")
            return False

        # Step 5: Generate Forecast
        if not self.step5_generate_forecast():
            print("\n[FAIL] Step 5 failed")
            return False

        # Summary
        print("\n" + "=" * 80)
        print("WORKFLOW SUMMARY")
        print("=" * 80)
        print(f"   Model Type: {CONFIG['model_type']}")
        if CONFIG['model_type'] == "ARTFIMA":
            print(f"   GLP Variant: {CONFIG['artfima_glp']}")
        print(f"   Dataset: {CONFIG['dataset_file']}")
        print(f"   Target Column: {CONFIG['target_column']}")
        print(f"   Forecast Periods: {CONFIG['forecast_periods']}")

        if self.trained_model:
            print(f"\n   Trained Model ID: {self.trained_model.get('id')}")
            params = self.trained_model.get('parameters', {})
            if 'd' in params:
                print(f"   Estimated d: {params.get('d')}")
            if 'lambda' in params:
                print(f"   Estimated lambda: {params.get('lambda')}")

        print("\n[OK] ARTFIMA workflow completed successfully!")
        return True


def main():
    """Main entry point"""
    tester = WorkflowTester()

    try:
        success = tester.run_full_workflow()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
