from django.views.generic import ListView
from .models import Testimonial


class TestimonialListView(ListView):
    model = Testimonial
    template_name = 'testimonials/testimonial_list.html'
    context_object_name = 'testimonials'
    paginate_by = 12

    def get_queryset(self):
        return Testimonial.objects.filter(is_active=True)
