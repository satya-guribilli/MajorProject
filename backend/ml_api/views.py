import os
import pickle
import json
import numpy as np
import pandas as pd
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, 'ml_api', 'models')

salary_model_path = os.path.join(MODELS_DIR, 'salary_model.pkl')
placement_model_path = os.path.join(MODELS_DIR, 'placed_model.pkl')

# Load models only once
with open(salary_model_path, 'rb') as f:
    salary_model = pickle.load(f)

with open(placement_model_path, 'rb') as f:
    placement_model = pickle.load(f)

# Define expected feature order for both models
placement_features = [
    'cgpa', 'inter_gpa', 'ssc_gpa', 'internships', 'no_of_projects',
    'is_participate_hackathon', 'is_participated_extracurricular',
    'no_of_programming_languages', 'dsa', 'mobile_dev', 'web_dev',
    'Machine Learning', 'cloud', 'tier_1', 'tier_2', 'tier_3',
    'gender_F', 'gender_M', 'gender_nan', 'branch_CSE', 'branch_ECE',
    'branch_EEE', 'branch_MECH',
]

# ---------------------- PREDICT SALARY ----------------------


@csrf_exempt
@api_view(['POST'])
def predict_salary(request):
    try:
        input_data = request.data[0] if isinstance(request.data, list) else request.data

        # Create a DataFrame with correct feature names
        input_df = pd.DataFrame([input_data], columns=placement_features)

        prediction = salary_model.predict(input_df)[0]

        return Response({'salary_prediction': round(float(prediction), 2)})

    except KeyError as ke:
        return Response({'error': f"Missing feature: {str(ke)}"}, status=400)
    except Exception as e:
        print("Prediction error (salary):", str(e))
        return Response({'error': str(e)}, status=500)


# ---------------------- PREDICT PLACEMENT ----------------------

@csrf_exempt
@api_view(['POST'])
def predict_placement(request):
    try:
        input_data = request.data[0] if isinstance(request.data, list) else request.data

        # Create a DataFrame with correct feature names
        input_df = pd.DataFrame([input_data], columns=placement_features)

        prediction = placement_model.predict(input_df)[0]
        probabilities = placement_model.predict_proba(input_df)[0]
        placed_prob = round(probabilities[1] * 100, 2)

        return Response({
            'placement_prediction': int(prediction),
            'placement_probability': placed_prob
        })

    except KeyError as ke:
        return Response({'error': f"Missing feature: {str(ke)}"}, status=400)
    except Exception as e:
        print("Prediction error (placement):", str(e))
        return Response({'error': str(e)}, status=500)


