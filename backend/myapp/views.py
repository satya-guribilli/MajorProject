from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
import google.generativeai as genai
import requests
import json
import os
import traceback
import threading
from .utils import deleteTempFiles, check_columns_and_datatypes, delete_file
from .predict import predict_college_stats, predict_students_placement

# Initialize API once globally
genai.configure(api_key="AIzaSyAl5RUjoGI7hbggV4JA5Ll3PJDZwqb0j20")

# Delete temp files on startup
deleteTempFiles()


def check(request):
    return JsonResponse({'status': 'Working....'})


def compare(compare_list, compare_str):
    """Check if any item in compare_list exists in compare_str"""
    return any(i in compare_str for i in compare_list)


@csrf_exempt
def predict_campus_placements(request):
    try:
        print("[DEBUG] Received request method:", request.method)

        if request.method == 'POST':
            print("[DEBUG] Handling POST request...")

            campus_data_file = request.FILES.get('file')
            print("[DEBUG] Uploaded file:", campus_data_file)

            if not campus_data_file:
                print("[ERROR] No file uploaded.")
                return JsonResponse({'message': 'File missing. Please upload an Excel file.'}, status=400)

            print("[DEBUG] Checking columns and datatypes...")
            isError, errorMessage = check_columns_and_datatypes(campus_data_file)
            print("[DEBUG] check_columns_and_datatypes result:", isError, errorMessage)

            if isError:
                print("[ERROR] Column/type validation failed:", errorMessage)
                return JsonResponse({'message': errorMessage}, status=400)

            print("[DEBUG] Running prediction and stats...")
            stats, download_url = predict_college_stats(campus_data_file)
            print("[DEBUG] Prediction complete. Stats:", stats)
            print("[DEBUG] Download URL:", download_url)

            # Auto-delete temp files after 1 hour
            temp_file_path = os.path.join('static', 'temp', os.path.basename(download_url))
            print("[DEBUG] Scheduled deletion for file:", temp_file_path)
            threading.Timer(60 * 60, delete_file, args=[temp_file_path]).start()

            print("[DEBUG] Returning successful JSON response.")
            return JsonResponse({
                'status': 'file uploaded',
                'stats': stats,
                'download_url': download_url
            }, status=200)

        else:
            print("[ERROR] Invalid request method:", request.method)
            return JsonResponse({'message': 'Invalid request method'}, status=405)

    except Exception:
        print("[EXCEPTION] Something went wrong:\n", traceback.format_exc())
        return JsonResponse({
            'message': 'Something went wrong.',
            'error': traceback.format_exc()
        }, status=500)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import traceback

@csrf_exempt
def predict_student_placement(request):
    try:
        print("[INFO] Received request to /predict-student-placement")

        if request.method == 'POST':
            print("[INFO] Request method is POST")

            # Decode and parse JSON
            raw_data = request.body.decode('utf-8')
            print(f"[INFO] Raw request body: {raw_data}")

            data = json.loads(raw_data)
            print(f"[INFO] Parsed JSON data: {data}")

            # Make predictions
            predictions = predict_students_placement(data)
            print(f"[INFO] Predictions generated: {predictions}")

            return JsonResponse({'predictions': predictions}, status=200)
        else:
            print("[WARNING] Request method is not POST")
            return JsonResponse({'message': 'Only POST method is allowed'}, status=405)

    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON decode error: {str(e)}")
        return JsonResponse({'message': 'Invalid JSON format'}, status=400)

    except Exception as e:
        print(f"[ERROR] Exception occurred:\n{traceback.format_exc()}")
        return JsonResponse({'message': 'Something went wrong.', 'error': traceback.format_exc()}, status=500)



@csrf_exempt
def resume_parser(request):
    try:
        if request.method == 'POST':
            resume_file = request.FILES.get('file')
            if not resume_file:
                return JsonResponse({'message': 'Resume file is required'}, status=400)

            resume_file_binary = resume_file.read()
            url = "https://api.resumepuppy.com/parse-resume"
            headers = {"Authorization": "Bearer YOUR_RESUMEPUPPY_API_KEY"}
            files = {"resume": (resume_file.name, resume_file_binary, "application/pdf")}

            response = requests.post(url, files=files, headers=headers)
            if response.status_code != 200:
                return JsonResponse({'message': 'Error parsing resume', 'error': response.text}, status=response.status_code)

            parsed_data = response.json()

            # Extract details safely
            details = {
                "name": parsed_data.get("name", "Not Found"),
                "email": parsed_data.get("email", "Not Found"),
                "phone": parsed_data.get("phone", "Not Found"),
                "skills": parsed_data.get("skills", []),
                "education": parsed_data.get("education", []),
                "experience": parsed_data.get("experience", []),
                "certifications": parsed_data.get("certifications", []),
            }

            return JsonResponse({"details": details}, status=200)

    except Exception:
        return JsonResponse({'message': 'Something went wrong.', 'error': traceback.format_exc()}, status=500)

@csrf_exempt
def recommend_skills(request):
    try:
        print("[INFO] Received request for skills recommendation in .txt format")

        if request.method == 'POST':
            try:
                body = json.loads(request.body.decode('utf-8'))
                print("[INFO] Request body:", body)
            except json.JSONDecodeError:
                return JsonResponse({'message': 'Invalid JSON format'}, status=400)

            if not isinstance(body, dict) or 'skills' not in body:
                return JsonResponse({'message': 'Invalid JSON structure. Expected: { "skills": [...] }'}, status=400)

            user_skills = ', '.join(body['skills'])
            print("[INFO] User skills:", user_skills)

            prompt = f"""
            I am a software developer. Based on my skills: {user_skills},
            recommend additional software development and IT-related skills that would enhance my career.
            Provide 5-10 suggestions.
            """

            model = genai.GenerativeModel("gemini-2.0-flash")
            response = model.generate_content(prompt)

            if not response.text:
                return JsonResponse({'message': 'No recommendations generated'}, status=500)

            recommended_skills = response.text.strip().split("\n")
            recommended_skills = [skill.strip("-• ") for skill in recommended_skills if skill.strip()]
            print("[SUCCESS] Recommended skills:", recommended_skills)

            # Write to .txt file
            filename = "recommended_skills.txt"
            file_content = "\n".join(recommended_skills)

            with open(filename, 'w', encoding='utf-8') as f:
                f.write(file_content)

            with open(filename, 'r', encoding='utf-8') as f:
                response = HttpResponse(f.read(), content_type='text/plain')
                response['Content-Disposition'] = f'attachment; filename="{filename}"'

            # Optional: Delete the file after sending (cleanup)
            os.remove(filename)

            return response

        return JsonResponse({'message': 'Invalid request method'}, status=405)

    except Exception as e:
        print("[EXCEPTION]", traceback.format_exc())
        return JsonResponse({'message': 'Error generating skills', 'error': traceback.format_exc()}, status=500)