# 5-10 Minute LMS Project Demo Video Script

**Project Name:** AI-Enhanced Admission Management System  
**Presenter:** Student / Applicant  
**Target Duration:** 6 to 8 minutes  

---

## ⏱️ Video Presentation Timeline

```
[00:00 - 01:15]  1. Introduction & Problem Statement
[01:15 - 03:00]  2. Student Portal: Application Submission & Instant ML Pre-Check
[03:00 - 04:30]  3. Application Status Tracking & Stepper
[04:30 - 06:15]  4. Admission Officer Console & Generative AI Evaluation Dossier
[06:15 - 07:15]  5. Executive Analytics Dashboard & CSV Export
[07:15 - 08:30]  6. Code Walkthrough: Backend, Logistic Regression & GenAI Integration
[08:30 - 09:00]  7. Conclusion & Wrap Up
```

---

## 🎬 Section-by-Section Walkthrough & Speaking Script

### 1. Introduction (00:00 - 01:15)
- **On Screen:** Start with browser showing the **Apex Institute Admissions Landing Page** (`http://127.0.0.1:5000`).
- **What to Say:**
  > *"Hello everyone and esteemed faculty members. Today I am presenting my project: the **AI-Enhanced Admission Management System**.*  
  > *In educational institutions, processing thousands of student applications manually is time-consuming, subjective, and prone to human error. To solve this, I have built a full-stack educational admission management application that combines **Full-Stack Application Tracking**, a **Machine Learning Module using Logistic Regression** to predict admission eligibility with transparent probability scores, and a **Generative AI Module** that generates comprehensive student evaluation summaries and admission recommendations.*  
  > *Let's take a look at the system in action."*

---

### 2. Student Portal: Application Submission & Live ML Pre-Check (01:15 - 03:00)
- **On Screen:** Click on **"Apply for Admission"** or go to `http://127.0.0.1:5000/login`.
- **Action:** Click the **"Fill Student (Applicant)"** demo pill, then click **"Sign In to Portal"**. You will arrive at `http://127.0.0.1:5000/student`.
- **Action:** Switch to the **"Submit New Application"** tab.
- **What to Say:**
  > *"Here is the Student Self-Service Portal. Prospective students can submit their personal details, select their desired degree program—such as B.Tech Computer Science or Artificial Intelligence—and input their academic GPA, entrance examination score, attendance percentage, and previous board marks.*  
  > *A unique feature is the **Instant ML Pre-Check**. Before formally submitting, the student can test their academic scores against our trained **Logistic Regression** model.*  
  > *Notice that when I click 'Run ML Pre-Check', the system instantly returns whether the profile is Eligible and calculates the success probability—for example, 92.4%—allowing transparent guidance."*
- **Action:** Select a course, attach a file in the upload zone, and click **"Submit Final Application"**.

---

### 3. Application Status Tracking & AI Dossier (03:00 - 04:30)
- **On Screen:** The system automatically switches to the **"Track My Application"** tab.
- **What to Say:**
  > *"Once submitted, the student can monitor their application progress in real-time through this 4-step progress stepper: from 'Submitted', to 'Under Review', 'ML & AI Evaluated', up to 'Final Decision'.*  
  > *Down here, the student can view their **Machine Learning Eligibility Score** with a calibrated probability meter, the status of their uploaded academic dossier, and the **AI-Generated Admission Evaluation & Insights** highlighting their academic strengths and suitability."*

---

### 4. Admission Officer Console & Generative AI Evaluation (04:30 - 06:15)
- **On Screen:** Click **Logout**, then sign in as **Admin** using the **"Fill Admin (Officer)"** demo pill (`admin@institution.edu`).
- **Action:** Navigate to `http://127.0.0.1:5000/admin`.
- **What to Say:**
  > *"Now, let's step into the role of the University Admission Officer.*  
  > *In the Officer Dashboard, we have real-time KPI counters tracking total applications, pending reviews, approvals, and the cohort ML eligibility rate.*  
  > *The master table allows officers to filter by degree course or status, and search by applicant name.*  
  > *Let's open the review dossier for candidate Priya Sharma by clicking **'Review & AI Dossier'**.*  
  > *Here, the modal displays the candidate's complete academic metrics, uploaded marksheet, and our Scikit-Learn Logistic Regression prediction—showing an eligibility probability of 100%.*  
  > *Below it is our **Generative AI Module**. It automatically synthesizes an **Executive Summary**, a clear **Admission Recommendation**, **Profile Insights** analyzing strengths and risks, and a statutory **Approval Justification** based on university quota rules.*  
  > *The officer can also enter custom directives—like 'Evaluate for department sports scholarship'—and click **'Regenerate AI Evaluation'** to update the report dynamically.*  
  > *Finally, the committee can confirm the admission decision by entering official remarks and clicking **'Approve Admission'**."*

---

### 5. Analytics & Reports Dashboard (06:15 - 07:15)
- **On Screen:** Click on **"Analytics & Reports"** in the top navbar (`http://127.0.0.1:5000/analytics`).
- **What to Say:**
  > *"For university leadership and accreditation bodies, the system includes an **Analytics & Intelligence Dashboard**.*  
  > *It visualizes applications by academic program using interactive Chart.js bar charts, admission status distribution via doughnut charts, quota category representation, and extracurricular distinctions.*  
  > *Admission officers can also click **'Download CSV Report'** to instantly export the entire dataset for institutional records and audits."*

---

### 6. Code Walkthrough: Architecture & ML Model (07:15 - 08:30)
- **On Screen:** Switch to VS Code / Antigravity IDE and briefly show the folder structure: `ML/`, `Backend/`, `Frontend/`.
- **What to Say:**
  > *"Let's briefly review the project architecture:*  
  > *1. **ML Module (`ML/`):** The model is trained using **Logistic Regression** in `ML/train_model.py` and documented in `ML/admission_model.ipynb`. Continuous features like GPA and entrance scores are scaled using `StandardScaler`, and categoricals like quota are encoded using `OneHotEncoder`. On the held-out test set, the model achieves **94.8% accuracy** and **0.9472 ROC-AUC**.*  
  > *2. **Backend (`Backend/`):** Built with Flask and organized into modular Blueprints for authentication, applications, ML inference, and GenAI synthesis. We use PyJWT for secure role-based authentication and SQLite with foreign key integrity.*  
  > *3. **Generative AI Service (`Backend/services/genai_service.py`):** Supports live LLM APIs like Google Gemini and OpenAI, paired with an intelligent offline synthesis engine so it runs reliably in any evaluation environment.*  
  > *4. **Frontend (`Frontend/`):** Crafted with responsive Vanilla CSS and modern design principles for speed and visual excellence."*

---

### 7. Conclusion & Wrap Up (08:30 - 09:00)
- **On Screen:** Switch back to the web portal landing page (`http://127.0.0.1:5000`).
- **What to Say:**
  > *"To summarize, this project provides a complete, production-ready, AI-enhanced educational admission management system that streamlines application handling, delivers transparent ML eligibility scoring, and automates AI evaluation reporting.*  
  > *The entire system runs locally with a single command: `python run.py`.*  
  > *Thank you very much!"*
