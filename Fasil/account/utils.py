from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def send_custom_email(subject, template, receivers):
    from_email = settings.DEFAULT_FROM_EMAIL  # Change this to your sender email address

    # Load the email template
    message = render_to_string(template, {'context_variable': 'value'})  # Pass any context variables needed in your template

    # Create a plain text version of the email (for clients that don't support HTML emails)
    plain_message = strip_tags(message)

    # Send the email
    send_mail(
        subject,
        plain_message,
        from_email,
        receivers,
        html_message=message,
    )
