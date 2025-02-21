#!/usr/bin/env python3
"""
Test runner script with coverage reporting.
"""

import sys
import pytest
import coverage

def main():
    # Start coverage measurement
    cov = coverage.Coverage(
        branch=True,
        source=['src'],
        omit=['*/__init__.py']
    )
    cov.start()

    # Run tests
    result = pytest.main(['tests'])

    # Stop coverage measurement
    cov.stop()
    cov.save()

    # Report coverage
    print("\nCoverage Report:")
    cov.report()

    # Generate HTML report
    cov.html_report(directory='coverage_report')
    print("\nDetailed coverage report generated in coverage_report/index.html")

    # Return test result
    return result

if __name__ == '__main__':
    sys.exit(main()) 