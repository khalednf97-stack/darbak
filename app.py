from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from readiness_engine import ReadinessEngine, market_db
import os
import PyPDF2
import json
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google import genai
from google.genai import types

# --- إعداد مفتاح الذكاء الاصطناعي ---
ai_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", "AIzaSyDW6Z0LGRWJ8cvdxREW3ybpFtEeAqlWNWY"))# ⚠️ ضع مفتاحك هنا

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///darbak.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

db = SQLAlchemy(app)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ==========================================
# إعدادات الإيميل
# ==========================================
SENDER_EMAIL = "darbak.ai.project@gmail.com"
SENDER_PASSWORD = "twdn ywyc kfpy xhfo"  

# ==========================================
# CC2020 COMPETENCY-BASED KNOWLEDGE BASE
# ==========================================
CC2020_KNOWLEDGE_BASE = {
    "Software Developer / Engineer": {
        "best_fit_majors": ["Computer Science", "Software Engineering"],
        "required_skills": ["programming fundamentals", "algorithms", "software design", "data structures", "software verification", "java", "c++", "python"],
        "required_dispositions": ["meticulous", "inventive", "collaborative", "problem solving"]
    },
    "Data Scientist / Analyst": {
        "best_fit_majors": ["Data Science", "Computer Science", "Information Systems"],
        "required_skills": ["data and information management", "machine learning", "statistics", "data mining", "big data", "python", "sql", "data visualization"],
        "required_dispositions": ["analytical", "meticulous", "proactive", "purpose-driven"]
    },
    "Cybersecurity Analyst / Professional": {
        "best_fit_majors": ["Cybersecurity", "Information Technology", "Computer Science", "Information Systems"],
        "required_skills": ["security policy and management", "security technology", "cryptography", "network security", "risk management", "ethical hacking"],
        "required_dispositions": ["responsible", "professional", "adaptable", "critical thinking"]
    },
    "Database Administrator": {
        "best_fit_majors": ["Information Systems", "Information Technology", "Data Science"],
        "required_skills": ["data management", "database practice", "systems administration", "sql", "data privacy", "enterprise architecture"],
        "required_dispositions": ["meticulous", "responsible", "organized", "responsive"]
    },
    "Network/Systems Administrator": {
        "best_fit_majors": ["Information Technology", "Computer Engineering", "Cybersecurity"],
        "required_skills": ["computer networks", "virtual systems", "platform technologies", "systems administration", "security implementation", "linux"],
        "required_dispositions": ["responsive", "adaptable", "troubleshooting", "responsible"]
    },
    "Business Systems Analyst": {
        "best_fit_majors": ["Information Systems", "Software Engineering"],
        "required_skills": ["systems analysis", "requirements analysis", "project management", "is management", "user experience design"],
        "required_dispositions": ["collaborative", "communication", "professional", "purpose-driven"]
    },
    "Embedded Systems Engineer": {
        "best_fit_majors": ["Computer Engineering", "Computer Science"],
        "required_skills": ["embedded systems", "architecture and organization", "digital design", "circuits and electronics", "c++", "c", "signal processing"],
        "required_dispositions": ["inventive", "meticulous", "passionate", "self-directed"]
    }
}

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    dob = db.Column(db.String(20))
    
    # --- الحقول الجديدة ---
    gender = db.Column(db.String(20), nullable=True)
    nationality = db.Column(db.String(50), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    
    university = db.Column(db.String(100), nullable=True)
    major = db.Column(db.String(50), nullable=True)
    gpa_scale = db.Column(db.Float, default=4.0)
    gpa = db.Column(db.Float, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    linkedin_link = db.Column(db.String(200), nullable=True)
    github_link = db.Column(db.String(200), nullable=True)
    portfolio_link = db.Column(db.String(200), nullable=True) 
    skills = db.Column(db.String(500), nullable=True)
    soft_skills = db.Column(db.String(500), nullable=True)
    profile_pic = db.Column(db.String(150), default='default.jpg')
    cv_file = db.Column(db.String(150), nullable=True)
    transcript_file = db.Column(db.String(150), nullable=False)

    target_job = db.Column(db.String(100), nullable=True)
    last_score = db.Column(db.Integer, nullable=True)
    last_status = db.Column(db.String(50), nullable=True)

    def to_dict(self):
        return {
            "id": self.id, "first_name": self.first_name, "last_name": self.last_name,
            "phone": self.phone, "dob": self.dob, "name": f"{self.first_name} {self.last_name}",
            "gender": self.gender if self.gender else "",
            "nationality": self.nationality if self.nationality else "",
            "location": self.location if self.location else "",
            "email": self.email, "major": self.major if self.major else "",
            "university": self.university if self.university else "",
            "gpa": self.gpa if self.gpa else 0.0, "gpa_scale": self.gpa_scale,
            "linkedin_link": self.linkedin_link if self.linkedin_link else "",
            "github_link": self.github_link if self.github_link else "",
            "portfolio_link": self.portfolio_link if self.portfolio_link else "",
            "skills": self.skills.split(',') if self.skills else [],
            "soft_skills": self.soft_skills.split(',') if self.soft_skills else [],
            "profile_pic": self.profile_pic, "cv_file": self.cv_file,
            "target_job": self.target_job if self.target_job else "",
            "last_score": self.last_score,
            "last_status": self.last_status if self.last_status else ""
        }

class Employer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    website = db.Column(db.String(100))
    industry = db.Column(db.String(50))
    location = db.Column(db.String(50))
    cr_number = db.Column(db.String(20))
    recruiter_name = db.Column(db.String(100), nullable=False)
    job_title = db.Column(db.String(50))
    work_email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    linkedin_link = db.Column(db.String(200), nullable=True)
    password_hash = db.Column(db.String(200), nullable=False)

    def to_dict(self):
        return {
            "id": self.id, "company": self.company_name, "website": self.website, 
            "industry": self.industry, "location": self.location, "cr_number": self.cr_number,
            "recruiter": self.recruiter_name, "job_title": self.job_title, 
            "work_email": self.work_email, "phone": self.phone,
            "linkedin_link": self.linkedin_link if self.linkedin_link else ""
        }

engine = ReadinessEngine(market_db)

with app.app_context():
    db.create_all()

# ==========================================
# مسارات العرض الأساسية
# ==========================================
@app.route('/')
def welcome_page(): return render_template('welcome.html')

@app.route('/login')
def login_page(): return render_template('login.html')

@app.route('/register/student')
def register_student_page(): return render_template('register.html')

@app.route('/register/employer')
def register_employer_page(): return render_template('register_employer.html')

@app.route('/student')
def student_dashboard(): return render_template('student_dashboard.html')

@app.route('/employer')
def employer_dashboard(): return render_template('employer_dashboard.html')

@app.route('/profile')
def profile_page(): return render_template('profile.html')

@app.route('/admin')
def admin_dashboard(): return render_template('admin_dashboard.html')

# ==========================================
# مسارات الـ API وتسجيل الدخول
# ==========================================
@app.route('/api/register/student', methods=['POST'])
def api_register_student():
    if Student.query.filter_by(email=request.form['email']).first():
        return jsonify({"status": "error", "message": "Email already registered!"})
    
    entered_gpa = request.form.get('gpa')
    entered_major = request.form.get('major', '').strip()
    
    if 'transcript_file' not in request.files or request.files['transcript_file'].filename == '':
        return jsonify({"status": "error", "message": "Official Transcript PDF is required!"})
    
    transcript_file = request.files['transcript_file']
    try:
        pdf_reader = PyPDF2.PdfReader(transcript_file)
        pdf_text = "".join([page.extract_text() for page in pdf_reader.pages]).lower()
        if str(entered_gpa) not in pdf_text and f"{float(entered_gpa):.2f}" not in pdf_text:
            return jsonify({"status": "error", "message": f"Verification Failed: GPA {entered_gpa} not found in the transcript."})
        if entered_major.lower() not in pdf_text:
             return jsonify({"status": "error", "message": f"Verification Failed: Major '{entered_major}' not found in the transcript."})
    except Exception as e:
        return jsonify({"status": "error", "message": "Could not read the PDF file."})

    transcript_file.seek(0)
    transcript_filename = secure_filename(transcript_file.filename)
    transcript_file.save(os.path.join(app.config['UPLOAD_FOLDER'], transcript_filename))

    pic_filename = 'default.jpg'
    cv_filename = None
    if 'profile_pic' in request.files and request.files['profile_pic'].filename != '':
        file = request.files['profile_pic']
        pic_filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_filename))
    if 'cv_file' in request.files and request.files['cv_file'].filename != '':
        file = request.files['cv_file']
        cv_filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], cv_filename))

    hashed_password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')

    new_student = Student(
        first_name=request.form.get('first_name'), last_name=request.form.get('last_name'), 
        phone=request.form.get('phone'), dob=request.form.get('dob'),
        gender=request.form.get('gender'), nationality=request.form.get('nationality'),
        location=request.form.get('location'),
        university=request.form.get('university'), major=entered_major,
        gpa_scale=float(request.form.get('gpa_scale', 4.0)), gpa=float(entered_gpa),
        email=request.form.get('email'), password_hash=hashed_password,
        linkedin_link=request.form.get('linkedin_link'),
        github_link=request.form.get('github_link'), 
        portfolio_link=request.form.get('portfolio_link'),
        profile_pic=pic_filename, cv_file=cv_filename, transcript_file=transcript_filename
    )
    db.session.add(new_student)
    db.session.commit()
    return jsonify({"status": "success", "message": "Profile verified and created successfully! Please login."})

@app.route('/api/register/employer', methods=['POST'])
def api_register_employer():
    data = request.json
    if Employer.query.filter_by(work_email=data['work_email']).first():
        return jsonify({"status": "error", "message": "Work email already registered!"})
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    new_employer = Employer(
        company_name=data['company_name'], website=data['website'], industry=data['industry'], 
        location=data['location'], cr_number=data['cr_number'], recruiter_name=data['recruiter_name'], 
        job_title=data['job_title'], work_email=data['work_email'], phone=data['phone'],
        linkedin_link=data.get('linkedin_link'),
        password_hash=hashed_password
    )
    db.session.add(new_employer)
    db.session.commit()
    return jsonify({"status": "success", "message": "Employer account created!"})

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    # الدخول السري للمدير (Admin Backdoor)
    if email == "admin@darbak.ai" and password == "admin123":
        return jsonify({
            "status": "success", 
            "role": "admin", 
            "redirect": "/admin", 
            "user_data": {"name": "System Admin", "email": "admin@darbak.ai"}
        })

    student = Student.query.filter_by(email=email).first()
    if student and check_password_hash(student.password_hash, password):
        return jsonify({"status": "success", "role": "student", "redirect": "/student", "user_data": student.to_dict()})

    employer = Employer.query.filter_by(work_email=email).first()
    if employer and check_password_hash(employer.password_hash, password):
        return jsonify({"status": "success", "role": "employer", "redirect": "/employer", "user_data": employer.to_dict()})

    return jsonify({"status": "error", "message": "Invalid email or password"})

@app.route('/api/profile/update', methods=['POST'])
def api_profile_update():
    role = request.form.get('role')
    email = request.form.get('email')
    
    if role == 'student':
        student = Student.query.filter_by(email=email).first()
        if not student: return jsonify({"status": "error", "message": "User not found"})
        
        student.first_name = request.form.get('first_name', student.first_name)
        student.last_name = request.form.get('last_name', student.last_name)
        student.phone = request.form.get('phone', student.phone)
        student.gender = request.form.get('gender', student.gender)
        student.nationality = request.form.get('nationality', student.nationality)
        student.location = request.form.get('location', student.location)
        student.linkedin_link = request.form.get('linkedin_link', student.linkedin_link)
        student.github_link = request.form.get('github_link', student.github_link)
        student.portfolio_link = request.form.get('portfolio_link', student.portfolio_link)
        
        new_gpa = request.form.get('gpa')
        new_major = request.form.get('major', '').strip()
        
        # ⚠️ إصلاح مشكلة الرياضيات في الـ GPA (تجاهل الفروقات العشرية الطفيفة)
        if (new_gpa and abs(float(new_gpa) - student.gpa) > 0.01) or (new_major and new_major != student.major):
            if 'transcript_file' not in request.files or request.files['transcript_file'].filename == '':
                return jsonify({"status": "error", "message": "You MUST upload a new Official Transcript to change your GPA or Major."})
            
            transcript_file = request.files['transcript_file']
            try:
                pdf_reader = PyPDF2.PdfReader(transcript_file)
                pdf_text = "".join([page.extract_text() for page in pdf_reader.pages]).lower()
                if str(new_gpa) not in pdf_text and f"{float(new_gpa):.2f}" not in pdf_text:
                    return jsonify({"status": "error", "message": "Verification Failed: New GPA not found in transcript."})
                if new_major.lower() not in pdf_text:
                    return jsonify({"status": "error", "message": "Verification Failed: New Major not found in transcript."})
                
                transcript_file.seek(0)
                t_filename = secure_filename(transcript_file.filename)
                transcript_file.save(os.path.join(app.config['UPLOAD_FOLDER'], t_filename))
                student.transcript_file = t_filename
                student.gpa = float(new_gpa)
                student.major = new_major
            except:
                return jsonify({"status": "error", "message": "Could not read the PDF file."})

        if 'profile_pic' in request.files and request.files['profile_pic'].filename != '':
            file = request.files['profile_pic']
            pic_filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_filename))
            student.profile_pic = pic_filename
            
        if 'cv_file' in request.files and request.files['cv_file'].filename != '':
            file = request.files['cv_file']
            cv_filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], cv_filename))
            student.cv_file = cv_filename

        new_password = request.form.get('password')
        if new_password: student.password_hash = generate_password_hash(new_password, method='pbkdf2:sha256')

        db.session.commit()
        return jsonify({"status": "success", "message": "Profile updated successfully!", "user_data": student.to_dict()})
        
    elif role == 'employer':
        employer = Employer.query.filter_by(work_email=email).first()
        if not employer: return jsonify({"status": "error", "message": "User not found"})
        employer.company_name = request.form.get('company_name', employer.company_name)
        employer.recruiter_name = request.form.get('recruiter_name', employer.recruiter_name)
        employer.job_title = request.form.get('job_title', employer.job_title)
        employer.phone = request.form.get('phone', employer.phone)
        employer.website = request.form.get('website', employer.website)
        employer.linkedin_link = request.form.get('linkedin_link', employer.linkedin_link)
        
        new_password = request.form.get('password')
        if new_password: employer.password_hash = generate_password_hash(new_password, method='pbkdf2:sha256')
        db.session.commit()
        return jsonify({"status": "success", "message": "Profile updated successfully!", "user_data": employer.to_dict()})

# ==========================================
# محرك الذكاء الاصطناعي (CC2020)
# ==========================================
def compute_cc2020_score_fast(profile, target_job):
    job_requirements = CC2020_KNOWLEDGE_BASE.get(target_job, CC2020_KNOWLEDGE_BASE["Software Developer / Engineer"])
    req_tech = job_requirements["required_skills"]
    req_soft = job_requirements["required_dispositions"]
    best_fit_majors = job_requirements["best_fit_majors"]

    student_major = profile.get('major', '').lower()
    student_skills = [s.lower().strip() for s in profile.get('skills', [])]
    student_disps = [d.lower().strip() for d in profile.get('soft_skills', [])]
    student_gpa = float(profile.get('gpa', 0.0))
    student_gpa_scale = float(profile.get('gpa_scale', 4.0))

    major_score = 15 if any(m.lower() in student_major for m in best_fit_majors) else 5
    gpa_score = (student_gpa / student_gpa_scale) * 15 if student_gpa_scale > 0 else 0

    met_tech, missing_tech = [], []
    for req in req_tech:
        if any(req in s or s in req for s in student_skills): met_tech.append(req)
        else: missing_tech.append(req)
    tech_score = (len(met_tech) / len(req_tech)) * 45 if req_tech else 0

    met_soft, missing_soft = [], []
    for req in req_soft:
        if any(req in s or s in req for s in student_disps): met_soft.append(req)
        else: missing_soft.append(req)
    soft_score = (len(met_soft) / len(req_soft)) * 25 if req_soft else 0

    final_score = min(int(major_score + gpa_score + tech_score + soft_score), 100)
    matched_skills = [s.title() for s in met_tech] + [s.title() + " (Disposition)" for s in met_soft]
    missing_skills = [s.title() for s in missing_tech] + [s.title() + " (Disposition)" for s in missing_soft]

    return final_score, matched_skills, missing_skills

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    data = request.json
    site_lang = data.get('lang', 'en') 
    target_job = data.get('job_title', 'Software Developer / Engineer')
    student_gpa = float(data.get('gpa', 0.0))
    student_gpa_scale = 4.0
    student_major = data.get('major', 'Unknown Major')
    student_tech_skills = data.get('skills', [])
    student_soft_skills = data.get('soft_skills', [])
    
    student_record = None
    if 'email' in data:
        student_record = Student.query.filter_by(email=data['email']).first()
        if student_record:
            if isinstance(student_tech_skills, list): student_record.skills = ",".join(student_tech_skills)
            if isinstance(student_soft_skills, list): student_record.soft_skills = ",".join(student_soft_skills)
            db.session.commit()
            student_gpa = float(student_record.gpa)
            student_gpa_scale = float(student_record.gpa_scale)

    job_reqs = CC2020_KNOWLEDGE_BASE.get(target_job, CC2020_KNOWLEDGE_BASE["Software Developer / Engineer"])
    req_tech = job_reqs["required_skills"]
    req_soft = job_reqs["required_dispositions"]
    best_fit_majors = job_reqs["best_fit_majors"]
    ai_language = 'Arabic' if site_lang == 'ar' else 'English'
    
    prompt = f"""
    You are an intelligent ACM/IEEE CC2020 semantic evaluator.
    [Target Job]: "{target_job}"
    [CC2020 Required Tech Skills]: {req_tech}
    [CC2020 Required Soft Skills]: {req_soft}
    [Student Profile]
    - Tech Skills: {student_tech_skills}
    - Soft Skills: {student_soft_skills}
    [Task 1] Compare skills semantically. Identify MET and MISSING skills. DO NOT calculate scores.
    [Task 2] Write a 1-sentence encouraging message, then a 3-step practical roadmap to learn ONLY missing skills. 
    Use HTML: <a href="https://www.coursera.org">Link</a>. NO markdown [text](url).
    CRITICAL: Generate the EXACT SAME roadmap in BOTH English and Arabic.
    [Output]
    {{
      "met_tech_requirements": ["list"], "missing_tech_requirements": ["list"],
      "met_soft_requirements": ["list"], "missing_soft_requirements": ["list"],
      "roadmap_html_en": "<HTML string>", "roadmap_html_ar": "<HTML string>"
    }}
    """

    try:
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash', contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.1, seed=42)
        )
        result_data = json.loads(response.text)
        ai_met_tech = result_data.get('met_tech_requirements', [])
        ai_missing_tech = result_data.get('missing_tech_requirements', [])
        ai_met_soft = result_data.get('met_soft_requirements', [])
        ai_missing_soft = result_data.get('missing_soft_requirements', [])
        ai_roadmap_html_en = result_data.get('roadmap_html_en', '')
        ai_roadmap_html_ar = result_data.get('roadmap_html_ar', '')

        major_score = 15 if any(m.lower() in student_major.lower() for m in best_fit_majors) else 5
        gpa_score = (student_gpa / student_gpa_scale) * 15 if student_gpa_scale > 0 else 0
        tech_score = min((len(ai_met_tech) / len(req_tech)) * 45, 45) if req_tech else 0
        soft_score = min((len(ai_met_soft) / len(req_soft)) * 25, 25) if req_soft else 0
        final_score = min(int(major_score + gpa_score + tech_score + soft_score), 100)
        
        matched_skills = [s.title() for s in ai_met_tech] + [s.title() + " (Disposition)" for s in ai_met_soft]
        missing_skills = [s.title() for s in ai_missing_tech] + [s.title() + " (Disposition)" for s in ai_missing_soft]

        def clean_html(html_str):
            html_str = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2" target="_blank">\1</a>', html_str)
            def clean_url(match):
                url = match.group(1).replace('[', '').replace(']', '').replace('(', '').replace(')', '').strip()
                if url.startswith('www.'): url = "https://" + url
                elif not url.startswith('http'): url = "https://" + "www.coursera.org"
                return f'href="{url}" target="_blank" style="color:#9013FE; font-weight:bold; text-decoration:underline;"'
            return re.sub(r'href=["\'](.*?)["\']', clean_url, html_str)

        ai_roadmap_html_en = clean_html(ai_roadmap_html_en)
        ai_roadmap_html_ar = clean_html(ai_roadmap_html_ar)
    except Exception as e:
        print("AI Evaluation Error:", e)
        final_score, matched_skills, missing_skills = compute_cc2020_score_fast(data, target_job)
        ai_roadmap_html_ar = "<p style='color:red;'>⚠️ تعذر الاتصال بالمحرك الدلالي.</p>"
        ai_roadmap_html_en = "<p style='color:red;'>⚠️ Unable to connect to Semantic Engine.</p>"

    recommendations = []
    for missing in missing_skills:
        clean_missing = missing.replace(' ', '%20')
        recommendations.append({
            "skill": missing, "title": f"Master '{missing}' (Certificate)",
            "provider": "Coursera / edX (Certified)", "link": "https://" + "www.coursera.org/search?query=" + clean_missing
        })

    if student_record:
        student_record.target_job = target_job
        student_record.last_score = final_score
        student_record.last_status = "Market Ready" if final_score >= 75 else "Needs Development"
        db.session.commit()

    return jsonify({
        "readiness_score": final_score,
        "status": "Market Ready" if final_score >= 75 else "Needs Development",
        "matched_skills": matched_skills, 
        "missing_skills": missing_skills,
        "recommended_courses": recommendations,
        "ai_roadmap_en": ai_roadmap_html_en,
        "ai_roadmap_ar": ai_roadmap_html_ar
    })

# ==========================================
# مسارات جلب وبحث الطلاب (للشركات)
# ==========================================
@app.route('/api/students/all', methods=['GET'])
def api_students_all():
    all_students = Student.query.all()
    result = []
    for s in all_students:
        if not s.major: continue
        tech_list = [skill.strip() for skill in s.skills.split(',') if skill.strip()] if s.skills else []
        soft_list = [skill.strip() for skill in s.soft_skills.split(',') if skill.strip()] if s.soft_skills else []
        result.append({
            "name": f"{s.first_name} {s.last_name}",
            "gender": s.gender, "nationality": s.nationality, "location": s.location,
            "major": s.major, "gpa_display": f"{s.gpa} / {s.gpa_scale}",
            "tech_skills": tech_list, "soft_skills": soft_list,
            "cv_link": f"/static/uploads/{s.cv_file}" if s.cv_file else "#",
            "profile_pic": f"/static/uploads/{s.profile_pic}" if s.profile_pic else "/static/uploads/default.jpg",
            "linkedin_link": s.linkedin_link if s.linkedin_link else "",
            "github_link": s.github_link if s.github_link else "",
            "portfolio_link": s.portfolio_link if s.portfolio_link else "",
            "email": s.email 
        })
    return jsonify(result)

@app.route('/api/search', methods=['POST'])
def api_search():
    data = request.json
    target_job = data.get('job_role')
    all_students = Student.query.all()
    matched = []
    for s in all_students:
        if not s.major: continue
        profile = s.to_dict()
        final_score, matched_skills, _ = compute_cc2020_score_fast(profile, target_job)
        if final_score > 50:
            tech_list = [skill.strip() for skill in profile.get('skills', []) if skill.strip()]
            soft_list = [skill.strip() for skill in profile.get('soft_skills', []) if skill.strip()]
            matched.append({
                "name": profile['name'], 
                "gender": profile.get('gender'), "nationality": profile.get('nationality'), "location": profile.get('location'),
                "major": profile['major'], "score": final_score,
                "gpa_display": f"{profile['gpa']} / {profile['gpa_scale']}",
                "tech_skills": tech_list, "soft_skills": soft_list,
                "cv_link": f"/static/uploads/{s.cv_file}" if s.cv_file else "#",
                "profile_pic": f"/static/uploads/{s.profile_pic}" if s.profile_pic else "/static/uploads/default.jpg",
                "linkedin_link": profile.get('linkedin_link', ''),
                "github_link": profile.get('github_link', ''),
                "portfolio_link": profile.get('portfolio_link', ''),
                "email": profile['email']
            })
    matched.sort(key=lambda x: x['score'], reverse=True)
    return jsonify(matched)

@app.route('/api/contact_student', methods=['POST'])
def api_contact_student():
    data = request.json
    employer_email = data.get('employer_email')
    student_email = data.get('student_email')
    job_role = data.get('job_role', 'General Opportunity')

    employer = Employer.query.filter_by(work_email=employer_email).first()
    student = Student.query.filter_by(email=student_email).first()
    if not employer or not student: return jsonify({"status": "error", "message": "User not found!"})

    subject = f"Job Opportunity at {employer.company_name} - via Darbak.AI"
    body = f"""
Hello {student.first_name},

Great news! {employer.recruiter_name} from {employer.company_name} is interested in your profile for the '{job_role}' position based on your skills on Darbak.AI.
Please reach out to them directly to discuss the opportunity:
Email: {employer.work_email}
Phone: {employer.phone}

Best of luck,
Darbak.AI Team
"""
    try:
        if SENDER_EMAIL == "your_email@gmail.com":
            return jsonify({"status": "success", "message": f"(Simulated) Email sent successfully to {student.first_name}!"})
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = student.email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        return jsonify({"status": "success", "message": f"Email officially sent to {student.first_name}!"})
    except Exception as e:
        print("Email Error:", e)
        return jsonify({"status": "error", "message": "Could not send email. Please check server configuration."})

# ==========================================
# مسارات لوحة تحكم المدير (Admin API)
# ==========================================
@app.route('/api/admin/stats', methods=['GET'])
def api_admin_stats():
    student_count = Student.query.count()
    employer_count = Employer.query.count()
    evaluation_count = Student.query.filter(Student.last_score != None).count()
    
    return jsonify({
        "students": student_count,
        "employers": employer_count,
        "evaluations": evaluation_count
    })

@app.route('/api/admin/users', methods=['GET'])
def api_admin_get_users():
    students = [s.to_dict() for s in Student.query.all()]
    employers = [e.to_dict() for e in Employer.query.all()]
    return jsonify({"students": students, "employers": employers})

@app.route('/api/admin/delete_user', methods=['POST'])
def api_admin_delete_user():
    data = request.json
    user_id = data.get('id')
    role = data.get('role')
    
    try:
        if role == 'student':
            user = Student.query.get(user_id)
        else:
            user = Employer.query.get(user_id)
            
        if user:
            db.session.delete(user)
            db.session.commit()
            return jsonify({"status": "success", "message": "User deleted successfully"})
        return jsonify({"status": "error", "message": "User not found"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# ==========================================
# تشغيل السيرفر للشبكة المحلية (البث المباشر)
# ==========================================
if __name__ == '__main__':
    # وضع '0.0.0.0' يسمح بفتح الموقع من جوالك عن طريق إدخال رقم الـ IP الخاص بجهازك متبوعاً بـ :5000
    app.run(host='0.0.0.0', port=5000, debug=True)