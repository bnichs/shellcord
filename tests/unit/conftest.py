import logging


def pytest_sessionfinish(session, exitstatus):
    """ whole test run finishes. """
    rootlogger = logging.getLogger()
    fpaths = [h.baseFilename for h in rootlogger.handlers if isinstance(h, logging.FileHandler)]

    print(f"Finished test run, logs are at: {fpaths}")

