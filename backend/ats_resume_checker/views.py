import os
import fitz
import docx
import language_tool_python
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from collections import Counter

REQUIRED_SECTIONS = ['education', 'experience', 'skills', 'projects', 'contact']
ACTION_VERBS = ['developed', 'managed', 'designed', 'implemented', 'created', 'led']
KEYWORDS = ['python', 'django', 'machine learning', 'react', 'sql', 'api']

tool = language_tool_python.LanguageTool('en-US')


def extract_text_from_pdf(path):
    doc = fitz.open(path)
    return "\n".join(page.get_text() for page in doc)


def extract_text_from_docx(path):
    doc = docx.Document(path)
    return "\n".join(para.text for para in doc.paragraphs)


def evaluate_resume(text):
    lower_text = text.lower()

    # Section check
    missing_sections = [sec.title() for sec in REQUIRED_SECTIONS if sec not in lower_text]

    # Action verbs
    action_usage = [word for word in ACTION_VERBS if word in lower_text]
    weak_action_words = len(action_usage) < 3

    # Keyword matching
    used_keywords = [word for word in KEYWORDS if word in lower_text]
    missing_keywords = list(set(KEYWORDS) - set(used_keywords))

    # Grammar check
    matches = tool.check(text)
    grammar_issues = [match.message for match in matches[:5]]

    score = 100
    deductions = 0
    if missing_sections: deductions += len(missing_sections) * 5
    if weak_action_words: deductions += 10
    if missing_keywords: deductions += len(missing_keywords) * 2
    if grammar_issues: deductions += len(grammar_issues) * 2
    score -= deductions
    score = max(score, 0)

    return {
    "score": score,
    "issues": missing_sections + (["Too few action verbs"] if weak_action_words else []) + grammar_issues,
    "suggestions": [
        suggestion for suggestion in [
            f"Add more keywords: {', '.join(missing_keywords)}" if missing_keywords else None,
            "Add more impactful action verbs" if weak_action_words else None,
            *[f"Grammar issue: {issue}" for issue in grammar_issues]
        ] if suggestion is not None  # This filters out None values
    ]
}



@csrf_exempt
def upload_resume(request):
    if request.method == 'POST' and request.FILES.get('resume'):
        resume = request.FILES['resume']
        file_path = default_storage.save(resume.name, resume)
        full_path = os.path.join(default_storage.location, file_path)

        ext = os.path.splitext(resume.name)[1].lower()
        try:
            text = extract_text_from_pdf(full_path) if ext == '.pdf' else extract_text_from_docx(full_path)
            analysis = evaluate_resume(text)
            name = get_name_from_text(text)  # 👈 extract name here
            return JsonResponse({
                'status': 'success',
                'name': name,  # 👈 return name
                'text': text[:1500] + "..." if len(text) > 1500 else text,
                **analysis
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'No file uploaded.'})

@csrf_exempt
def get_name_from_text(text):
    # Simple heuristic: pick the first non-empty line that looks like a name
    lines = text.strip().split('\n')
    for line in lines:
        line = line.strip()
        if line and len(line.split()) in [2, 3]:  # Likely a name
            if all(word[0].isupper() for word in line.split()):  # All words start with capital letter
                return line
    return "User"
