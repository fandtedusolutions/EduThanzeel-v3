# EduThanzeel Backend

This is the Django backend for the EduThanzeel website. It handles admission applications and contact inquiries.

## Features
- **Admin Dashboard**: Access via `/admin` to view and manage all form submissions.
- **REST API**:
  - `POST /api/admission/`: For student applications.
  - `POST /api/contact/`: For general inquiries.
- **CORS Support**: Configured to allow requests from the frontend.

## Setup Instructions

1. **Python Installation**: Ensure Python 3.10+ is installed.
2. **Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Run Migrations**:
   ```bash
   python manage.py migrate
   ```
5. **Start Server**:
   ```bash
   python manage.py runserver
   ```

## Admin Access
- **URL**: `http://127.0.0.1:8000/admin`
- **Username**: `admin`
- **Password**: `admin123` (Change this in production!)

## Connecting Frontend
Update your frontend JavaScript to call the following endpoints:
- Admissions: `http://127.0.0.1:8000/api/admission/`
- Contact: `http://127.0.0.1:8000/api/contact/`

Example:
```javascript
fetch('http://127.0.0.1:8000/api/admission/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(formData)
});
```
"# Edu-thanzeel-v1" 
