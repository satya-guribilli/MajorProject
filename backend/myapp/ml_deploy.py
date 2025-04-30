import requests

# Replace with your actual Django backend endpoints
SALARY_PREDICTION_URL = 'http://localhost:8000/api/predict/salary/'
PLACEMENT_PREDICTION_URL = 'http://localhost:8000/api/predict/placement/'

def predict_salary_api(feature_dict):
    try:
        response = requests.post(SALARY_PREDICTION_URL, json=feature_dict)
        response.raise_for_status()

        data = response.json()
        print("Raw salary API response:", data)

        # ✅ Accept new API format
        if isinstance(data, dict) and "salary_prediction" in data:
            return [data["salary_prediction"]]  # wrap in list for consistency

        elif isinstance(data, dict) and "predictions" in data:
            return data["predictions"]

        elif isinstance(data, list):
            return data

        else:
            raise ValueError(f"Unexpected salary response type: {type(data)}, content: {data}")

    except Exception as e:
        print(f"[Error] Failed to get salary prediction: {e}")
        return [0.0]




def predict_isplaced_api(feature_dict):
    try:
        response = requests.post(PLACEMENT_PREDICTION_URL, json=feature_dict)
        response.raise_for_status()

        data = response.json()
        print("Raw placement API response:", data)

        # ✅ Accept new API format
        if isinstance(data, dict) and "placement_probability" in data:
            return [data["placement_probability"]]

        elif isinstance(data, dict) and "predictions" in data:
            return data["predictions"]

        elif isinstance(data, list):
            return data

        else:
            raise ValueError(f"Unexpected placement response type: {type(data)}, content: {data}")

    except Exception as e:
        print(f"[Error] Failed to get placement prediction: {e}")
        return [0.0]




