import unittest
from openmailer.client import OpenMailerClient
from openmailer.template_engine import render_template
from openmailer.config import SMTP_CONFIG

class TestRealEmail(unittest.TestCase):

    def test_send_real_email(self):
        client = OpenMailerClient(config=SMTP_CONFIG)

        html = """
        <html>
          <body>
            <h1>Hello {{name}}</h1>
            <p>This is a test email from OpenMailer.</p>
          </body>
        </html>
        """

        html_rendered = render_template(html, {"name": "TestUser"})

        result = client.send_email(
            to="example@example",  # Replace with valid recipient
            subject="OpenMailer Test Email",
            html_body=html_rendered
        )

        self.assertEqual(result["status"], "sent")

if __name__ == "__main__":
    unittest.main()

