import unittest

def all_tests_modules():
    modules = [
            "execconf.tests.test_utils",
            "execconf.tests.test_config",
            "execconf.tests.test_validator_nodes",
            "execconf.tests.test_validator",
            "execconf.tests.test_builder",
            "execconf.tests.test_loader"
        ]
    return modules


def all_tests_suite():
    suite = unittest.TestLoader().loadTestsFromNames(all_tests_modules())
    return suite

def main():
    from os import path
    import sys

    append_path = path.normpath(path.join(path.dirname(path.abspath(__file__)),
                                          "../.."))
    sys.path.insert(0, append_path)

    runner = unittest.TextTestRunner(verbosity=2)
    suite = all_tests_suite()
    raise SystemExit(not runner.run(suite).wasSuccessful())

def run():
    runner = unittest.TextTestRunner(verbosity=2)
    suite = all_tests_suite()
    return runner.run(suite).wasSuccessful()

if __name__ == '__main__':
    main()

