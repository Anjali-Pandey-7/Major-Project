import base64
import streamlit as st
import os
import io
from PIL import Image
import pdf2image
import google.generativeai as genai
from dotenv import load_dotenv
from jobs_data import jobs  # Import jobs from separate file

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to interact with Google Gemini AI model for generating text responses
def get_gemini_response(input, pdf_content, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input, pdf_content[0], prompt])
    return response.text

def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        images = pdf2image.convert_from_bytes(uploaded_file.read())
        first_page = images[0]
        img_byte_arr = io.BytesIO()
        first_page.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()
        pdf_parts = [{
            "mime_type": "image/jpeg",
            "data": base64.b64encode(img_byte_arr).decode()
        }]
        return pdf_parts
    else:
        raise FileNotFoundError("No file uploaded")

def recommend_jobs(resume_skills, jobs_list):
    resume_skills_set = set(skill.strip().lower() for skill in resume_skills.split(','))
    recommended = []
    for job in jobs_list:
        job_skills = set(s.lower() for s in job["skills_required"])
        if resume_skills_set.intersection(job_skills):
            recommended.append(job)
    return recommended

st.set_page_config(page_title="ATS Resume Scanner with Job Recommendations")
st.header("ATS Tracking System")

input_text = st.text_area("Job Description: ", key="input")
uploaded_file = st.file_uploader("Upload your resume (PDF)...", type=["pdf"])

submit1 = st.button("Tell Me About the Resume")
submit3 = st.button("Percentage match")
submit_rec = st.button("Get Job Recommendations")
# Prompt given to AI for detailed resume review
input_prompt1 = """
 You are an experienced Technical Human Resource Manager,your task is to review the provided resume against the job description. 
 Please share your professional evaluation on whether the candidate's profile aligns with the role. 
 Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
"""

input_prompt3 = """
You are an skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality, 
your task is to evaluate the resume against the provided job description. give me the percentage of match if the resume matches
the job description. First the output should come as percentage and then keywords missing and last final thoughts.
"""

input_prompt_skills = """
Extract the list of technical skills and keywords from this resume content. Provide the skills as a simple comma-separated list.
"""

if uploaded_file is not None:
    st.write("PDF Uploaded Successfully")

if submit1:
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_prompt1, pdf_content, input_text)
        st.subheader("The Response is")
        st.write(response)
    else:
        st.write("Please upload the resume")

elif submit3:
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_prompt3, pdf_content, input_text)
        st.subheader("The Response is")
        st.write(response)
    else:
        st.write("Please upload the resume")

elif submit_rec:
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        
        # Step 1: Extract skills from resume using Gemini
        skills_response = get_gemini_response(input_prompt_skills, pdf_content, "")
        st.subheader("Extracted Skills:")
        st.write(skills_response)

        # Step 2: Recommend jobs based on extracted skills
        recommended = recommend_jobs(skills_response, jobs)
        
        if recommended:
            st.subheader("Job Recommendations Based on Your Resume:")
            for job in recommended:
                st.markdown(f"""
                **{job['title']}** at *{job['company']}*  
                Location: {job['location']}  
                Start Date: {job['start_date']}  
                Type: {job['type']}
                """)
        else:
            st.write("No matching jobs found based on your skills.")
    else:
        st.write("Please upload the resume")
