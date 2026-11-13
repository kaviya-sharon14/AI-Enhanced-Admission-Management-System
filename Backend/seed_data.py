"""
Seed initial administrative, course, and student data for AI-Enhanced Admission Management System.
"""

import os
from database import get_db_connection, init_db, hash_password
from services.ml_service import ml_service
from services.genai_service import genai_service

def seed_all():
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("--- Seeding Users ---")
    users = [
        ("Dr. K. Ramanathan (Admission Director)", "admin@institution.edu", hash_password("Admin@123"), "admin", "+91 98765 43210"),
        ("Prof. S. Venkatesh (Admission Officer)", "officer@institution.edu", hash_password("Officer@123"), "admin", "+91 98765 43211"),
        ("Priya Sharma", "student@institution.edu", hash_password("Student@123"), "student", "+91 91234 56780"),
        ("Aarav Patel", "aarav.patel@example.com", hash_password("Student@123"), "student", "+91 91234 56781"),
        ("Sneha Kulkarni", "sneha.k@example.com", hash_password("Student@123"), "student", "+91 91234 56782"),
        ("Mohammed Farhan", "farhan.m@example.com", hash_password("Student@123"), "student", "+91 91234 56783"),
        ("Ananya Iyer", "ananya.iyer@example.com", hash_password("Student@123"), "student", "+91 91234 56784"),
        ("Kavitha Murugan", "kavitha.m@example.com", hash_password("Student@123"), "student", "+91 91234 56785"),
        ("Rahul Verma", "rahul.v@example.com", hash_password("Student@123"), "student", "+91 91234 56786"),
        ("Deepak Raj", "deepak.raj@example.com", hash_password("Student@123"), "student", "+91 91234 56787")
    ]
    
    for name, email, pw, role, phone in users:
        cursor.execute("""
        INSERT OR IGNORE INTO users (name, email, password_hash, role, phone)
        VALUES (?, ?, ?, ?, ?)
        """, (name, email, pw, role, phone))
    conn.commit()
    
    print("--- Seeding Courses ---")
    courses = [
        ("CSE-101", "B.Tech Computer Science & Engineering", "School of Computing", 120, 75.0, 70.0),
        ("AIDS-102", "B.Tech Artificial Intelligence & Data Science", "School of Computing", 60, 78.0, 75.0),
        ("ECE-103", "B.Tech Electronics & Communication Engineering", "School of Electrical Sciences", 90, 70.0, 65.0),
        ("IT-104", "B.Tech Information Technology", "School of Computing", 60, 72.0, 68.0),
        ("MECH-105", "B.Tech Mechanical Engineering", "School of Mechanical Sciences", 60, 65.0, 60.0),
        ("BIO-106", "B.Tech Biotechnology", "School of Bioengineering", 40, 68.0, 62.0),
        ("MBA-201", "Master of Business Administration (MBA)", "School of Management", 80, 60.0, 65.0),
        ("DS-202", "M.Sc Data Science & Analytics", "School of Mathematics & Computing", 45, 70.0, 70.0)
    ]
    
    for code, name, dept, seats, min_gpa, min_ent in courses:
        cursor.execute("""
        INSERT OR IGNORE INTO courses (code, name, department, seats, min_gpa, min_entrance)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (code, name, dept, seats, min_gpa, min_ent))
    conn.commit()

    print("--- Seeding Realistic Student Applications ---")
    # Check if applications already exist
    cursor.execute("SELECT COUNT(*) FROM applications")
    if cursor.fetchone()[0] == 0:
        seed_applications = [
            {
                "app_no": "ADM-2026-0001",
                "user_email": "student@institution.edu",
                "name": "Priya Sharma",
                "phone": "+91 91234 56780",
                "dob": "2005-04-12",
                "gender": "Female",
                "address": "45, Temple View St, Chennai, TN",
                "course_code": "CSE-101",
                "gpa": 91.5,
                "entrance": 94.0,
                "attendance": 96.0,
                "prev_score": 93.0,
                "category": "General",
                "extracurricular": "State_Level",
                "status": "Approved",
                "remarks": "Merit seat allocated. Outstanding entrance ranking.",
                "doc_name": "Priya_Sharma_Marksheet.pdf"
            },
            {
                "app_no": "ADM-2026-0002",
                "user_email": "aarav.patel@example.com",
                "name": "Aarav Patel",
                "phone": "+91 91234 56781",
                "dob": "2005-08-22",
                "gender": "Male",
                "address": "12, Navrangpura, Ahmedabad, GJ",
                "course_code": "AIDS-102",
                "gpa": 88.0,
                "entrance": 89.5,
                "attendance": 92.0,
                "prev_score": 86.0,
                "category": "OBC",
                "extracurricular": "National_Level",
                "status": "Approved",
                "remarks": "Approved under OBC quota + National Sports distinction.",
                "doc_name": "Aarav_Patel_Certificates.pdf"
            },
            {
                "app_no": "ADM-2026-0003",
                "user_email": "sneha.k@example.com",
                "name": "Sneha Kulkarni",
                "phone": "+91 91234 56782",
                "dob": "2005-01-19",
                "gender": "Female",
                "address": "78, Shivaji Park, Pune, MH",
                "course_code": "IT-104",
                "gpa": 82.0,
                "entrance": 79.0,
                "attendance": 88.0,
                "prev_score": 80.5,
                "category": "General",
                "extracurricular": "School_Level",
                "status": "Under Review",
                "remarks": "Document verification in progress.",
                "doc_name": "Sneha_Kulkarni_AcademicRecord.pdf"
            },
            {
                "app_no": "ADM-2026-0004",
                "user_email": "farhan.m@example.com",
                "name": "Mohammed Farhan",
                "phone": "+91 91234 56783",
                "dob": "2004-11-05",
                "gender": "Male",
                "address": "21, Mall Road, Bengaluru, KA",
                "course_code": "ECE-103",
                "gpa": 76.5,
                "entrance": 74.0,
                "attendance": 84.0,
                "prev_score": 75.0,
                "category": "OBC",
                "extracurricular": "None",
                "status": "Submitted",
                "remarks": None,
                "doc_name": "Farhan_HSC_Marksheet.pdf"
            },
            {
                "app_no": "ADM-2026-0005",
                "user_email": "ananya.iyer@example.com",
                "name": "Ananya Iyer",
                "phone": "+91 91234 56784",
                "dob": "2005-06-30",
                "gender": "Female",
                "address": "15, Jubilee Hills, Hyderabad, TS",
                "course_code": "CSE-101",
                "gpa": 95.0,
                "entrance": 96.5,
                "attendance": 98.0,
                "prev_score": 97.0,
                "category": "General",
                "extracurricular": "National_Level",
                "status": "Approved",
                "remarks": "Institutional topper scholarship recommended.",
                "doc_name": "Ananya_Iyer_Dossier.pdf"
            },
            {
                "app_no": "ADM-2026-0006",
                "user_email": "kavitha.m@example.com",
                "name": "Kavitha Murugan",
                "phone": "+91 91234 56785",
                "dob": "2005-09-14",
                "gender": "Female",
                "address": "90, Gandhi Nagar, Madurai, TN",
                "course_code": "BIO-106",
                "gpa": 84.0,
                "entrance": 81.0,
                "attendance": 90.0,
                "prev_score": 83.0,
                "category": "SC_ST",
                "extracurricular": "State_Level",
                "status": "Approved",
                "remarks": "Approved with full institutional fee waiver support.",
                "doc_name": "Kavitha_Certificates.pdf"
            },
            {
                "app_no": "ADM-2026-0007",
                "user_email": "rahul.v@example.com",
                "name": "Rahul Verma",
                "phone": "+91 91234 56786",
                "dob": "2004-12-02",
                "gender": "Male",
                "address": "33, Civil Lines, Jaipur, RJ",
                "course_code": "MECH-105",
                "gpa": 56.0,
                "entrance": 46.0,
                "attendance": 65.0,
                "prev_score": 54.0,
                "category": "General",
                "extracurricular": "None",
                "status": "Rejected",
                "remarks": "Entrance score and GPA below minimum engineering cutoff.",
                "doc_name": "Rahul_Verma_Documents.pdf"
            },
            {
                "app_no": "ADM-2026-0008",
                "user_email": "deepak.raj@example.com",
                "name": "Deepak Raj",
                "phone": "+91 91234 56787",
                "dob": "2005-03-27",
                "gender": "Male",
                "address": "104, Lake View, Kochi, KL",
                "course_code": "MBA-201",
                "gpa": 71.0,
                "entrance": 72.0,
                "attendance": 80.0,
                "prev_score": 69.5,
                "category": "EWS",
                "extracurricular": "School_Level",
                "status": "Submitted",
                "remarks": None,
                "doc_name": "Deepak_Raj_Portfolio.pdf"
            }
        ]

        # Dummy document sample creation in uploads
        uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
        os.makedirs(uploads_dir, exist_ok=True)

        for app_data in seed_applications:
            # Fetch user_id
            cursor.execute("SELECT id FROM users WHERE email = ?", (app_data["user_email"],))
            user_row = cursor.fetchone()
            user_id = user_row[0] if user_row else 1
            
            # Fetch course name
            cursor.execute("SELECT name FROM courses WHERE code = ?", (app_data["course_code"],))
            course_name = cursor.fetchone()[0]

            # Generate sample placeholder file if not exists
            dummy_file_path = os.path.join(uploads_dir, app_data["doc_name"])
            if not os.path.exists(dummy_file_path):
                with open(dummy_file_path, 'w') as f:
                    f.write(f"Verified Academic Document for {app_data['name']}\nCourse: {course_name}\nApplication: {app_data['app_no']}")

            # Run ML Model
            ml_input = {
                'academic_gpa': app_data['gpa'],
                'entrance_score': app_data['entrance'],
                'attendance_pct': app_data['attendance'],
                'prev_academic_score': app_data['prev_score'],
                'category': app_data['category'],
                'extracurricular': app_data['extracurricular']
            }
            ml_res = ml_service.predict_eligibility(ml_input)

            # Generate AI Evaluation Report
            applicant_profile = {
                'full_name': app_data['name'],
                'course_name': course_name,
                'course_code': app_data['course_code'],
                'academic_gpa': app_data['gpa'],
                'entrance_score': app_data['entrance'],
                'attendance_pct': app_data['attendance'],
                'prev_academic_score': app_data['prev_score'],
                'category': app_data['category'],
                'extracurricular': app_data['extracurricular']
            }
            ai_rep = genai_service.generate_evaluation_report(applicant_profile, ml_res)

            cursor.execute("""
            INSERT INTO applications (
                application_no, user_id, full_name, email, phone, dob, gender, address,
                course_code, academic_gpa, entrance_score, attendance_pct, prev_academic_score,
                category, extracurricular, document_path, document_name, status,
                ml_prediction, ml_probability,
                ai_evaluation_summary, ai_recommendation, ai_profile_insights, ai_explanation,
                admin_remarks, reviewed_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                app_data["app_no"],
                user_id,
                app_data["name"],
                app_data["user_email"],
                app_data["phone"],
                app_data["dob"],
                app_data["gender"],
                app_data["address"],
                app_data["course_code"],
                app_data["gpa"],
                app_data["entrance"],
                app_data["attendance"],
                app_data["prev_score"],
                app_data["category"],
                app_data["extracurricular"],
                dummy_file_path,
                app_data["doc_name"],
                app_data["status"],
                ml_res["prediction"],
                ml_res["probability"],
                ai_rep["evaluation_summary"],
                ai_rep["admission_recommendation"],
                ai_rep["profile_insights"],
                ai_rep["approval_rejection_explanation"],
                app_data["remarks"],
                "Dr. K. Ramanathan" if app_data["status"] in ["Approved", "Rejected"] else None
            ))
        conn.commit()
        print("Pre-seeded 8 diverse student applications with full ML + AI evaluations.")

    conn.close()
    print("Database seeding completed successfully.")

if __name__ == '__main__':
    seed_all()
