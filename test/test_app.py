import unittest

from github_issue_adapter.adapter import app


class AppTest(unittest.TestCase):
    """
    This test allows you to manually run the adapter for testing.
    """


    def test_app(self):
        app.lambda_handler(None, None)


if __name__ == '__main__':
    unittest.main()
