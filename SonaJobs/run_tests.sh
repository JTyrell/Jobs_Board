#!/bin/bash

# Resume Processing Integration Test Suite
# Comprehensive testing script for the entire resume processing workflow

set -e  # Exit on any error

echo "🚀 Resume Processing Integration Test Suite"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${2}${1}${NC}"
}

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    print_status "❌ Error: This script must be run from the Django project root directory" "$RED"
    exit 1
fi

# Check Python virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    print_status "⚠️  Warning: No virtual environment detected. Consider activating one." "$YELLOW"
fi

# Check dependencies
print_status "📋 Checking dependencies..." "$BLUE"

# Check if Django is available
if ! python -c "import django" 2>/dev/null; then
    print_status "❌ Django not found. Please install requirements." "$RED"
    exit 1
fi

# Check if resume processor modules are available
if ! python -c "from resume_processor.processor import ResumeProcessor" 2>/dev/null; then
    print_status "❌ Resume processor modules not found." "$RED"
    exit 1
fi

print_status "✅ Dependencies check passed" "$GREEN"

# Check for test media files
print_status "📁 Checking test media files..." "$BLUE"

MEDIA_DIR="media/resumes"
if [ -d "$MEDIA_DIR" ]; then
    PDF_COUNT=$(find "$MEDIA_DIR" -name "*.pdf" | wc -l)
    if [ "$PDF_COUNT" -gt 0 ]; then
        print_status "✅ Found $PDF_COUNT PDF files for testing" "$GREEN"
    else
        print_status "⚠️  No PDF files found in $MEDIA_DIR. Some tests may be skipped." "$YELLOW"
    fi
else
    print_status "⚠️  Media directory $MEDIA_DIR not found. Some tests may be skipped." "$YELLOW"
fi

# Function to run test category
run_test_category() {
    local category="$1"
    local description="$2"
    
    print_status "\n📋 Running $description..." "$BLUE"
    echo "----------------------------------------"
    
    if python manage.py test tests.test_resume_integration.${category} --verbosity=1 --keepdb; then
        print_status "✅ $description - PASSED" "$GREEN"
        return 0
    else
        print_status "❌ $description - FAILED" "$RED"
        return 1
    fi
}

# Function to run frontend tests
run_frontend_tests() {
    local category="$1"
    local description="$2"
    
    print_status "\n📋 Running $description..." "$BLUE"
    echo "----------------------------------------"
    
    if python manage.py test tests.test_frontend_integration.${category} --verbosity=1 --keepdb; then
        print_status "✅ $description - PASSED" "$GREEN"
        return 0
    else
        print_status "❌ $description - FAILED" "$RED"
        return 1
    fi
}

# Function to run UI validation tests
run_ui_tests() {
    local category="$1"
    local description="$2"
    
    print_status "\n📋 Running $description..." "$BLUE"
    echo "----------------------------------------"
    
    if python manage.py test tests.test_ui_validation.${category} --verbosity=1 --keepdb; then
        print_status "✅ $description - PASSED" "$GREEN"
        return 0
    else
        print_status "❌ $description - FAILED" "$RED"
        return 1
    fi
}

# Initialize counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Test categories array
declare -a TEST_CATEGORIES=(
    "FileUploadValidationTests:File Upload Validation"
    "PDFProcessingTests:PDF Processing"
    "EntityExtractionTests:Entity Extraction"
    "APIEndpointTests:API Endpoints"
    "DatabaseIntegrationTests:Database Integration"
    "PerformanceTests:Performance Tests"
    "ErrorHandlingTests:Error Handling"
    "IntegrationWorkflowTests:Complete Workflow"
)

# Frontend test categories
declare -a FRONTEND_CATEGORIES=(
    "JobApplicationFormTests:Job Application Form"
    "EmployerDashboardTests:Employer Dashboard"
    "ErrorStateTests:Error State Handling"
    "LoadingStateTests:Loading State Handling"
)

# UI validation categories
declare -a UI_CATEGORIES=(
    "FormValidationTests:Form Validation"
    "ErrorStateDisplayTests:Error State Display"
    "LoadingStateTests:Loading States"
    "ResponsiveDesignTests:Responsive Design"
    "AccessibilityTests:Accessibility"
    "UserExperienceFlowTests:User Experience Flows"
)

print_status "\n🧪 Starting Integration Tests..." "$BLUE"
print_status "=================================" "$BLUE"

# Run integration tests
for category in "${TEST_CATEGORIES[@]}"; do
    IFS=':' read -r test_class description <<< "$category"
    ((TOTAL_TESTS++))
    
    if run_test_category "$test_class" "$description"; then
        ((PASSED_TESTS++))
    else
        ((FAILED_TESTS++))
    fi
done

print_status "\n🖥️  Starting Frontend Tests..." "$BLUE"
print_status "==============================" "$BLUE"

# Run frontend tests
for category in "${FRONTEND_CATEGORIES[@]}"; do
    IFS=':' read -r test_class description <<< "$category"
    ((TOTAL_TESTS++))
    
    if run_frontend_tests "$test_class" "$description"; then
        ((PASSED_TESTS++))
    else
        ((FAILED_TESTS++))
    fi
done

print_status "\n🎨 Starting UI Validation Tests..." "$BLUE"
print_status "==================================" "$BLUE"

# Run UI validation tests
for category in "${UI_CATEGORIES[@]}"; do
    IFS=':' read -r test_class description <<< "$category"
    ((TOTAL_TESTS++))
    
    if run_ui_tests "$test_class" "$description"; then
        ((PASSED_TESTS++))
    else
        ((FAILED_TESTS++))
    fi
done

# Generate comprehensive report using the Python test runner
print_status "\n📊 Generating Comprehensive Report..." "$BLUE"
print_status "====================================" "$BLUE"

if python run_integration_tests.py; then
    print_status "✅ Comprehensive report generated successfully" "$GREEN"
else
    print_status "⚠️  Report generation completed with warnings" "$YELLOW"
fi

# Final summary
print_status "\n📈 FINAL TEST SUMMARY" "$BLUE"
print_status "=====================" "$BLUE"
print_status "Total Tests: $TOTAL_TESTS" "$BLUE"
print_status "Passed: $PASSED_TESTS" "$GREEN"
print_status "Failed: $FAILED_TESTS" "$RED"

SUCCESS_RATE=$((PASSED_TESTS * 100 / TOTAL_TESTS))
print_status "Success Rate: ${SUCCESS_RATE}%" "$BLUE"

# Check if all tests passed
if [ "$FAILED_TESTS" -eq 0 ]; then
    print_status "\n🎉 ALL TESTS PASSED!" "$GREEN"
    print_status "Resume processing system is ready for production!" "$GREEN"
    
    # Check for generated reports
    if [ -f "test_results.html" ]; then
        print_status "\n📄 Test reports generated:" "$BLUE"
        print_status "- HTML Report: test_results.html" "$BLUE"
    fi
    
    if [ -f "test_results.json" ]; then
        print_status "- JSON Report: test_results.json" "$BLUE"
    fi
    
    exit 0
else
    print_status "\n💥 SOME TESTS FAILED!" "$RED"
    print_status "Please review the test results and fix issues before deployment." "$RED"
    print_status "\nFailed test categories need attention:" "$YELLOW"
    
    exit 1
fi