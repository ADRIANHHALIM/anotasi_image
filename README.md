# Anotasi Image

## Project Overview

Anotasi Image is a Django-based web application for image annotation. It allows users to:
- Upload datasets of images
- Create annotation jobs with different segmentation types (semantic, instance, panoptic)
- Annotate images using different shape types (bounding box, polygon)
- Review annotations

## How to Run the Project

### 1. Set Up the Environment

```bash
# Activate the virtual environment
# On Windows:
anotasienv\Scripts\activate
# On macOS/Linux:
source anotasienv/bin/activate

# If the virtual environment doesn't exist, create it:
python -m venv anotasienv
source anotasienv/bin/activate  # or anotasienv\Scripts\activate on Windows
```

### 2. Install Dependencies

```bash
pip install django django-crispy-forms crispy-bootstrap4 django-allauth python-dotenv Pillow
```

### 3. Configure Environment Variables

Create a `.env` file in the project root with the following variables:
```
SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
EMAIL_HOST_USER=your_email
EMAIL_HOST_PASSWORD=your_email_password
```

### 4. Set Up the Database

```bash
# Navigate to the project directory
cd Anotasi_Image

# Run migrations
python manage.py migrate

# Create a superuser (optional)
python manage.py createsuperuser
```

### 5. Run the Development Server

```bash
# Make sure you're in the Anotasi_Image directory
cd Anotasi_Image  # if not already there

# Start the server
python manage.py runserver
```

The application will be available at http://127.0.0.1:8000/

## Project Structure

- `Anotasi_Image/`: Main project directory
  - `Anotasi_Image/`: Project settings and URL configuration
  - `master/`: Core app with user management and job/dataset models
  - `annotator/`: App for image annotation features
  - `reviewer/`: App for reviewing annotations
  - `media/`: User-uploaded files (datasets, job images)
  - `static/`: Static files (CSS, JS, images)
  - `templates/`: Project-wide templates

## Testing

```bash
# Run all tests
python manage.py test

# Run tests for a specific app
python manage.py test master
python manage.py test annotator
python manage.py test reviewer
```

For more detailed information, please refer to the `guidelines.md` file.
