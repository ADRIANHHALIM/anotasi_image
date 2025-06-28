# Anotasi Image Project Guidelines

This document provides essential information for developers working on the Anotasi Image project.

## Project Overview

Anotasi Image is a Django-based web application for image annotation. It allows users to:
- Upload datasets of images
- Create annotation jobs with different segmentation types (semantic, instance, panoptic)
- Annotate images using different shape types (bounding box, polygon)
- Review annotations

The project has three main apps:
- `master`: Core functionality, user management, and dataset/job management
- `annotator`: Features for annotating images
- `reviewer`: Features for reviewing annotations

## Build/Configuration Instructions

### Environment Setup

1. **Python Version**: The project uses Python 3.13 (as indicated by the virtual environment).

2. **Virtual Environment**: 
   ```bash
   # Create a virtual environment
   python -m venv anotasienv

   # Activate the virtual environment
   # On Windows:
   anotasienv\Scripts\activate
   # On macOS/Linux:
   source anotasienv/bin/activate

   ```

3. **Dependencies**: The project uses the following key dependencies:
   - Django (web framework)
   - django-crispy-forms and crispy-bootstrap4 (for form styling)
   - django-allauth (for authentication, including social auth)
   - python-dotenv (for environment variable management)

   Since there's no requirements.txt file, you'll need to install these dependencies manually:
   ```bash
   pip install django django-crispy-forms crispy-bootstrap4 django-allauth python-dotenv Pillow
   ```

4. **Environment Variables**: Create a `.env` file in the project root with the following variables:
   ```
   SECRET_KEY=your_secret_key
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   GOOGLE_CLIENT_ID=your_google_client_id
   GOOGLE_CLIENT_SECRET=your_google_client_secret
   EMAIL_HOST_USER=your_email
   EMAIL_HOST_PASSWORD=your_email_password
   ```

5. **Database Setup**:
   ```bash
   # Navigate to the project directory
   cd Anotasi_Image

   # Run migrations
   python manage.py migrate

   # Create a superuser
   python manage.py createsuperuser
   ```

6. **Running the Development Server**:
   ```bash
   # First, check for any configuration issues
   python manage.py check
   
   # Run migrations to ensure database is ready
   python manage.py migrate
   
   # Start the development server (be patient, it may take 10-30 seconds to load)
   python manage.py runserver
   
   # Alternative: Run on a specific port
   python manage.py runserver 8001
   ```
   
   **Important**: 
   - DO NOT press Ctrl+C immediately after running the command
   - Wait for the server to fully load (you'll see "Starting development server at...")
   - The first load may take 30+ seconds due to PostgreSQL connection setup

## Troubleshooting

### Server Won't Start / KeyboardInterrupt Error

If you get a `KeyboardInterrupt` error when starting the server:

1. **Don't interrupt**: Wait for Django to fully load (30+ seconds)
2. **Check configuration**: Run `python manage.py check` first
3. **Database issues**: Make sure PostgreSQL is running
4. **Environment variables**: Ensure `.env` file is properly configured

```bash
# Step-by-step troubleshooting
cd Anotasi_Image

# 1. Check Django configuration
python manage.py check

# 2. Check database connection
python manage.py migrate --dry-run

# 3. Start server with verbose output
python manage.py runserver --verbosity=2

# 4. If still failing, try different port
python manage.py runserver 8001
```

### Common Issues

1. **PostgreSQL not running**: Start PostgreSQL service
2. **Missing dependencies**: Run `pip install -r requirements.txt`
3. **Environment variables**: Check `.env` file exists and has correct values
4. **Permission issues**: Ensure virtual environment is activated

## Testing Information

### Running Tests

The project uses Django's built-in testing framework. To run tests:

```bash
# Run all tests
python manage.py test

# Run tests for a specific app
python manage.py test master
python manage.py test annotator
python manage.py test reviewer

# Run a specific test class
python manage.py test master.tests.CustomUserModelTest

# Run a specific test method
python manage.py test master.tests.CustomUserModelTest.test_user_creation
```

### Writing Tests

Tests should be organized by app and model/view/functionality. Here's an example of a model test:

```python
from django.test import TestCase
from django.contrib.auth import get_user_model

class CustomUserModelTest(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword123"
        )

    def test_user_creation(self):
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(self.user.email, "test@example.com")
        self.assertTrue(self.user.is_active)
```

For view tests, use Django's test client:

```python
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

class ViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword123"
        )

    def test_login_view(self):
        response = self.client.post(reverse('master:login'), {
            'login': 'test@example.com',
            'password': 'testpassword123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after login
```

### Test Coverage

To measure test coverage, install the `coverage` package:

```bash
pip install coverage
```

Then run:

```bash
# Run tests with coverage
coverage run --source='.' manage.py test

# Generate a coverage report
coverage report

# Generate an HTML coverage report
coverage html
```

## Additional Development Information

### Code Style

The project follows standard Django conventions:

- Class names use CamelCase
- Function and variable names use snake_case
- Constants use UPPER_CASE
- Models have singular names
- App names are plural

### Project Structure

- `Anotasi_Image/`: Main project directory
  - `Anotasi_Image/`: Project settings and URL configuration
  - `master/`: Core app with user management and job/dataset models
  - `annotator/`: App for image annotation features
  - `reviewer/`: App for reviewing annotations
  - `media/`: User-uploaded files (datasets, job images)
  - `static/`: Static files (CSS, JS, images)
  - `templates/`: Project-wide templates

### Authentication

The project uses django-allauth for authentication, supporting both email/password and Google OAuth. The custom user model (`CustomUser`) in the `master` app extends Django's `AbstractUser` with additional fields.

### File Uploads

- Datasets are uploaded to `media/datasets/`
- Job images are uploaded to `media/job_images/<job_id>/`
- Maximum upload size is 50MB
- Allowed upload formats are .zip, .rar, and .7zip

### Known Issues

- There's a duplicate entry for 'accounts/' in the main URLs file
- The `ACCOUNT_AUTHENTICATION_METHOD` setting is deprecated and should be replaced with `ACCOUNT_LOGIN_METHODS = {'email'}`

### Development Workflow

1. Create a virtual environment and install dependencies
2. Make changes to the codebase
3. Write tests for new functionality
4. Run tests to ensure everything works
5. Run the development server to manually test changes
6. Commit changes with descriptive messages
