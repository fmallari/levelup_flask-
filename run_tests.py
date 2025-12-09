"""
Test Runner Script
Save as run_tests.py in your project root

This script runs all tests and generates a coverage report.
"""

import sys
import os
import unittest

# Add current directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


def run_all_tests():
    """Run all unit tests"""
    print("=" * 70)
    print("Running LevelUp Flask Test Suite")
    print("=" * 70)
    print()
    
    # Discover and run all tests in the tests directory
    loader = unittest.TestLoader()
    start_dir = 'tests'
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print()
    print("=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print()
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


def run_with_coverage():
    """Run tests with coverage report"""
    try:
        import coverage
    except ImportError:
        print("Coverage.py not installed. Install with: pip install coverage")
        return run_all_tests()
    
    print("Running tests with coverage...")
    print()
    
    # Start coverage
    cov = coverage.Coverage()
    cov.start()
    
    # Run tests
    exit_code = run_all_tests()
    
    # Stop coverage and generate report
    cov.stop()
    cov.save()
    
    print()
    print("=" * 70)
    print("Coverage Report")
    print("=" * 70)
    cov.report()
    
    # Generate HTML coverage report
    print()
    print("Generating HTML coverage report...")
    cov.html_report(directory='htmlcov')
    print("HTML report generated in ./htmlcov/index.html")
    print()
    
    return exit_code


if __name__ == '__main__':
    # Check for coverage flag
    if '--coverage' in sys.argv or '-c' in sys.argv:
        exit_code = run_with_coverage()
    else:
        exit_code = run_all_tests()
    
    sys.exit(exit_code)


"""
===============================================================================
TESTING DOCUMENTATION
===============================================================================

## Setup Instructions

1. Install testing dependencies:
   ```bash
   pip install pytest pytest-cov coverage
   ```

2. Update your requirements.txt:
   ```
   pytest==7.4.3
   pytest-cov==4.1.0
   coverage==7.3.2
   ```

3. Create tests directory structure:
   ```
   levelup_flask/
   ├── app.py
   ├── models.py
   ├── forms.py
   ├── api_client.py
   ├── tests/
   │   ├── __init__.py
   │   ├── conftest.py
   │   ├── test_app.py
   │   └── test_app_pytest.py
   └── run_tests.py
   ```

## Running Tests

### Option 1: Using unittest
```bash
# Run all tests
python -m unittest discover tests -v

# Run specific test file
python -m unittest tests.test_app -v

# Run specific test class
python -m unittest tests.test_app.TestUserModel -v

# Run specific test method
python -m unittest tests.test_app.TestUserModel.test_user_creation -v
```

### Option 2: Using pytest
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_app_pytest.py -v

# Run specific test class
pytest tests/test_app_pytest.py::TestUserAuthentication -v

# Run specific test
pytest tests/test_app_pytest.py::TestUserAuthentication::test_user_login_success -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html --cov-report=term
```

### Option 3: Using the test runner script
```bash
# Run all tests
python run_tests.py

# Run with coverage report
python run_tests.py --coverage
```

## Test Coverage Goals

Aim for at least 80% code coverage across:
- Routes/Views: 90%+
- Models: 95%+
- Forms: 85%+
- Utilities: 80%+

## Continuous Integration

### GitHub Actions Example (.github/workflows/tests.yml)
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        pytest tests/ --cov=. --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

## Writing New Tests

### Test Structure
```python
class TestNewFeature(BaseTestCase):
    
    def test_feature_works(self):
        # Arrange - Set up test data
        user = self.create_user()
        
        # Act - Perform the action
        response = self.client.post('/new_feature', data={
            'field': 'value'
        })
        
        # Assert - Check the results
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Success', response.data)
```

### Best Practices
1. Use descriptive test names that explain what is being tested
2. Test one thing per test method
3. Use fixtures for common setup
4. Test both success and failure cases
5. Test edge cases and boundary conditions
6. Mock external API calls
7. Clean up test data after each test
8. Keep tests independent - each test should work on its own

## Test Categories

### Unit Tests
- Test individual functions and methods in isolation
- Fast to run
- High code coverage

### Integration Tests
- Test how different parts work together
- Test database interactions
- Test API integrations

### Functional Tests
- Test complete user workflows
- Test from user's perspective
- Simulate real usage patterns

## Debugging Failed Tests

```bash
# Run with detailed output
pytest tests/ -vv

# Run with print statements visible
pytest tests/ -s

# Stop at first failure
pytest tests/ -x

# Run last failed tests
pytest tests/ --lf

# Enter debugger on failure
pytest tests/ --pdb
```

## Mocking External Services

```python
from unittest.mock import patch, MagicMock

class TestAPIIntegration(BaseTestCase):
    
    @patch('api_client.requests.get')
    def test_api_call(self, mock_get):
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = {'data': 'test'}
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Test your code
        result = some_function_that_calls_api()
        
        # Assertions
        self.assertEqual(result, {'data': 'test'})
        mock_get.assert_called_once()
```

## Common Issues and Solutions

### Issue: Tests fail due to database conflicts
Solution: Use in-memory SQLite database for tests

### Issue: Tests are slow
Solution: Use smaller test datasets, mock external services

### Issue: Tests pass individually but fail together
Solution: Ensure proper cleanup in tearDown, avoid global state

### Issue: Import errors
Solution: Check PYTHONPATH and sys.path configuration

===============================================================================
"""