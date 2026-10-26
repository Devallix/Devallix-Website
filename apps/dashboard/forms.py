from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Field, Submit, HTML, Div, ButtonHolder
from apps.desktop_apps.models import DesktopApplication, ApplicationVersion, ApplicationCategory
from apps.web_projects.models import WebProject
from apps.mobile_apps.models import MobileApp
from apps.graphic_design.models import GraphicDesignProject
from apps.portfolio.models import Skill, SkillCategory
from apps.blog.models import BlogPost
from apps.testimonials.models import Testimonial
from apps.core.models import SiteSettings


class DisplayOrderMixin:
    """Make display_order optional and default it to 0 for new objects."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        field = self.fields.get('display_order')
        if field is not None:
            field.required = False
            if not self.instance.pk:
                field.initial = 0

    def clean_display_order(self):
        return self.cleaned_data.get('display_order') or 0


class AppForm(forms.ModelForm):
    class Meta:
        model = DesktopApplication
        fields = [
            'name', 'category', 'short_description', 'description', 'version',
            'platform', 'license_type', 'file_size', 'release_date',
            'minimum_requirements', 'installation_instructions', 'logo', 'banner',
            'installer_file', 'zip_file', 'website_url', 'github_url',
            'featured', 'published', 'meta_title', 'meta_description',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'short_description': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'version': forms.TextInput(attrs={'class': 'form-control'}),
            'file_size': forms.TextInput(attrs={'class': 'form-control'}),
            'release_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'minimum_requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'installation_instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'website_url': forms.URLInput(attrs={'class': 'form-control'}),
            'github_url': forms.URLInput(attrs={'class': 'form-control'}),
            'meta_title': forms.TextInput(attrs={'class': 'form-control'}),
            'meta_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'platform': forms.Select(attrs={'class': 'form-select'}),
            'license_type': forms.Select(attrs={'class': 'form-select'}),
            'logo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'banner': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'installer_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'zip_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='col-md-8'),
                Column('version', css_class='col-md-4'),
            ),
            Row(
                Column('category', css_class='col-md-6'),
                Column('platform', css_class='col-md-3'),
                Column('license_type', css_class='col-md-3'),
            ),
            'short_description',
            'description',
            Row(
                Column('file_size', css_class='col-md-6'),
                Column('release_date', css_class='col-md-6'),
            ),
            HTML('<hr class="my-4" style="border-color:var(--border-color);">'),
            HTML('<h6 class="fw-bold mb-3" style="color:var(--accent);"><i class="fas fa-image me-2"></i>Media</h6>'),
            Row(
                Column('logo', css_class='col-md-6'),
                Column('banner', css_class='col-md-6'),
            ),
            Row(
                Column('installer_file', css_class='col-md-6'),
                Column('zip_file', css_class='col-md-6'),
            ),
            HTML('<hr class="my-4" style="border-color:var(--border-color);">'),
            HTML('<h6 class="fw-bold mb-3" style="color:var(--accent);"><i class="fas fa-cog me-2"></i>Requirements & Installation</h6>'),
            'minimum_requirements',
            'installation_instructions',
            HTML('<hr class="my-4" style="border-color:var(--border-color);">'),
            HTML('<h6 class="fw-bold mb-3" style="color:var(--accent);"><i class="fas fa-link me-2"></i>Links</h6>'),
            Row(
                Column('website_url', css_class='col-md-6'),
                Column('github_url', css_class='col-md-6'),
            ),
            HTML('<hr class="my-4" style="border-color:var(--border-color);">'),
            HTML('<h6 class="fw-bold mb-3" style="color:var(--accent);"><i class="fas fa-cog me-2"></i>Settings</h6>'),
            Row(
                Column('featured', css_class='col-auto'),
                Column('published', css_class='col-auto'),
            ),
            HTML('<hr class="my-4" style="border-color:var(--border-color);">'),
            HTML('<h6 class="fw-bold mb-3" style="color:var(--accent);"><i class="fas fa-search me-2"></i>SEO</h6>'),
            'meta_title',
            'meta_description',
            ButtonHolder(
                Submit('submit', 'Save Application', css_class='btn btn-accent mt-3')
            ),
        )


class VersionForm(forms.ModelForm):
    class Meta:
        model = ApplicationVersion
        fields = [
            'version_number', 'release_date', 'changes', 'release_notes',
            'installer_file', 'zip_file', 'file_size', 'is_current',
        ]
        widgets = {
            'version_number': forms.TextInput(attrs={'class': 'form-control'}),
            'release_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'changes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'release_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'installer_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'zip_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'file_size': forms.TextInput(attrs={'class': 'form-control'}),
            'is_current': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'is_current': 'Set as current version',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            Row(
                Column('version_number', css_class='col-md-6'),
                Column('release_date', css_class='col-md-6'),
            ),
            'changes',
            'release_notes',
            Row(
                Column('file_size', css_class='col-md-4'),
                Column('installer_file', css_class='col-md-4'),
                Column('zip_file', css_class='col-md-4'),
            ),
            Row(
                Column('is_current', css_class='col-auto'),
            ),
            ButtonHolder(
                Submit('submit', 'Save Version', css_class='btn btn-accent mt-3')
            ),
        )


class ProjectForm(forms.ModelForm):
    class Meta:
        model = WebProject
        fields = [
            'name', 'short_description', 'description', 'technologies',
            'image', 'live_demo_url', 'github_url', 'status', 'featured',
            'meta_title', 'meta_description',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'short_description': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'technologies': forms.CheckboxSelectMultiple(),
            'live_demo_url': forms.URLInput(attrs={'class': 'form-control'}),
            'github_url': forms.URLInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'meta_title': forms.TextInput(attrs={'class': 'form-control'}),
            'meta_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            'name',
            'short_description',
            'description',
            'technologies',
            Row(
                Column('image', css_class='col-md-6'),
                Column('status', css_class='col-md-6'),
            ),
            HTML('<hr class="my-4" style="border-color:var(--border-color);">'),
            HTML('<h6 class="fw-bold mb-3" style="color:var(--accent);"><i class="fas fa-link me-2"></i>Links</h6>'),
            Row(
                Column('live_demo_url', css_class='col-md-6'),
                Column('github_url', css_class='col-md-6'),
            ),
            HTML('<hr class="my-4" style="border-color:var(--border-color);">'),
            HTML('<h6 class="fw-bold mb-3" style="color:var(--accent);"><i class="fas fa-cog me-2"></i>Settings</h6>'),
            Row(
                Column('featured', css_class='col-auto'),
            ),
            HTML('<hr class="my-4" style="border-color:var(--border-color);">'),
            HTML('<h6 class="fw-bold mb-3" style="color:var(--accent);"><i class="fas fa-search me-2"></i>SEO</h6>'),
            'meta_title',
            'meta_description',
            ButtonHolder(
                Submit('submit', 'Save Project', css_class='btn btn-accent mt-3')
            ),
        )


class SkillForm(DisplayOrderMixin, forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['name', 'category', 'category_type', 'proficiency_level', 'icon', 'display_order', 'is_featured']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'category_type': forms.Select(attrs={'class': 'form-select'}),
            'proficiency_level': forms.Select(attrs={'class': 'form-select'}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. fab fa-python'}),
            'display_order': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'is_featured': 'Featured skill',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'name',
            Row(
                Column('category_type', css_class='col-md-6'),
                Column('category', css_class='col-md-6'),
            ),
            Row(
                Column('proficiency_level', css_class='col-md-6'),
                Column('display_order', css_class='col-md-6'),
            ),
            'icon',
            Row(
                Column('is_featured', css_class='col-auto'),
            ),
            ButtonHolder(
                Submit('submit', 'Save Skill', css_class='btn btn-accent mt-3')
            ),
        )


class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = [
            'title', 'category', 'tags', 'featured_image', 'excerpt',
            'content', 'status', 'featured', 'meta_title', 'meta_description',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'excerpt': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 8}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'tags': forms.CheckboxSelectMultiple(),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'featured_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'meta_title': forms.TextInput(attrs={'class': 'form-control'}),
            'meta_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        labels = {
            'featured': 'Featured post',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            'title',
            Row(
                Column('category', css_class='col-md-6'),
                Column('status', css_class='col-md-6'),
            ),
            'tags',
            'featured_image',
            'excerpt',
            'content',
            HTML('<hr class="my-4" style="border-color:var(--border-color);">'),
            HTML('<h6 class="fw-bold mb-3" style="color:var(--accent);"><i class="fas fa-cog me-2"></i>Settings</h6>'),
            Row(
                Column('featured', css_class='col-auto'),
            ),
            HTML('<hr class="my-4" style="border-color:var(--border-color);">'),
            HTML('<h6 class="fw-bold mb-3" style="color:var(--accent);"><i class="fas fa-search me-2"></i>SEO</h6>'),
            'meta_title',
            'meta_description',
            ButtonHolder(
                Submit('submit', 'Save Post', css_class='btn btn-accent mt-3')
            ),
        )


class TestimonialForm(DisplayOrderMixin, forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = [
            'client_name', 'company', 'position', 'image', 'review',
            'rating', 'featured', 'is_active', 'display_order',
        ]
        widgets = {
            'client_name': forms.TextInput(attrs={'class': 'form-control'}),
            'company': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'review': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'rating': forms.Select(attrs={'class': 'form-select'}),
            'display_order': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'is_active': 'Active',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            Row(
                Column('client_name', css_class='col-md-6'),
                Column('company', css_class='col-md-6'),
            ),
            'position',
            'review',
            Row(
                Column('rating', css_class='col-md-4'),
                Column('display_order', css_class='col-md-4'),
                Column('image', css_class='col-md-4'),
            ),
            Row(
                Column('featured', css_class='col-auto'),
                Column('is_active', css_class='col-auto'),
            ),
            ButtonHolder(
                Submit('submit', 'Save Testimonial', css_class='btn btn-accent mt-3')
            ),
        )


class CategoryForm(DisplayOrderMixin, forms.ModelForm):
    class Meta:
        model = ApplicationCategory
        fields = ['name', 'icon', 'description', 'display_order']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. fas fa-code'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'display_order': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'name',
            'icon',
            'description',
            'display_order',
            ButtonHolder(
                Submit('submit', 'Save Category', css_class='btn btn-accent mt-3')
            ),
        )


class SiteSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = [
            'site_name', 'site_tagline', 'logo', 'favicon',
            'hero_title', 'hero_subtitle', 'hero_cta_text', 'hero_cta_url',
            'about_image', 'footer_text',
            'email', 'phone', 'address',
            'github_url', 'linkedin_url', 'twitter_url', 'youtube_url', 'facebook_url', 'instagram_url',
            'meta_title', 'meta_description', 'meta_keywords', 'og_image',
            'google_analytics_code',
        ]
        widgets = {
            'site_name': forms.TextInput(attrs={'class': 'form-control'}),
            'site_tagline': forms.TextInput(attrs={'class': 'form-control'}),
            'hero_title': forms.TextInput(attrs={'class': 'form-control'}),
            'hero_subtitle': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'hero_cta_text': forms.TextInput(attrs={'class': 'form-control'}),
            'hero_cta_url': forms.TextInput(attrs={'class': 'form-control'}),
            'footer_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'github_url': forms.URLInput(attrs={'class': 'form-control'}),
            'linkedin_url': forms.URLInput(attrs={'class': 'form-control'}),
            'twitter_url': forms.URLInput(attrs={'class': 'form-control'}),
            'youtube_url': forms.URLInput(attrs={'class': 'form-control'}),
            'facebook_url': forms.URLInput(attrs={'class': 'form-control'}),
            'instagram_url': forms.URLInput(attrs={'class': 'form-control'}),
            'meta_title': forms.TextInput(attrs={'class': 'form-control'}),
            'meta_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'meta_keywords': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'google_analytics_code': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Paste GA code here...'}),
            'logo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'favicon': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'about_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'og_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            HTML('<h6 class="fw-bold mb-3" style="color:var(--accent);"><i class="fas fa-globe me-2"></i>General</h6>'),
            Row(
                Column('site_name', css_class='col-md-6'),
                Column('site_tagline', css_class='col-md-6'),
            ),
            Row(
                Column('logo', css_class='col-md-6'),
                Column('favicon', css_class='col-md-6'),
            ),
            HTML('<hr class="my-4" style="border-color:var(--border-color);">'),
            HTML('<h6 class="fw-bold mb-3" style="color:var(--accent);"><i class="fas fa-heading me-2"></i>Hero Section</h6>'),
            'hero_title',
            'hero_subtitle',
            Row(
                Column('hero_cta_text', css_class='col-md-6'),
                Column('hero_cta_url', css_class='col-md-6'),
            ),
            HTML('<hr class="my-4" style="border-color:var(--border-color);">'),
            HTML('<h6 class="fw-bold mb-3" style="color:var(--accent);"><i class="fas fa-image me-2"></i>About & Footer</h6>'),
            'about_image',
            'footer_text',
            HTML('<hr class="my-4" style="border-color:var(--border-color);">'),
            HTML('<h6 class="fw-bold mb-3" style="color:var(--accent);"><i class="fas fa-envelope me-2"></i>Contact Info</h6>'),
            Row(
                Column('email', css_class='col-md-6'),
                Column('phone', css_class='col-md-6'),
            ),
            'address',
            HTML('<hr class="my-4" style="border-color:var(--border-color);">'),
            HTML('<h6 class="fw-bold mb-3" style="color:var(--accent);"><i class="fas fa-share-alt me-2"></i>Social Links</h6>'),
            Row(
                Column('github_url', css_class='col-md-6'),
                Column('linkedin_url', css_class='col-md-6'),
            ),
            Row(
                Column('twitter_url', css_class='col-md-6'),
                Column('youtube_url', css_class='col-md-6'),
            ),
            Row(
                Column('facebook_url', css_class='col-md-6'),
                Column('instagram_url', css_class='col-md-6'),
            ),
            HTML('<hr class="my-4" style="border-color:var(--border-color);">'),
            HTML('<h6 class="fw-bold mb-3" style="color:var(--accent);"><i class="fas fa-search me-2"></i>SEO</h6>'),
            'meta_title',
            'meta_description',
            'meta_keywords',
            Row(
                Column('og_image', css_class='col-md-6'),
                Column('google_analytics_code', css_class='col-md-6'),
            ),
            ButtonHolder(
                Submit('submit', 'Save Settings', css_class='btn btn-accent mt-3')
            ),
        )


class MobileAppForm(DisplayOrderMixin, forms.ModelForm):
    class Meta:
        model = MobileApp
        fields = [
            'name', 'short_description', 'description', 'platform', 'technologies',
            'version', 'logo', 'image', 'play_store_url', 'app_store_url',
            'website_url', 'github_url', 'status', 'featured', 'display_order',
            'meta_title', 'meta_description',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'short_description': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'platform': forms.Select(attrs={'class': 'form-select'}),
            'technologies': forms.CheckboxSelectMultiple(),
            'version': forms.TextInput(attrs={'class': 'form-control'}),
            'logo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'play_store_url': forms.URLInput(attrs={'class': 'form-control'}),
            'app_store_url': forms.URLInput(attrs={'class': 'form-control'}),
            'website_url': forms.URLInput(attrs={'class': 'form-control'}),
            'github_url': forms.URLInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'display_order': forms.NumberInput(attrs={'class': 'form-control'}),
            'meta_title': forms.TextInput(attrs={'class': 'form-control'}),
            'meta_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='col-md-8'),
                Column('version', css_class='col-md-4'),
            ),
            Row(
                Column('platform', css_class='col-md-6'),
                Column('status', css_class='col-md-6'),
            ),
            'short_description',
            'description',
            'technologies',
            HTML('<hr class="my-4" style="border-color:var(--border-color);">'),
            HTML('<h6 class="fw-bold mb-3" style="color:var(--accent);"><i class="fas fa-image me-2"></i>Media</h6>'),
            Row(
                Column('logo', css_class='col-md-6'),
                Column('image', css_class='col-md-6'),
            ),
            HTML('<hr class="my-4" style="border-color:var(--border-color);">'),
            HTML('<h6 class="fw-bold mb-3" style="color:var(--accent);"><i class="fas fa-link me-2"></i>Links</h6>'),
            Row(
                Column('play_store_url', css_class='col-md-6'),
                Column('app_store_url', css_class='col-md-6'),
            ),
            Row(
                Column('website_url', css_class='col-md-6'),
                Column('github_url', css_class='col-md-6'),
            ),
            HTML('<hr class="my-4" style="border-color:var(--border-color);">'),
            HTML('<h6 class="fw-bold mb-3" style="color:var(--accent);"><i class="fas fa-cog me-2"></i>Settings</h6>'),
            Row(
                Column('featured', css_class='col-auto'),
                Column('display_order', css_class='col-md-3'),
            ),
            HTML('<hr class="my-4" style="border-color:var(--border-color);">'),
            HTML('<h6 class="fw-bold mb-3" style="color:var(--accent);"><i class="fas fa-search me-2"></i>SEO</h6>'),
            'meta_title',
            'meta_description',
            ButtonHolder(
                Submit('submit', 'Save Mobile App', css_class='btn btn-accent mt-3')
            ),
        )


class GraphicDesignForm(DisplayOrderMixin, forms.ModelForm):
    class Meta:
        model = GraphicDesignProject
        fields = [
            'name', 'category', 'short_description', 'description', 'image',
            'client', 'tools', 'project_url', 'featured', 'published',
            'display_order', 'meta_title', 'meta_description',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'short_description': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'client': forms.TextInput(attrs={'class': 'form-control'}),
            'tools': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Photoshop, Illustrator, Figma'}),
            'project_url': forms.URLInput(attrs={'class': 'form-control'}),
            'featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'display_order': forms.NumberInput(attrs={'class': 'form-control'}),
            'meta_title': forms.TextInput(attrs={'class': 'form-control'}),
            'meta_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='col-md-8'),
                Column('category', css_class='col-md-4'),
            ),
            'short_description',
            'description',
            HTML('<hr class="my-4" style="border-color:var(--border-color);">'),
            HTML('<h6 class="fw-bold mb-3" style="color:var(--accent);"><i class="fas fa-image me-2"></i>Media</h6>'),
            'image',
            HTML('<hr class="my-4" style="border-color:var(--border-color);">'),
            HTML('<h6 class="fw-bold mb-3" style="color:var(--accent);"><i class="fas fa-info-circle me-2"></i>Project Details</h6>'),
            Row(
                Column('client', css_class='col-md-6'),
                Column('tools', css_class='col-md-6'),
            ),
            'project_url',
            HTML('<hr class="my-4" style="border-color:var(--border-color);">'),
            HTML('<h6 class="fw-bold mb-3" style="color:var(--accent);"><i class="fas fa-cog me-2"></i>Settings</h6>'),
            Row(
                Column('featured', css_class='col-auto'),
                Column('published', css_class='col-auto'),
                Column('display_order', css_class='col-md-3'),
            ),
            HTML('<hr class="my-4" style="border-color:var(--border-color);">'),
            HTML('<h6 class="fw-bold mb-3" style="color:var(--accent);"><i class="fas fa-search me-2"></i>SEO</h6>'),
            'meta_title',
            'meta_description',
            ButtonHolder(
                Submit('submit', 'Save Design Project', css_class='btn btn-accent mt-3')
            ),
        )
