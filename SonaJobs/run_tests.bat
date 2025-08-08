@echo off
REM Resume Processing Integration Test Suite - Windows Batch Script
REM Comprehensive testing script for the entire resume processing workflow

echo ============================================
echo 🚀 Resume Processing Integration Test Suite
echo ============================================

REM Check if we're in the right directory
if not exist "manage.py" (
    echo ❌ Error: This script must be run from the Django project root directory
    pause
    exit /b 1
)

REM Check Python virtual environment
if "%VIRTUAL_ENV%"=="" (
    echo ⚠️  Warning: No virtual environment detected. Consider activating one.
)

REM Check dependencies
echo 📋 Checking dependencies...

REM Check if Django is available
python -c "import django" 2>nul
if %errorlevel% neq 0 (
    echo ❌ Django not found. Please install requirements.
    pause
    exit /b 1
)

REM Check if resume processor modules are available
python -c "from resume_processor.processor import ResumeProcessor" 2>nul
if %errorlevel% neq 0 (
    echo ❌ Resume processor modules not found.
    pause
    exit /b 1
)

echo ✅ Dependencies check passed

REM Check for test media files
echo 📁 Checking test media files...

set MEDIA_DIR=media\resumes
if exist "%MEDIA_DIR%" (
    for /f %%i in ('dir /b "%MEDIA_DIR%\*.pdf" 2^>nul ^| find /c /v ""') do set PDF_COUNT=%%i
    if !PDF_COUNT! gtr 0 (
        echo ✅ Found !PDF_COUNT! PDF files for testing
    ) else (
        echo ⚠️  No PDF files found in %MEDIA_DIR%. Some tests may be skipped.
    )
) else (
    echo ⚠️  Media directory %MEDIA_DIR% not found. Some tests may be skipped.
)

REM Initialize counters
set TOTAL_TESTS=0
set PASSED_TESTS=0
set FAILED_TESTS=0

echo.
echo 🧪 Starting Integration Tests...
echo =================================

REM Test categories
set TEST_CATEGORIES[0]=FileUploadValidationTests:File Upload Validation
set TEST_CATEGORIES[1]=PDFProcessingTests:PDF Processing
set TEST_CATEGORIES[2]=EntityExtractionTests:Entity Extraction
set TEST_CATEGORIES[3]=APIEndpointTests:API Endpoints
set TEST_CATEGORIES[4]=DatabaseIntegrationTests:Database Integration
set TEST_CATEGORIES[5]=PerformanceTests:Performance Tests
set TEST_CATEGORIES[6]=ErrorHandlingTests:Error Handling
set TEST_CATEGORIES[7]=IntegrationWorkflowTests:Complete Workflow

REM Frontend test categories
set FRONTEND_CATEGORIES[0]=JobApplicationFormTests:Job Application Form
set FRONTEND_CATEGORIES[1]=EmployerDashboardTests:Employer Dashboard
set FRONTEND_CATEGORIES[2]=ErrorStateTests:Error State Handling
set FRONTEND_CATEGORIES[3]=LoadingStateTests:Loading State Handling

REM UI validation categories
set UI_CATEGORIES[0]=FormValidationTests:Form Validation
set UI_CATEGORIES[1]=ErrorStateDisplayTests:Error State Display
set UI_CATEGORIES[2]=LoadingStateTests:Loading States
set UI_CATEGORIES[3]=ResponsiveDesignTests:Responsive Design
set UI_CATEGORIES[4]=AccessibilityTests:Accessibility
set UI_CATEGORIES[5]=UserExperienceFlowTests:User Experience Flows

REM Function to run test category
:run_test_category
set test_class=%1
set description=%2

echo.
echo 📋 Running %description%...
echo ----------------------------------------

python manage.py test tests.test_resume_integration.%test_class% --verbosity=1 --keepdb
if %errorlevel% equ 0 (
    echo ✅ %description% - PASSED
    set /a PASSED_TESTS+=1
) else (
    echo ❌ %description% - FAILED
    set /a FAILED_TESTS+=1
)
set /a TOTAL_TESTS+=1
goto :eof

REM Function to run frontend tests
:run_frontend_tests
set test_class=%1
set description=%2

echo.
echo 📋 Running %description%...
echo ----------------------------------------

python manage.py test tests.test_frontend_integration.%test_class% --verbosity=1 --keepdb
if %errorlevel% equ 0 (
    echo ✅ %description% - PASSED
    set /a PASSED_TESTS+=1
) else (
    echo ❌ %description% - FAILED
    set /a FAILED_TESTS+=1
)
set /a TOTAL_TESTS+=1
goto :eof

REM Function to run UI tests
:run_ui_tests
set test_class=%1
set description=%2

echo.
echo 📋 Running %description%...
echo ----------------------------------------

python manage.py test tests.test_ui_validation.%test_class% --verbosity=1 --keepdb
if %errorlevel% equ 0 (
    echo ✅ %description% - PASSED
    set /a PASSED_TESTS+=1
) else (
    echo ❌ %description% - FAILED
    set /a FAILED_TESTS+=1
)
set /a TOTAL_TESTS+=1
goto :eof

REM Run all test categories
for /L %%i in (0,1,7) do (
    for /f "tokens=1,2 delims=:" %%a in ("!TEST_CATEGORIES[%%i]!") do (
        call :run_test_category "%%a" "%%b"
    )
)

echo.
echo 🖥️  Starting Frontend Tests...
echo ==============================

for /L %%i in (0,1,3) do (
    for /f "tokens=1,2 delims=:" %%a in ("!FRONTEND_CATEGORIES[%%i]!") do (
        call :run_frontend_tests "%%a" "%%b"
    )
)

echo.
echo 🎨 Starting UI Validation Tests...
echo ==================================

for /L %%i in (0,1,5) do (
    for /f "tokens=1,2 delims=:" %%a in ("!UI_CATEGORIES[%%i]!") do (
        call :run_ui_tests "%%a" "%%b"
    )
)

REM Generate comprehensive report
echo.
echo 📊 Generating Comprehensive Report...
echo ====================================

python run_integration_tests.py
if %errorlevel% equ 0 (
    echo ✅ Comprehensive report generated successfully
) else (
    echo ⚠️  Report generation completed with warnings
)

REM Final summary
echo.
echo 📈 FINAL TEST SUMMARY
echo =====================
echo Total Tests: %TOTAL_TESTS%
echo Passed: %PASSED_TESTS%
echo Failed: %FAILED_TESTS%

set /a SUCCESS_RATE=(%PASSED_TESTS% * 100) / %TOTAL_TESTS%
echo Success Rate: %SUCCESS_RATE%%%

REM Check if all tests passed
if %FAILED_TESTS% equ 0 (
    echo.
    echo 🎉 ALL TESTS PASSED!
    echo Resume processing system is ready for production!
    
    REM Check for generated reports
    if exist "test_results.html" (
        echo.
        echo 📄 Test reports generated:
        echo - HTML Report: test_results.html
    )
    
    if exist "test_results.json" (
        echo - JSON Report: test_results.json
    )
    
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 0
) else (
    echo.
    echo 💥 SOME TESTS FAILED!
    echo Please review the test results and fix issues before deployment.
    echo.
    echo Failed test categories need attention.
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)