from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import FormView, TemplateView
from .forms import ContactForm
from .models import ContactMessage


class ContactView(FormView):
    form_class = ContactForm
    template_name = 'contact/contact.html'
    success_url = '/contact/'

    def form_valid(self, form):
        ip = self.request.META.get('REMOTE_ADDR')
        ContactMessage.objects.create(
            name=form.cleaned_data['name'],
            email=form.cleaned_data['email'],
            subject=form.cleaned_data['subject'],
            message=form.cleaned_data['message'],
            ip_address=ip,
        )
        messages.success(self.request, 'Your message has been sent successfully. We will get back to you soon!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Contact Us'
        return context
