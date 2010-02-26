from django.conf import settings
from django.test.simple import run_tests as django_test_runner
import coverage
def test_runner_with_coverage(test_labels, verbosity=1, interactive=True,
                              extra_tests=[], failfast=None):
    """
    Custom test runner.  Follows the django.test.simple.run_tests() interface.
    """
    # Start code coverage before anything else if necessary
    if hasattr(settings, 'COVERAGE_MODULES'):
        cov = coverage.coverage()
        #coverage.use_cache(0) # Do not cache any of the coverage.py stuff
        cov.use_cache(0) # Do not cache any of the coverage.py stuff
        cov.start()

    test_results = django_test_runner(test_labels, 
                                      verbosity=verbosity, 
                                      interactive=interactive, 
                                      extra_tests=extra_tests,
                                      failfast=failfast)

    # Stop code coverage after tests have completed
    if hasattr(settings, 'COVERAGE_MODULES'):
        cov.stop()

    # Print code metrics header
    print ''
    print '----------------------------------------------------------------------'
    print ' Unit Test Code Coverage Results'
    print '----------------------------------------------------------------------'

    # Report code coverage metrics
    if hasattr(settings, 'COVERAGE_MODULES'):
        coverage_modules = []
        for module in settings.COVERAGE_MODULES:
            coverage_modules.append(__import__(module, globals(), locals(), ['']))
        cov.report(coverage_modules, show_missing=1)
        #cov.html_report(coverage_modules, directory='coverage_report')
        # Print code metrics footer
        print '----------------------------------------------------------------------'

    return test_results
