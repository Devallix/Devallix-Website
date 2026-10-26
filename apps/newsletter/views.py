from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import FormView
from .forms import NewsletterSubscribeForm
from .models import NewsletterSubscriber


class NewsletterSubscribeView(FormView):
    form_class = NewsletterSubscribeForm
    template_name = 'newsletter/subscribe.html'

    def form_valid(self, form):
        email = form.cleaned_data['email']
        subscriber, created = NewsletterSubscriber.objects.get_or_create(email=email)
        if created:
            messages.success(self.request, 'You have been subscribed successfully!')
        else:
            messages.info(self.request, 'You are already subscribed.')
        return redirect(self.request.META.get('HTTP_REFERER', 'core:home'))
