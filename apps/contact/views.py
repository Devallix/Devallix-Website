import logging

from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.shortcuts import redirect
from django.views.generic import FormView, TemplateView

from .forms import ContactForm
from .models import ContactMessage

logger = logging.getLogger(__name__)


class ContactView(FormView):
    form_class = ContactForm
    template_name = 'contact/contact.html'
    success_url = '/contact/'

    def form_valid(self, form):
        ip = self.request.META.get('REMOTE_ADDR')
        contact_message = ContactMessage.objects.create(
            name=form.cleaned_data['name'],
            email=form.cleaned_data['email'],
            subject=form.cleaned_data['subject'],
            message=form.cleaned_data['message'],
            ip_address=ip,
        )

        if self._send_notification(contact_message):
            messages.success(self.request, 'Your message has been sent successfully. We will get back to you soon!')
        else:
            messages.warning(
                self.request,
                'Your message was saved, but the email notification could not be '
                'delivered right now. We will still receive and review it.',
            )

        return super().form_valid(form)

    def _send_notification(self, contact_message):
        """Email the site owner about a new contact message.

        Returns True when the notification was sent, False otherwise. The
        message is always stored in the dashboard inbox regardless.
        """
        recipient = settings.DEFAULT_FROM_EMAIL
        if not recipient:
            logger.error(
                'Contact notification not sent: configure an email in Site Settings '
                'or set DEFAULT_FROM_EMAIL.'
            )
            return False

        body = (
            f'You have received a new message through the website contact form.\n\n'
            f'Name: {contact_message.name}\n'
            f'Email: {contact_message.email}\n'
            f'Subject: {contact_message.subject}\n\n'
            f'Message:\n{contact_message.message}\n'
        )

        email = EmailMessage(
            subject=f'[Website Contact] {contact_message.subject}',
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient],
            reply_to=[contact_message.email],
        )

        try:
            email.send(fail_silently=False)
        except Exception:
            logger.exception('Failed to send contact form notification email.')
            return False
        return True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Contact Us'
        return context
