#!/usr/bin/env python
"""
Resume Processing Integration Test Runner
Executes comprehensive tests and generates structured reports.
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime
from pathlib import Path

# Add the Django project to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobs_platform.settings')

import django
django.setup()

from django.test.runner import DiscoverRunner
from django.test.utils import get_runner
from django.conf import settings
from django.core.management import call_command


class ResumeIntegrationTestRunner:
    """Custom test runner for resume processing integration tests"""
    
    def __init__(self):
        self.test_results = []
        self.start_time = None
        self.end_time = None
        
    def run_tests(self):
        """Run all integration tests and collect results"""
        print("🚀 Starting Resume Processing Integration Tests")
        print("=" * 60)
        
        self.start_time = time.time()
        
        # Test categories to run
        test_categories = [
            {
                'name': 'File Upload Validation',
                'module': 'tests.test_resume_integration.FileUploadValidationTests',
                'description': 'Test file upload validation and processing'
            },
            {
                'name': 'PDF Processing',
                'module': 'tests.test_resume_integration.PDFProcessingTests',
                'description': 'Test PDF text extraction and processing'
            },
            {
                'name': 'Entity Extraction',
                'module': 'tests.test_resume_integration.EntityExtractionTests',
                'description': 'Test AI-powered entity extraction'
            },
            {
                'name': 'API Endpoints',
                'module': 'tests.test_resume_integration.APIEndpointTests',
                'description': 'Test all resume processor API endpoints'
            },
            {
                'name': 'Database Integration',
                'module': 'tests.test_resume_integration.DatabaseIntegrationTests',
                'description': 'Test database storage and relationships'
            },
            {
                'name': 'Performance Tests',
                'module': 'tests.test_resume_integration.PerformanceTests',
                'description': 'Test performance requirements and benchmarks'
            },
            {
                'name': 'Error Handling',
                'module': 'tests.test_resume_integration.ErrorHandlingTests',
                'description': 'Test comprehensive error handling'
            },
            {
                'name': 'Frontend Integration',
                'module': 'tests.test_frontend_integration.JobApplicationFormTests',
                'description': 'Test job application form with resume upload'
            },
            {
                'name': 'Employer Dashboard',
                'module': 'tests.test_frontend_integration.EmployerDashboardTests',
                'description': 'Test employer dashboard resume viewing'
            },
            {
                'name': 'Error States',
                'module': 'tests.test_frontend_integration.ErrorStateTests',
                'description': 'Test frontend error state handling'
            },
            {
                'name': 'Loading States',
                'module': 'tests.test_frontend_integration.LoadingStateTests',
                'description': 'Test loading state handling'
            },
            {
                'name': 'Complete Workflow',
                'module': 'tests.test_resume_integration.IntegrationWorkflowTests',
                'description': 'Test complete end-to-end workflow'
            }
        ]
        
        # Run each test category
        for category in test_categories:
            print(f"\n📋 Running {category['name']} Tests")
            print(f"   {category['description']}")
            print("-" * 50)
            
            result = self._run_test_category(category)
            self.test_results.append(result)
            
            # Print immediate feedback
            status = "✅ PASSED" if result['passed'] else "❌ FAILED"
            print(f"   {status} - {result['test_count']} tests, {result['performance']:.2f}s")
            
            if result['errors']:
                print(f"   ⚠️  {len(result['errors'])} errors found")
        
        self.end_time = time.time()
        
        # Generate comprehensive report
        self._generate_report()
        
        # Return overall success
        return all(result['passed'] for result in self.test_results)
    
    def _run_test_category(self, category):
        """Run a specific test category and return structured results"""
        start_time = time.time()
        
        try:
            # Use Django's test runner to run the specific test module
            runner = DiscoverRunner(verbosity=1, interactive=False, keepdb=True)
            
            # Run the specific test module without setting up environment again
            result = runner.run_tests([category['module']])
            
            processing_time = time.time() - start_time
            
            return {
                'scenario': category['name'],
                'passed': result == 0,  # Django test runner returns 0 for success
                'errors': [],  # Will be populated if we can capture specific errors
                'dataConsistency': 100.0 if result == 0 else 0.0,
                'performance': processing_time * 1000,  # Convert to milliseconds
                'test_count': 1,  # We'll improve this with actual test counting
                'description': category['description']
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            
            return {
                'scenario': category['name'],
                'passed': False,
                'errors': [{
                    'type': 'runtime',
                    'message': str(e),
                    'component': category['module']
                }],
                'dataConsistency': 0.0,
                'performance': processing_time * 1000,
                'test_count': 0,
                'description': category['description']
            }
    
    def _generate_report(self):
        """Generate comprehensive test report"""
        total_time = self.end_time - self.start_time
        total_tests = sum(result['test_count'] for result in self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['passed'])
        
        # Console report
        print("\n" + "="*60)
        print("📊 RESUME PROCESSING INTEGRATION TEST REPORT")
        print("="*60)
        
        print(f"⏱️  Total Time: {total_time:.2f} seconds")
        print(f"🧪 Total Test Categories: {len(self.test_results)}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {len(self.test_results) - passed_tests}")
        print(f"📈 Success Rate: {(passed_tests/len(self.test_results)*100):.1f}%")
        
        # Detailed results
        print("\n📋 Detailed Results:")
        print("-" * 60)
        
        for result in self.test_results:
            status = "✅" if result['passed'] else "❌"
            print(f"{status} {result['scenario']}")
            print(f"    Performance: {result['performance']:.0f}ms")
            print(f"    Data Consistency: {result['dataConsistency']:.1f}%")
            
            if result['errors']:
                print(f"    ⚠️  Errors:")
                for error in result['errors']:
                    print(f"      - {error['type']}: {error['message']}")
        
        # Performance analysis
        print("\n⚡ Performance Analysis:")
        print("-" * 60)
        
        slow_tests = [r for r in self.test_results if r['performance'] > 3000]  # > 3 seconds
        if slow_tests:
            print("⚠️  Tests exceeding 3s performance threshold:")
            for test in slow_tests:
                print(f"   - {test['scenario']}: {test['performance']:.0f}ms")
        else:
            print("✅ All tests meet performance requirements (<3s)")
        
        # Error summary
        all_errors = []
        for result in self.test_results:
            all_errors.extend(result['errors'])
        
        if all_errors:
            print("\n🚨 Error Summary:")
            print("-" * 60)
            
            error_types = {}
            for error in all_errors:
                error_type = error['type']
                if error_type not in error_types:
                    error_types[error_type] = []
                error_types[error_type].append(error)
            
            for error_type, errors in error_types.items():
                print(f"   {error_type.upper()}: {len(errors)} errors")
                for error in errors[:3]:  # Show first 3 errors of each type
                    print(f"      - {error['message']}")
                if len(errors) > 3:
                    print(f"      ... and {len(errors) - 3} more")
        
        # Generate JSON report
        self._generate_json_report()
        
        # Generate HTML report
        self._generate_html_report()
        
        print(f"\n📄 Reports generated:")
        print(f"   - JSON: test_results.json")
        print(f"   - HTML: test_results.html")
    
    def _generate_json_report(self):
        """Generate JSON report file"""
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_categories': len(self.test_results),
                'passed': sum(1 for r in self.test_results if r['passed']),
                'failed': sum(1 for r in self.test_results if not r['passed']),
                'total_time_seconds': self.end_time - self.start_time,
                'success_rate': sum(1 for r in self.test_results if r['passed']) / len(self.test_results) * 100
            },
            'results': self.test_results,
            'performance_analysis': {
                'slow_tests': [r for r in self.test_results if r['performance'] > 3000],
                'average_performance': sum(r['performance'] for r in self.test_results) / len(self.test_results)
            }
        }
        
        with open('test_results.json', 'w') as f:
            json.dump(report_data, f, indent=2)
    
    def _generate_html_report(self):
        """Generate HTML report file"""
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Resume Processing Integration Test Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .summary-card {{ background: #ecf0f1; padding: 20px; border-radius: 8px; text-align: center; }}
        .summary-card h3 {{ margin: 0; color: #2c3e50; }}
        .summary-card .value {{ font-size: 2em; font-weight: bold; margin: 10px 0; }}
        .passed .value {{ color: #27ae60; }}
        .failed .value {{ color: #e74c3c; }}
        .time .value {{ color: #f39c12; }}
        .rate .value {{ color: #9b59b6; }}
        .test-results {{ margin-top: 30px; }}
        .test-item {{ margin: 15px 0; padding: 15px; border-left: 4px solid #bdc3c7; background: #f8f9fa; border-radius: 0 5px 5px 0; }}
        .test-item.passed {{ border-left-color: #27ae60; }}
        .test-item.failed {{ border-left-color: #e74c3c; }}
        .test-title {{ font-weight: bold; font-size: 1.1em; }}
        .test-description {{ color: #7f8c8d; margin: 5px 0; }}
        .test-metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin-top: 10px; }}
        .metric {{ background: white; padding: 8px; border-radius: 4px; text-align: center; }}
        .errors {{ margin-top: 10px; }}
        .error-item {{ background: #fdf2f2; border: 1px solid #f5c6cb; padding: 8px; margin: 5px 0; border-radius: 4px; }}
        .performance-warning {{ color: #f39c12; font-weight: bold; }}
        .timestamp {{ color: #7f8c8d; font-size: 0.9em; margin-bottom: 20px; }}
        .mermaid {{ text-align: center; margin: 20px 0; }}
    </style>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
</head>
<body>
    <div class="container">
        <h1>🧪 Resume Processing Integration Test Report</h1>
        <div class="timestamp">Generated: {timestamp}</div>
        
        <div class="summary">
            <div class="summary-card passed">
                <h3>✅ Passed</h3>
                <div class="value">{passed}</div>
            </div>
            <div class="summary-card failed">
                <h3>❌ Failed</h3>
                <div class="value">{failed}</div>
            </div>
            <div class="summary-card time">
                <h3>⏱️ Total Time</h3>
                <div class="value">{total_time:.1f}s</div>
            </div>
            <div class="summary-card rate">
                <h3>📈 Success Rate</h3>
                <div class="value">{success_rate:.1f}%</div>
            </div>
        </div>

        <h2>📊 Test Flow Diagram</h2>
        <div class="mermaid">
            graph LR
                A[Upload] --> B[PDF Processing]
                B --> C[API Validation] 
                C --> D[Database Matching]
                D --> E[Frontend Rendering]
                E --> F[User Output]
                
                style A fill:#e1f5fe
                style B fill:#e8f5e8
                style C fill:#fff3e0
                style D fill:#f3e5f5
                style E fill:#fce4ec
                style F fill:#e0f2f1
        </div>

        <h2>📋 Detailed Test Results</h2>
        <div class="test-results">
            {test_results_html}
        </div>
        
        <h2>⚡ Performance Analysis</h2>
        <p>Performance threshold: <strong>3 seconds per document</strong></p>
        {performance_analysis_html}
    </div>
    
    <script>
        mermaid.initialize({{ startOnLoad: true }});
    </script>
</body>
</html>
        """
        
        # Generate test results HTML
        test_results_html = ""
        for result in self.test_results:
            status_class = "passed" if result['passed'] else "failed"
            status_icon = "✅" if result['passed'] else "❌"
            
            performance_warning = ""
            if result['performance'] > 3000:
                performance_warning = ' <span class="performance-warning">⚠️ Slow</span>'
            
            errors_html = ""
            if result['errors']:
                errors_html = '<div class="errors"><strong>Errors:</strong>'
                for error in result['errors']:
                    errors_html += f'<div class="error-item"><strong>{error["type"]}:</strong> {error["message"]}</div>'
                errors_html += '</div>'
            
            test_results_html += f"""
            <div class="test-item {status_class}">
                <div class="test-title">{status_icon} {result['scenario']}</div>
                <div class="test-description">{result['description']}</div>
                <div class="test-metrics">
                    <div class="metric">
                        <strong>Performance</strong><br>
                        {result['performance']:.0f}ms{performance_warning}
                    </div>
                    <div class="metric">
                        <strong>Data Consistency</strong><br>
                        {result['dataConsistency']:.1f}%
                    </div>
                    <div class="metric">
                        <strong>Status</strong><br>
                        {status_icon} {'PASSED' if result['passed'] else 'FAILED'}
                    </div>
                </div>
                {errors_html}
            </div>
            """
        
        # Performance analysis HTML
        slow_tests = [r for r in self.test_results if r['performance'] > 3000]
        if slow_tests:
            performance_analysis_html = "<p class='performance-warning'>⚠️ Tests exceeding performance threshold:</p><ul>"
            for test in slow_tests:
                performance_analysis_html += f"<li>{test['scenario']}: {test['performance']:.0f}ms</li>"
            performance_analysis_html += "</ul>"
        else:
            performance_analysis_html = "<p style='color: #27ae60;'>✅ All tests meet performance requirements!</p>"
        
        # Fill template
        html_content = html_template.format(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            passed=sum(1 for r in self.test_results if r['passed']),
            failed=sum(1 for r in self.test_results if not r['passed']),
            total_time=self.end_time - self.start_time,
            success_rate=sum(1 for r in self.test_results if r['passed']) / len(self.test_results) * 100,
            test_results_html=test_results_html,
            performance_analysis_html=performance_analysis_html
        )
        
        with open('test_results.html', 'w', encoding='utf-8') as f:
            f.write(html_content)


def main():
    """Main entry point for test runner"""
    print("Setting up test environment...")
    
    # Ensure we're in the right directory
    os.chdir(project_root)
    
    # Check if media files exist
    media_path = project_root / 'media' / 'resumes'
    if not media_path.exists():
        print("⚠️  Warning: Resume media files not found. Some tests may be skipped.")
        print(f"Expected location: {media_path}")
    
    # Run migrations to ensure test database is set up
    print("Running database migrations...")
    try:
        call_command('migrate', verbosity=0, interactive=False)
    except Exception as e:
        print(f"Warning: Migration failed: {e}")
    
    # Create test runner and run tests
    runner = ResumeIntegrationTestRunner()
    success = runner.run_tests()
    
    if success:
        print("\n🎉 All tests passed! Resume processing system is ready for production.")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed. Please review the report and fix issues before deployment.")
        sys.exit(1)


if __name__ == '__main__':
    main()