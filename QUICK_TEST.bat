@echo off
REM M01 Employee Onboarding Module - Quick Testing Script
REM Run this to quickly set up and test the onboarding module

echo.
echo ============================================
echo M01 Onboarding Module - Quick Test Setup
echo ============================================
echo.

REM Step 1: Create migrations
echo [1/4] Creating migrations...
python manage.py makemigrations onboarding
if %errorlevel% neq 0 (
    echo ERROR: Migration creation failed!
    pause
    exit /b 1
)

REM Step 2: Apply migrations
echo.
echo [2/4] Applying migrations to database...
python manage.py migrate onboarding
if %errorlevel% neq 0 (
    echo ERROR: Migration application failed!
    pause
    exit /b 1
)

REM Step 3: Create initial data
echo.
echo [3/4] Creating document requirements...
python manage.py shell <<EOF
from onboarding.models import DocumentRequirement

docs = [
    {'name': 'Resume/CV', 'is_required': True, 'file_type_allowed': 'pdf', 'description': 'Your resume or CV'},
    {'name': 'ID Proof', 'is_required': True, 'file_type_allowed': 'pdf', 'description': 'Aadhar/Passport'},
    {'name': 'Address Proof', 'is_required': True, 'file_type_allowed': 'pdf', 'description': 'Utility bill'},
    {'name': 'Bank Details', 'is_required': True, 'file_type_allowed': 'pdf', 'description': 'Bank form'},
]

for doc_data in docs:
    doc, created = DocumentRequirement.objects.get_or_create(
        name=doc_data['name'],
        defaults={
            'is_required': doc_data['is_required'],
            'file_type_allowed': doc_data['file_type_allowed'],
            'description': doc_data['description']
        }
    )
    status = "Created" if created else "Already exists"
    print(f"✓ {doc.name} - {status}")

print("\n✓ All document requirements ready!")
EOF

if %errorlevel% neq 0 (
    echo WARNING: Document creation had issues, but continuing...
)

REM Step 4: Create media folders
echo.
echo [4/4] Creating media folders...
if not exist media (
    mkdir media
    echo ✓ Created media folder
)
if not exist media\employee_documents (
    mkdir media\employee_documents
    echo ✓ Created employee_documents folder
)
if not exist media\offer_letters (
    mkdir media\offer_letters
    echo ✓ Created offer_letters folder
)
if not exist media\signatures (
    mkdir media\signatures
    echo ✓ Created signatures folder
)

echo.
echo ============================================
echo ✓ SETUP COMPLETE!
echo ============================================
echo.
echo Next Steps:
echo.
echo 1. Update .env file with:
echo    - EMAIL credentials (Gmail)
echo    - TWILIO credentials (WhatsApp) [Optional]
echo.
echo 2. Run the development server:
echo    python manage.py runserver
echo.
echo 3. Go to: http://localhost:8000/admin/
echo.
echo 4. Create a test employee:
echo    - Go to Employees → Add Employee
echo    - Name: Test User
echo    - Email: test@example.com
echo    - Phone: +919876543210
echo    - Position: Developer
echo.
echo 5. Send invitation:
echo    - Go to http://localhost:8000/onboarding/
echo    - Find Test User in Pending Invitations
echo    - Click Send
echo    - Check console for email output
echo.
echo 6. Accept invitation and test portal:
echo    - Copy invitation link from console email
echo    - Paste in browser
echo    - Click "Accept & Continue"
echo.
echo 7. Upload documents and sign offer
echo    - Follow prompts on portal
echo.
echo For complete testing guide, see: TESTING_GUIDE.md
echo.
pause
