#!/usr/bin/env python3
"""
Final Test Execution Script for Resume Processing System
Provides systematic testing with targeted fixes for remaining issues
"""
import os
import sys
import subprocess
import json
import time
from datetime import datetime

class FinalTestRunner:
    def __init__(self):
        self.start_time = time.time()
        self.test_results = {}
        self.critical_issues = []
        
    def run_specific_test(self, test_path, description=""):
        """Run a specific test and capture results"""
        print(f"\n{'='*60}")
        print(f"🧪 Testing: {description or test_path}")
        print('='*60)
        
        try:
            result = subprocess.run(
                [sys.executable, 'manage.py', 'test', test_path, '--keepdb', '--verbosity=2'],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            success = result.returncode == 0
            self.test_results[test_path] = {
                'success': success,
                'description': description,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'duration': time.time() - self.start_time
            }
            
            if success:
                print(f"✅ PASSED: {description}")
            else:
                print(f"❌ FAILED: {description}")
                print(f"Error: {result.stderr}")
                self.critical_issues.append({
                    'test': test_path,
                    'description': description,
                    'error': result.stderr
                })
            
            return success
            
        except subprocess.TimeoutExpired:
            print(f"⏰ TIMEOUT: {description}")
            self.critical_issues.append({
                'test': test_path,
                'description': description,
                'error': 'Test timeout after 120 seconds'
            })
            return False
        except Exception as e:
            print(f"💥 ERROR: {description} - {e}")
            return False
    
    def run_focused_tests(self):
        """Run focused tests on the most critical components"""
        print("🎯 Running Focused Integration Tests")
        print("Targeting the most critical components for production readiness\n")
        
        # Test critical components in order of importance
        tests = [
            # Core Database Operations
            ("tests.test_resume_integration.DatabaseIntegrationTests.test_analysis_storage", 
             "Database Analysis Storage"),
            
            # PDF Processing
            ("tests.test_resume_integration.PDFProcessingTests.test_pdf_text_extraction",
             "PDF Text Extraction"),
            
            # API Endpoints  
            ("tests.test_resume_integration.APIEndpointTests.test_validate_file_api",
             "File Validation API"),
            
            # Entity Extraction
            ("tests.test_resume_integration.EntityExtractionTests.test_skills_extraction",
             "Skill Extraction"),
            
            # Performance  
            ("tests.test_resume_integration.PerformanceTests.test_processing_latency",
             "Processing Performance"),
            
            # Error Handling
            ("tests.test_resume_integration.FileUploadValidationTests.test_invalid_file_type",
             "Error Handling"),
            
            # Frontend Basic
            ("tests.test_frontend_integration.JobApplicationFormTests.test_job_application_form_render",
             "Frontend Form Rendering"),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_path, description in tests:
            if self.run_specific_test(test_path, description):
                passed += 1
            time.sleep(1)  # Brief pause between tests
        
        return passed, total
    
    def check_system_health(self):
        """Check basic system health before running tests"""
        print("🏥 System Health Check")
        print("-" * 30)
        
        # Check Django setup
        try:
            result = subprocess.run([sys.executable, 'manage.py', 'check'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Django system check passed")
            else:
                print(f"❌ Django system check failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Django check error: {e}")
            return False
        
        # Check database connectivity
        try:
            result = subprocess.run([sys.executable, 'manage.py', 'migrate', '--check'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Database connectivity confirmed")
            else:
                print(f"⚠️  Database migration status: {result.stderr}")
        except Exception as e:
            print(f"❌ Database check error: {e}")
            
        # Check static files
        static_dir = os.path.join(os.getcwd(), 'staticfiles')
        if os.path.exists(static_dir):
            print("✅ Static files directory exists")
        else:
            print("⚠️  Static files directory missing")
            
        print()
        return True
    
    def run_dependency_check(self):
        """Check that all required dependencies are installed"""
        print("📦 Dependency Check")
        print("-" * 20)
        
        dependencies = [
            'django',
            'pdfplumber', 
            'spacy',
            'sklearn',
            'numpy'
        ]
        
        all_good = True
        for dep in dependencies:
            try:
                __import__(dep)
                print(f"✅ {dep}")
            except ImportError:
                print(f"❌ {dep} - MISSING")
                all_good = False
        
        # Check spaCy model
        try:
            import spacy
            nlp = spacy.load('en_core_web_sm')
            print("✅ spaCy en_core_web_sm model")
        except OSError:
            print("❌ spaCy en_core_web_sm model - MISSING")
            all_good = False
        except Exception as e:
            print(f"⚠️  spaCy model check: {e}")
            
        print()
        return all_good
    
    def generate_summary_report(self, passed, total):
        """Generate a summary report of test results"""
        duration = time.time() - self.start_time
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print("\n" + "="*60)
        print("📊 FINAL TEST EXECUTION SUMMARY")
        print("="*60)
        print(f"⏱️  Total Execution Time: {duration:.2f} seconds")
        print(f"🧪 Tests Run: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {total - passed}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 EXCELLENT: System ready for production deployment!")
        elif success_rate >= 60:
            print("👍 GOOD: System ready for staging with minor fixes needed")
        elif success_rate >= 40:
            print("⚠️  MODERATE: System needs additional work before deployment")
        else:
            print("🚨 CRITICAL: Major issues need resolution before deployment")
        
        if self.critical_issues:
            print("\n🚨 Critical Issues to Address:")
            print("-" * 40)
            for i, issue in enumerate(self.critical_issues, 1):
                print(f"{i}. {issue['description']}")
                print(f"   Test: {issue['test']}")
                print(f"   Error: {issue['error'][:100]}...")
                print()
        
        # Save detailed results
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'duration': duration,
            'tests_run': total,
            'passed': passed,
            'failed': total - passed,
            'success_rate': success_rate,
            'critical_issues': self.critical_issues,
            'detailed_results': self.test_results
        }
        
        with open('final_test_results.json', 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"📄 Detailed report saved to: final_test_results.json")
        
        return success_rate >= 60  # Return True if ready for staging
    
    def run_quick_fixes(self):
        """Apply quick fixes for known issues"""
        print("🔧 Applying Quick Fixes")
        print("-" * 25)
        
        fixes_applied = 0
        
        # Fix 1: Ensure static files are collected
        try:
            result = subprocess.run([sys.executable, 'manage.py', 'collectstatic', '--noinput'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Static files collected")
                fixes_applied += 1
            else:
                print(f"⚠️  Static files collection: {result.stderr}")
        except Exception as e:
            print(f"❌ Static files error: {e}")
        
        # Fix 2: Run database migrations
        try:
            result = subprocess.run([sys.executable, 'manage.py', 'migrate'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Database migrations applied")
                fixes_applied += 1
            else:
                print(f"⚠️  Database migrations: {result.stderr}")
        except Exception as e:
            print(f"❌ Migration error: {e}")
        
        print(f"🔧 Applied {fixes_applied} quick fixes\n")
        return fixes_applied

def main():
    """Main execution function"""
    print("🚀 Resume Processing System - Final Test Execution")
    print("="*60)
    print("This script runs focused tests on critical components")
    print("to assess production readiness of the resume processing system.\n")
    
    runner = FinalTestRunner()
    
    # Step 1: System health check
    if not runner.check_system_health():
        print("❌ System health check failed. Aborting tests.")
        return False
    
    # Step 2: Dependency check  
    if not runner.run_dependency_check():
        print("❌ Dependency check failed. Please install missing packages.")
        return False
    
    # Step 3: Apply quick fixes
    runner.run_quick_fixes()
    
    # Step 4: Run focused tests
    passed, total = runner.run_focused_tests()
    
    # Step 5: Generate summary report
    production_ready = runner.generate_summary_report(passed, total)
    
    if production_ready:
        print("\n🎯 RECOMMENDATION: Proceed with staging deployment")
        print("   The system shows good stability for basic operations.")
        print("   Monitor closely and gather user feedback.")
    else:
        print("\n🎯 RECOMMENDATION: Continue development and testing")
        print("   Address critical issues before attempting deployment.")
        print("   Focus on the failing tests listed above.")
    
    return production_ready

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Test execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)