"""
ANZSCO 482 Occupation Eligibility Assessment Script
Uses Gemini 2.5 Flash to assess job descriptions against ANZSCO 482 occupation list
"""

import json
import os
from typing import Dict, List
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')  # Set your API key as environment variable

SYSTEM_PROMPT = """
You are an ANZSCO Subclass 482 occupation assessor.

Your task is to determine whether a given job is eligible for Subclass 482 sponsorship by matching it ONLY against the ANZSCO 482 Eligible Occupation List provided below.

STRICT RULES:
1. Assess eligibility based on actual job duties, responsibilities, authority, and skill level — NOT job title alone.
2. You may ONLY select an occupation from the ANZSCO 482 Eligible Occupation List below.
3. If the role does not clearly and convincingly match an occupation’s core ANZSCO duties and required skill level, mark it as NOT eligible.
4. Operational, support, assistant, coordinator, technician, or execution-only roles are NOT eligible unless they clearly meet ANZSCO professional or managerial standards.
5. If there is ambiguity, insufficient evidence, or partial alignment, default to NOT eligible.
6. Do NOT invent occupations, ANZSCO codes, or eligibility rules.
7. Do NOT apply any visa logic beyond occupation matching.

ASSESSMENT METHOD:
- Identify the closest matching occupation from the list below.
- Verify that at least 60–70% of the role’s primary duties align with the ANZSCO occupation.
- Confirm the role meets the expected ANZSCO skill level.
- If all conditions are met, eligible = true. Otherwise, eligible = false.

ANZSCO 482 ELIGIBLE OCCUPATIONS:
ANZSCO 482 Eligible Occupations:
Chief Executive or Managing Director (111111)
Corporate General Manager (111211)
Aquaculture Farmer (121111)
Apiarist (121311)
Dairy Cattle Farmer (121313)
Goat Farmer (121315)
Pig Farmer (121318)
Poultry Farmer (121321)
Flower Grower (121611)
Sales and Marketing Manager (131112)
Advertising Manager (131113)
Corporate Services Manager (132111)
Finance Manager (132211)
Human Resource Manager (132311)
Policy and Planning Manager (132411)
Research and Development Manager (132511)
Construction Project Manager (133111)
Project Builder (133112)
Engineering Manager (133211)
Production Manager (Forestry) (133511)
Production Manager (Manufacturing) (133512)
Supply and Distribution Manager (133611)
Procurement Manager (133612)
Medical Administrator/ Medical Superintendent (134211)
Nursing Clinical Director (134212)
Primary Health Organisation Manager (134213)
School Principal (134311)
Faculty Head (134411)
Education Managers nec (134499)
Chief Information Officer (135111)
ICT Project Manager (135112)
ICT Managers nec (135199)
Arts Administrator or Manager (139911)
Environmental Manager (139912)
Laboratory Manager (139913)
Quality Assurance Manager (139916)
Regulatory Affairs Manager (139917)
Hotel or Motel Manager (141311)
Licensed Club Manager (141411)
Accommodation and Hospitality Managers nec (141999)
Retail Manager (General) (142111)
Travel Agency Manager (142116)
Fleet Manager (149411)
Boarding Kennel or Cattery Operator (149911)
Cinema or Theatre Manager (149912)
Equipment Hire Manager (149915)
Hospitality, Retail and Service Managers nec (149999)
Music Director (211212)
Artistic Director (212111)
Program Director (Television or Radio) (212315)
Stage Manager (212316)
Technical Director (212317)
Video Producer (212318)
Print Journalist (212413)
Radio Journalist (212414)
Technical Writer (212415)
Television Journalist (212416)
Journalists and Other Writers nec (212499)
Accountant (General) (221111)
Management Accountant (221112)
Taxation Accountant (221113)
Company Secretary (221211)
External Auditor (221213)
Internal Auditor (221214)
Finance Broker (222112)
Insurance Broker (222113)
Financial Investment Adviser (222311)
Human Resource Adviser (223111)
Recruitment Consultant (223112)
Workplace Relations Adviser (223113)
Actuary (224111)
Mathematician (224112)
Data Analyst (224114)
Data Scientist (224115)
Statistician (224116)
Land Economist (224511)
Valuer (224512)
Organisation and Methods Analyst (224712)
Management Consultant (224713)
Supply Chain Analyst (224714)
Patents Examiner (224914)
Information and Organisation Professionals nec (224999)
Advertising Specialist (225111)
Marketing Specialist (225113)
Content Creator (Marketing) (225114)
ICT Account Manager (225211)
ICT Business Development Manager (225212)
ICT Sales Representative (225213)
Public Relations Professional (225311)
Sales Representative (Industrial Products) (225411)
Sales Representative (Medical and Pharmaceutical Products) (225412)
Technical Sales Representatives nec (225499)
Aeroplane Pilot (231111)
Flying Instructor (231113)
Helicopter Pilot (231114)
Air Transport Professionals nec (231199)
Ship's Engineer (231212)
Architect (232111)
Landscape Architect (232112)
Surveyor (232212)
Cartographer (232213)
Other Spatial Scientist (232214)
Jewellery Designer (232313)
Illustrator (232412)
Multimedia Designer (232413)
Web Designer (232414)
Interior Designer (232511)
Urban and Regional Planner (232611)
Chemical Engineer (233111)
Materials Engineer (233112)
Civil Engineer (233211)
Geotechnical Engineer (233212)
Quantity Surveyor (233213)
Structural Engineer (233214)
Transport Engineer (233215)
Electrical Engineer (233311)
Electronics Engineer (233411)
Industrial Engineer (233511)
Mechanical Engineer (233512)
Production or Plant Engineer (233513)
Mining Engineer (excluding Petroleum) (233611)
Petroleum Engineer (233612)
Aeronautical Engineer (233911)
Agricultural Engineer (233912)
Biomedical Engineer (233913)
Engineering Technologist (233914)
Environmental Engineer (233915)
Naval Architect/ Marine Designer (233916)
Engineering Professionals nec (233999)
Agricultural Consultant (234111)
Agricultural Research Scientist (234114)
Agronomist (234115)
Aquaculture or Fisheries Scientist (234116)
Chemist (234211)
Food Technologist (234212)
Wine Maker (234213)
Environmental Consultant (234312)
Environmental Scientists nec (234399)
Geologist (234411)
Geophysicist (234412)
Hydrogeologist (234413)
Life Scientist (General) (234511)
Biochemist (234513)
Botanist (234515)
Marine Biologist (234516)
Entomologist (234521)
Zoologist (234522)
Life Scientists nec (234599)
Respiratory Scientist (234612)
Veterinarian (234711)
Conservator (234911)
Metallurgist (234912)
Meteorologist (234913)
Physicist (234914)
Natural and Physical Science Professionals nec (234999)
Early Childhood (Pre-primary School) Teacher (241111)
Primary School Teacher (241213)
Middle School Teacher/ Intermediate School Teacher (241311)
Secondary School Teacher (241411)
Special Needs Teacher (241511)
Teacher of the Hearing Impaired (241512)
Teacher of the Sight Impaired (241513)
Special Education Teachers nec (241599)
University Lecturer (242111)
Vocational Education Teacher/ Polytechnic Teacher (242211)
Education Reviewer (249112)
Music Teacher (Private Tuition) (249214)
Private Tutors and Teachers nec (249299)
Dietitian (251111)
Medical Diagnostic Radiographer (251211)
Medical Radiation Therapist (251212)
Nuclear Medicine Technologist (251213)
Sonographer (251214)
Occupational Health and Safety Adviser (251312)
Optometrist (251411)
Orthoptist (251412)
Hospital Pharmacist (251511)
Industrial Pharmacist (251512)
Retail Pharmacist (251513)
Orthotist or Prosthetist (251912)
Health Diagnostic and Promotion Professionals nec (251999)
Traditional Chinese Medicine Practitioner (252214)
Complementary Health Therapists nec (252299)
Dental Specialist (252311)
Dentist (252312)
Occupational Therapist (252411)
Physiotherapist (252511)
Podiatrist (252611)
Audiologist (252711)
Speech Pathologist/ Speech Language Therapist (252712)
General Practitioner (253111)
Resident Medical Officer (253112)
Anaesthetist (253211)
Specialist Physician (General Medicine) (253311)
Cardiologist (253312)
Clinical Haematologist (253313)
Medical Oncologist (253314)
Endocrinologist (253315)
Gastroenterologist (253316)
Intensive Care Specialist (253317)
Neurologist (253318)
Paediatrician (253321)
Renal Medicine Specialist (253322)
Rheumatologist (253323)
Thoracic Medicine Specialist (253324)
Specialist Physicians nec (253399)
Psychiatrist (253411)
Surgeon (General) (253511)
Cardiothoracic Surgeon (253512)
Neurosurgeon (253513)
Orthopaedic Surgeon (253514)
Otorhinolaryngologist (253515)
Paediatric Surgeon (253516)
Plastic and Reconstructive Surgeon (253517)
Urologist (253518)
Vascular Surgeon (253521)
Dermatologist (253911)
Emergency Medicine Specialist (253912)
Obstetrician and Gynaecologist (253913)
Ophthalmologist (253914)
Pathologist (253915)
Diagnostic and Interventional Radiologist (253917)
Radiation Oncologist (253918)
Medical Practitioners nec (253999)
Midwife (254111)
Nurse Educator (254211)
Nurse Researcher (254212)
Nurse Practitioner (254411)
Registered Nurse (Aged Care) (254412)
Registered Nurse (Child and Family Health) (254413)
Registered Nurse (Community Health) (254414)
Registered Nurse (Critical Care and Emergency) (254415)
Registered Nurse (Developmental Disability) (254416)
Registered Nurse (Disability and Rehabilitation) (254417)
Registered Nurse (Medical) (254418)
Registered Nurse (Medical Practice) (254421)
Registered Nurse (Mental Health) (254422)
Registered Nurse (Perioperative) (254423)
Registered Nurse (Surgical) (254424)
Registered Nurse (Paediatrics) (254425)
Registered Nurses nec (254499)


OUTPUT REQUIREMENTS:
- Return ONLY valid JSON.
- Do NOT include any text outside the JSON.

{
  "eligible": true | false,
  "occupation": "",
  "anzsco_code": "",
  "confidence_score": 0.0,
  "reason": ""
}

"""


class ANZSCOAssessor:
    def __init__(self, api_key: str):
        """Initialize the ANZSCO assessor with Gemini API"""
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        genai.configure(api_key=api_key)
        # Try gemini-1.5-flash instead of 2.0-flash-exp (quota issues)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def assess_job(self, job_title: str, job_description: str) -> Dict:
        """
        Assess a single job against ANZSCO 482 occupation list
        
        Args:
            job_title: The job title
            job_description: The full job description
            
        Returns:
            Dictionary with eligibility assessment
        """
        user_prompt = f"""Job Title: {job_title}

Job Description:
{job_description}
"""
        
        try:
            # Create the prompt with system context and user input
            full_prompt = f"{SYSTEM_PROMPT}\n\nUSER:\n{user_prompt}"
            
            # Generate assessment
            response = self.model.generate_content(full_prompt)
            
            # Parse JSON response
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            assessment = json.loads(response_text.strip())
            return assessment
            
        except Exception as e:
            print(f"Error assessing job '{job_title}': {str(e)}")
            return {
                "eligible": False,
                "occupation": "",
                "anzsco_code": "",
                "confidence_score": 0,
                "reason": f"Error during assessment: {str(e)}"
            }
    
    def assess_jobs_from_file(self, input_file: str, output_file: str):
        """
        Assess all jobs from input JSON file and save results
        
        Args:
            input_file: Path to input JSON file with jobs
            output_file: Path to output JSON file for results
        """
        # Load jobs
        print(f"Loading jobs from {input_file}...")
        with open(input_file, 'r', encoding='utf-8') as f:
            jobs = json.load(f)
        
        print(f"Found {len(jobs)} jobs to assess")
        
        # Assess each job
        results = []
        for i, job in enumerate(jobs, 1):
            print(f"\nAssessing job {i}/{len(jobs)}: {job.get('job_title', 'Unknown')}")
            
            # Get assessment
            assessment = self.assess_job(
                job.get('job_title', ''),
                job.get('job_description', '')
            )
            
            # Combine original job data with assessment
            result = {
                **job,  # Original job data
                "anzsco_assessment": assessment  # Add assessment
            }
            
            results.append(result)
            
            # Print result
            if assessment['eligible']:
                print(f"✓ ELIGIBLE: {assessment['occupation']} ({assessment['anzsco_code']}) - Confidence: {assessment['confidence_score']}")
            else:
                print(f"✗ NOT ELIGIBLE: {assessment['reason']}")
        
        # Save results
        print(f"\n\nSaving results to {output_file}...")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Print summary
        eligible_count = sum(1 for r in results if r['anzsco_assessment']['eligible'])
        print(f"\n{'='*60}")
        print(f"ASSESSMENT SUMMARY")
        print(f"{'='*60}")
        print(f"Total jobs assessed: {len(results)}")
        print(f"Eligible jobs: {eligible_count} ({eligible_count/len(results)*100:.1f}%)")
        print(f"Not eligible: {len(results) - eligible_count} ({(len(results) - eligible_count)/len(results)*100:.1f}%)")
        print(f"\nResults saved to: {output_file}")


def main():
    """Main execution function"""
    # Configuration
    INPUT_FILE = "indeed_jobs_dynamic2.json"
    OUTPUT_FILE = "indeed_jobs_anzsco_assessed.json"
    
    # Check for API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("ERROR: GEMINI_API_KEY environment variable not set")
        print("\nPlease set your Gemini API key:")
        print("export GEMINI_API_KEY='your-api-key-here'")
        return
    
    # Initialize assessor
    assessor = ANZSCOAssessor(api_key)
    
    # Run assessment
    assessor.assess_jobs_from_file(INPUT_FILE, OUTPUT_FILE)


if __name__ == "__main__":
    main()
