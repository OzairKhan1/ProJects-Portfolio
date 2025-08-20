import streamlit as st
import pandas as pd
import smtplib
import random
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
import re
from io import BytesIO

st.set_page_config(page_title="📧 SmartSend", layout="wide", page_icon="📨")

# --- Custom Styling ---
st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(120deg, #e0f7fa, #e1bee7);
            color: #333;
        }
        .center-title {
            text-align: center;
        }
        .stTextInput > label,
        .stTextArea > label,
        .stSelectbox > label,
        .stFileUploader > label,
        .stMultiselect > label,
        .stRadio > label {
            font-weight: 700;
            color: #000;
        }
        .stRadio > div {
            gap: 1.5rem !important;
        }
        thead tr th {
            font-weight: bold !important;
        }
        /* Keep the (Help) link visually next to the label without changing label width */
        .app-pass-row { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
        .app-pass-row a { font-size: 0.95rem; text-decoration: none; color: #0a66c2; }
    </style>
""", unsafe_allow_html=True)

# --- Title ---
st.markdown("""<h1 class='center-title'>📧 SmartSend</h1>""", unsafe_allow_html=True)
st.markdown("""<h5 class='center-title'>Developer: Ozair Khan</h5>""", unsafe_allow_html=True)

# --- Mode Selection ---
st.markdown("<h5 style='font-weight:bold;'>Choose Email Mode:</h5>", unsafe_allow_html=True)
mode = st.radio(
    "Choose Email Mode",  # real label for accessibility
    ["For Students", "Customized Email"],
    label_visibility="collapsed"  # hides the label visually
)

cv_file, excel_file, df = None, None, None
email_subject = ""
email_body = ""
col_names = []

# --- File Upload ----
LOG_DIR = os.path.join(os.getcwd(), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

if mode == "For Students":
    excel_file = st.file_uploader("Upload Excel file", type=['xlsx', 'xls'])
    cv_file = st.file_uploader("Upload your CV (PDF)", type=['pdf'])
    done_file = os.path.join(LOG_DIR, "sent_emails_log.csv")

    if excel_file:
        df = pd.read_excel(excel_file)
        df = df.fillna("")
        st.subheader("📄 Uploaded Excel Preview")
        st.dataframe(df)
        col_names = df.columns.tolist()

if mode == "Customized Email":
    done_file = os.path.join(LOG_DIR, "sent_custom_log.csv")
    excel_file = st.file_uploader("Upload Excel file", type=['xlsx', 'xls'])
    # === ALLOWED CHANGE: allow single/multiple attachments for Customized Email ===
    attachment_files = st.file_uploader("Upload Attachment(s)", type=None, accept_multiple_files=True)
    if excel_file:
        df = pd.read_excel(excel_file)
        df = df.fillna("")
        st.subheader("📄 Uploaded Excel Preview")
        st.dataframe(df)
        col_names = df.columns.tolist()

# --- Email Subject & Body ---
email_subject = st.text_input("Email Subject", value="Please Put The Subject. It's Compulsory.")

# Rich text editor for email body
try:
    from streamlit_quill import st_quill
    use_quill = True
except:
    use_quill = False

email_placeholder = """Email Body Instructions
You may compose a fully customized email body here.
If you wish to include dynamic details from an Excel file, use the following format:

Prefix the field with @

Enclose the field name in parentheses

Example:
@(Email), @(Name of Someone), @(Profession of Someone)

When the email is sent, these placeholders will be automatically replaced with the corresponding data from your Excel file.
 """

if use_quill:
    email_body = st_quill(value=email_placeholder, html=False)
else:
    email_body = st.text_area("Email Body", value=email_placeholder, height=300)

# --- Column Placeholder Picker ---
if df is not None and col_names:
    st.markdown("### 📌 Insert Column Placeholder")
    selected_col = st.selectbox("Pick a column to insert", col_names)
    if st.button("Insert @(ColumnName)"):
        st.warning(f"👉 Manually insert `@({selected_col})` into the editor above.")

    # Normalize column names for matching
    normalized_col_names = {re.sub(r'\s+', ' ', col).strip().lower(): col for col in col_names}
    escaped_cols = [re.escape(col) for col in col_names]
    valid_pattern = r'@\((?:' + '|'.join(escaped_cols) + r')\)'

    # Extract used placeholders
    used_cols = set()
    for match in re.finditer(valid_pattern, email_body):
        candidate = match.group(0)[2:-1].strip()
        used_cols.add(candidate)

    # Check for unknown placeholders
    unknown_cols = []
    for match in re.finditer(r'@\(([\w\s&\-().]+)\)', email_body):
        candidate = match.group(1).strip()
        if candidate not in col_names:
            unknown_cols.append(candidate)

    if unknown_cols:
        st.warning(f"⚠️ Unknown column(s) referenced: {', '.join(unknown_cols)}")

    with st.expander("📋 Available Column Names"):
        st.markdown("Click to copy any column name:")
        for col in col_names:
            st.code(f"@({col})", language='text')

# --- Sender Credentials ---
# Sender Email
sender_email = st.text_input("Sender Email")

# Password Section 
# ***********************************************************

# Custom label with clickable Help
st.markdown("""
<div style="display: flex; align-items: center; font-weight: 600; font-size: 14px; margin-bottom: -8px;">
    App Password
    <a href="#app-password-help-section" style="margin-left: 6px; font-weight: 400; text-decoration: none;">
        (Help)
    </a>
</div>
""", unsafe_allow_html=True)

# Real Streamlit password box — label hidden so no gap
password = st.text_input(
    "App Password (hidden)",  # Keep a real label here
    type="password",
    key="app_password_input",
    label_visibility="collapsed"  
)

#******************************************************************
# --- Send Emails ---
send_button = st.button("📨 Send Emails")

if send_button:
    if not all([sender_email, password, email_subject, email_body]):
        st.error("Please complete all fields.")
    elif mode == "For Students" and (df is None or cv_file is None):
        st.error("Please upload Excel file and CV.")
    else:
        sent_emails = []
        if os.path.exists(done_file):
            sent_df = pd.read_csv(done_file)
            sent_emails = sent_df['Email'].tolist()

        if cv_file:
            with open("temp_cv.pdf", "wb") as f:
                f.write(cv_file.read())

        success, failed = 0, 0
        log_data = []

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as server:
                server.login(sender_email, password)

                rows_to_process = df.to_dict(orient='records') if df is not None else [{}]

                for row_data in rows_to_process:
                    email = row_data.get("Email", "")
                    if email in sent_emails or not email:
                        continue

                    msg = email_body
                    for match in re.finditer(valid_pattern, email_body):
                        placeholder = match.group(0)
                        key = match.group(0)[2:-1].strip()
                        msg = msg.replace(placeholder, str(row_data.get(key, "")))

                    subj = email_subject
                    for match in re.finditer(valid_pattern, email_subject):
                        placeholder = match.group(0)
                        key = match.group(0)[2:-1].strip()
                        subj = subj.replace(placeholder, str(row_data.get(key, "")))
                    
                    message = MIMEMultipart()
                    message['From'] = sender_email
                    message['To'] = email
                    message['Subject'] = subj
                    message.attach(MIMEText(msg, 'plain'))

                    if mode == "For Students" and cv_file:
                        with open("temp_cv.pdf", 'rb') as pdf:
                            payload = MIMEBase('application', 'octet-stream')
                            payload.set_payload(pdf.read())
                            encoders.encode_base64(payload)
                            payload.add_header('Content-Disposition', f'attachment; filename="{cv_file.name}"')
                            message.attach(payload)

                    # === ALLOWED CHANGE: attach uploaded files in Customized Email mode ===
                    if mode == "Customized Email" and attachment_files:
                        for file in attachment_files:
                            payload = MIMEBase('application', 'octet-stream')
                            payload.set_payload(file.read())
                            encoders.encode_base64(payload)
                            payload.add_header('Content-Disposition', f'attachment; filename="{file.name}"')
                            message.attach(payload)

                    try:
                        server.sendmail(sender_email, email, message.as_string())
                        log_data.append({"Email": email})
                        success += 1
                        st.success(f"✅ Email sent to {email}")
                        time.sleep(random.randint(1, 2))
                    except Exception as e:
                        st.error(f"❌ Failed to send to {email}: {str(e)}")
                        failed += 1

        except Exception as e:
            st.error(f"❌ Failed to connect or send emails: {str(e)}")


        # Save log only if emails were sent
        if log_data:
            df_log = pd.DataFrame(log_data)
            if os.path.exists(done_file):
                old_df = pd.read_csv(done_file)
                df_log = pd.concat([old_df, df_log], ignore_index=True)
            df_log.to_csv(done_file, index=False)

        st.info(f"📊 Emails Sent: {success} | Failed: {failed}")

        # Check if log file exists before download
        if os.path.exists(done_file):
            with open(done_file, 'rb') as f:
                st.download_button("📅 Download Sent Log", data=f, file_name=os.path.basename(done_file))
        else:
            st.warning("📂 No log file available. Emails may not have been sent.")

# --- Helpers ---
st.markdown("""
### 💡 Email Writing Helpers
- [ChatGPT](https://chat.openai.com/) – for drafting personalized messages  
- [Grammarly](https://www.grammarly.com/) – for grammar and clarity  
- [QuillBot](https://quillbot.com/) – for paraphrasing and polishing text  
""")

# --- App Password Help Section ---
st.markdown("""
---
## 🔑 App Password Help Section
<a name="app-password-help-section"></a>
**What is an App Password?**  
An App Password is a unique 16-digit code generated by your email provider that allows secure access for third-party apps (like this email sender) without using your main email password.

**How is it different from your normal email password?**  
- **Normal Password**: Used to log in directly to your email account.  
- **App Password**: Special password for apps, more secure, can be revoked anytime.

**How to create an App Password?**
1. **Gmail** – Enable 2-Step Verification, then create an App Password:  
   [Generate Gmail App Password](https://myaccount.google.com/apppasswords)  
2. **Outlook / Hotmail / Live** – Enable 2-Step Verification, then create an App Password:  
   [Generate Outlook App Password](https://account.live.com/proofs/AppPassword)  
3. **Yahoo Mail** – Enable 2-Step Verification, then create an App Password:  
   [Generate Yahoo App Password](https://login.yahoo.com/account/security)
---
""", unsafe_allow_html=True)

