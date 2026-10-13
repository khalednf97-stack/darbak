import difflib

# --- 1. تعريف قاعدة بيانات السوق (Market Database) ---
market_db = {
    "Python Developer": {
        "skills": {
            "Python": 30,
            "Django": 20,
            "SQL": 15,
            "Git": 10,
            "REST API": 15,
            "Communication": 10
        }
    },
    "Data Analyst": {
        "skills": {
            "Excel": 20,
            "Python": 20,
            "SQL": 30,
            "Tableau": 15,
            "Statistics": 15
        }
    }
}

# --- 2. محرك الجاهزية (Readiness Engine Class) ---
class ReadinessEngine:
    def __init__(self, market_criteria):
        self.market_criteria = market_criteria

    def _fuzzy_match(self, student_skill, required_skills, threshold=0.6):
        """
        Check if a skill matches using inclusion or fuzzy logic.
        """
        student_skill_lower = student_skill.lower()
        for req_skill in required_skills:
            req_skill_lower = req_skill.lower()
            
            # 1. Direct Inclusion (e.g., "Python" in "Python Programming")
            if req_skill_lower in student_skill_lower or student_skill_lower in req_skill_lower:
                return req_skill
            
            # 2. Fuzzy Match (for typos)
            similarity = difflib.SequenceMatcher(None, student_skill_lower, req_skill_lower).ratio()
            if similarity >= threshold:
                return req_skill
        return None

    def analyze_profile(self, student_profile, target_role):
        """
        Analyze the student profile against the target role requirements.
        """
        if target_role not in self.market_criteria:
            return None

        requirements = self.market_criteria[target_role]
        required_skills = requirements['skills']
        
        total_weight = sum(required_skills.values())
        if total_weight == 0:
            return None

        earned_score = 0
        missing_skills = []
        matched_skills = []
        
        # 1. Skill Analysis
        for skill, weight in required_skills.items():
            found = False
            for student_skill in student_profile['skills']:
                if self._fuzzy_match(student_skill, [skill]):
                    earned_score += weight
                    matched_skills.append(skill)
                    found = True
                    break
            if not found:
                missing_skills.append(skill)

        # 2. GPA Logic (Normalized)
        gpa = student_profile.get('gpa', 0)
        scale = student_profile.get('gpa_scale', 4.0) # Default to 4.0 if not provided
        
        gpa_bonus = 0
        
        if scale > 0:
            # Calculate GPA Percentage (e.g., 3.5 / 4.0 = 0.875)
            gpa_percentage = gpa / scale
            
            # Logic: If GPA is roughly equivalent to "Very Good" (approx 87.5%) or higher, give bonus.
            if gpa_percentage >= 0.87:
                gpa_bonus = 5
        
        # Calculate Final Score
        raw_score = (earned_score / total_weight * 100) + gpa_bonus
        final_score = min(100, raw_score)
        
        return {
            "readiness_score": round(final_score, 2),
            "status": "Job Ready" if final_score >= 80 else "Needs Improvement",
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "roadmap": self._generate_roadmap(missing_skills)
        }

    def _generate_roadmap(self, missing_skills):
        roadmap = []
        for skill in missing_skills:
            recommendation = {
                "skill": skill,
                "action": f"Take an intensive course in {skill}",
                "provider": "Udacity / Coursera"
            }
            roadmap.append(recommendation)
        return roadmap