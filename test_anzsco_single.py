"""
Test ANZSCO assessment with a single job
"""

import json
import os
from dotenv import load_dotenv
from assess_anzsco_eligibility import ANZSCOAssessor

# Load environment variables from .env file
load_dotenv()

# Check for API key
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("ERROR: GEMINI_API_KEY environment variable not set")
    print("\nPlease set your Gemini API key:")
    print("export GEMINI_API_KEY='your-api-key-here'")
    exit(1)

# Load one job from the file
with open('indeed_jobs_dynamic2.json', 'r', encoding='utf-8') as f:
    jobs = json.load(f)

# Test with the first job
test_job = jobs[0]
print(f"Testing with job: {test_job['job_title']}")
print(f"Employer: {test_job['employer_name']}")
print(f"Location: {test_job['location']}")
print("\n" + "="*60)

# Initialize assessor
assessor = ANZSCOAssessor(api_key)

# Assess the job
assessment = assessor.assess_job(
    test_job['job_title'],
    test_job['job_description']
)

# Print results
print("\nASSESSMENT RESULT:")
print("="*60)
print(json.dumps(assessment, indent=2))
print("="*60)

if assessment['eligible']:
    print(f"\n✓ ELIGIBLE for ANZSCO 482")
    print(f"Occupation: {assessment['occupation']}")
    print(f"Code: {assessment['anzsco_code']}")
    print(f"Confidence: {assessment['confidence_score']}")
else:
    print(f"\n✗ NOT ELIGIBLE for ANZSCO 482")
    print(f"Reason: {assessment['reason']}")
