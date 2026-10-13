from app import app, db, Student, Employer
from werkzeug.security import generate_password_hash

COMMON_PASSWORD = generate_password_hash('password123', method='pbkdf2:sha256')

def seed_database():
    with app.app_context():
        print("🗑️ Dropping old database tables...")
        db.drop_all()
        
        print("🏗️ Creating new database tables...")
        db.create_all()

        print("👨‍🎓 Seeding 8 Students...")
        students_data = [
            {
                "first": "Ahmad", "last": "Ali", "phone": "0501234567", "dob": "2000-05-14",
                "gender": "Male", "nationality": "Saudi", "location": "Riyadh",
                "uni": "Arab Open University", "major": "Computer Science", "gpa": 3.8,
                "email": "ahmad@student.aou.edu", "linkedin": "https://linkedin.com/in/ahmad",
                "skills": "Python, Java, C++, Algorithms, Software Design, Data Structures",
                "soft_skills": "Problem Solving, Collaborative, Meticulous",
                "pic": "default.jpg", "cv": "dummy.pdf", "transcript": "dummy_transcript.pdf"
            },
            {
                "first": "Sara", "last": "Khalid", "phone": "0507654321", "dob": "2001-08-22",
                "gender": "Female", "nationality": "Jordanian", "location": "Jeddah",
                "uni": "Arab Open University", "major": "Data Science", "gpa": 3.9,
                "email": "sara@student.aou.edu", "linkedin": "https://linkedin.com/in/sara",
                "skills": "Python, SQL, Machine Learning, Data Mining, Statistics",
                "soft_skills": "Analytical, Proactive, Purpose-driven",
                "pic": "default.jpg", "cv": "dummy.pdf", "transcript": "dummy_transcript.pdf"
            },
            {
                "first": "Omar", "last": "Yasser", "phone": "0551122334", "dob": "1999-11-05",
                "gender": "Male", "nationality": "Egyptian", "location": "Dammam",
                "uni": "Arab Open University", "major": "Cybersecurity", "gpa": 3.5,
                "email": "omar@student.aou.edu", "linkedin": "",
                "skills": "Network Security, Cryptography, Ethical Hacking, Linux",
                "soft_skills": "Responsible, Professional, Critical Thinking",
                "pic": "default.jpg", "cv": "dummy.pdf", "transcript": "dummy_transcript.pdf"
            },
            {
                "first": "Lina", "last": "Fares", "phone": "0569988776", "dob": "2002-02-18",
                "gender": "Female", "nationality": "Saudi", "location": "Riyadh",
                "uni": "Arab Open University", "major": "Information Technology", "gpa": 3.2,
                "email": "lina@student.aou.edu", "linkedin": "https://linkedin.com/in/lina",
                "skills": "Computer Networks, Linux, Systems Administration",
                "soft_skills": "Troubleshooting, Adaptable, Responsive",
                "pic": "default.jpg", "cv": "dummy.pdf", "transcript": "dummy_transcript.pdf"
            },
            {
                "first": "Tariq", "last": "Ziad", "phone": "0544455667", "dob": "2001-12-30",
                "gender": "Male", "nationality": "Saudi", "location": "Mecca",
                "uni": "Arab Open University", "major": "Software Engineering", "gpa": 2.8,
                "email": "tariq@student.aou.edu", "linkedin": "",
                "skills": "HTML, CSS, JavaScript",
                "soft_skills": "Communication, Teamwork",
                "pic": "default.jpg", "cv": "dummy.pdf", "transcript": "dummy_transcript.pdf"
            },
            {
                "first": "Nour", "last": "Hisham", "phone": "0598877665", "dob": "2000-07-07",
                "gender": "Female", "nationality": "Lebanese", "location": "Dubai",
                "uni": "Arab Open University", "major": "Information Systems", "gpa": 3.7,
                "email": "nour@student.aou.edu", "linkedin": "https://linkedin.com/in/nour",
                "skills": "Systems Analysis, Project Management, SQL, Requirements Analysis",
                "soft_skills": "Communication, Collaborative, Professional",
                "pic": "default.jpg", "cv": "dummy.pdf", "transcript": "dummy_transcript.pdf"
            },
            {
                "first": "Faisal", "last": "Saad", "phone": "0533322111", "dob": "1998-09-15",
                "gender": "Male", "nationality": "Saudi", "location": "Dhahran",
                "uni": "King Saud University", "major": "Computer Engineering", "gpa": 3.4,
                "email": "faisal@student.ksu.edu", "linkedin": "https://linkedin.com/in/faisal",
                "skills": "C, C++, Embedded Systems, Digital Design, Circuits",
                "soft_skills": "Inventive, Meticulous, Self-directed",
                "pic": "default.jpg", "cv": "dummy.pdf", "transcript": "dummy_transcript.pdf"
            },
            {
                "first": "Maha", "last": "Salem", "phone": "0500001111", "dob": "2001-04-20",
                "gender": "Female", "nationality": "Syrian", "location": "Riyadh",
                "uni": "Arab Open University", "major": "Computer Science", "gpa": 3.6,
                "email": "maha@student.aou.edu", "linkedin": "",
                "skills": "Python, Java, Database Practice, Web Development",
                "soft_skills": "Problem Solving, Meticulous",
                "pic": "default.jpg", "cv": "dummy.pdf", "transcript": "dummy_transcript.pdf"
            }
        ]

        for s in students_data:
            student = Student(
                first_name=s['first'], last_name=s['last'], phone=s['phone'], dob=s['dob'],
                gender=s['gender'], nationality=s['nationality'], location=s['location'],
                university=s['uni'], major=s['major'], gpa_scale=4.0, gpa=s['gpa'],
                email=s['email'], password_hash=COMMON_PASSWORD,
                linkedin_link=s['linkedin'], github_link="", portfolio_link="",
                skills=s['skills'], soft_skills=s['soft_skills'],
                profile_pic=s['pic'], cv_file=s['cv'], transcript_file=s['transcript']
            )
            db.session.add(student)

        print("🏢 Seeding 4 Employers...")
        employers_data = [
            {
                "company": "Elm", "website": "https://elm.sa", "industry": "Technology",
                "location": "Riyadh", "cr": "1010101010", "recruiter": "Khalid Majed",
                "job": "HR Tech Recruiter", "email": "khalid@elm.sa", "phone": "0112223333",
                "linkedin": "https://linkedin.com/in/khalid"
            },
            {
                "company": "STC", "website": "https://stc.com.sa", "industry": "Telecommunications",
                "location": "Riyadh", "cr": "2020202020", "recruiter": "Abdullah Nasser",
                "job": "Talent Acquisition", "email": "abdullah@stc.com.sa", "phone": "0114445555",
                "linkedin": "https://linkedin.com/in/abdullah"
            },
            {
                "company": "Google Arabia", "website": "https://google.com", "industry": "Technology",
                "location": "Dubai", "cr": "3030303030", "recruiter": "Sarah Jones",
                "job": "Regional Recruiter", "email": "sarah@google.com", "phone": "00971555555",
                "linkedin": "https://linkedin.com/in/sarah"
            },
            {
                "company": "Aramco", "website": "https://aramco.com", "industry": "Energy & Technology",
                "location": "Dhahran", "cr": "4040404040", "recruiter": "Fahad Al-Dossari",
                "job": "Cybersecurity HR Specialist", "email": "fahad@aramco.com", "phone": "0138889999",
                "linkedin": ""
            }
        ]
        
        for e in employers_data:
            employer = Employer(
                company_name=e['company'], website=e['website'], industry=e['industry'],
                location=e['location'], cr_number=e['cr'], recruiter_name=e['recruiter'],
                job_title=e['job'], work_email=e['email'], phone=e['phone'],
                linkedin_link=e['linkedin'], password_hash=COMMON_PASSWORD
            )
            db.session.add(employer)

        db.session.commit()
        print("✅ Database successfully seeded with 8 Students and 4 Employers!")
        print("🔑 Password for all generated accounts is: password123")

if __name__ == "__main__":
    seed_database()