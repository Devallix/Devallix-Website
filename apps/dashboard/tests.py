from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from apps.blog.models import BlogPost, BlogCategory

User = get_user_model()


class BlogCategoryDashboardTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.staff_user = User.objects.create_user(
            username='staff_test',
            email='staff@example.com',
            password='testpassword123',
            is_staff=True
        )
        self.regular_user = User.objects.create_user(
            username='regular_test',
            email='regular@example.com',
            password='testpassword123',
            is_staff=False
        )
        self.client.login(username='staff_test', password='testpassword123')

    def test_blog_category_slug_generation_and_uniqueness(self):
        cat1 = BlogCategory.objects.create(name='Artificial Intelligence')
        self.assertEqual(cat1.slug, 'artificial-intelligence')

        cat2 = BlogCategory.objects.create(name='Artificial Intelligence')
        self.assertEqual(cat2.slug, 'artificial-intelligence-1')

    def test_blog_category_list_view_staff_only(self):
        cat = BlogCategory.objects.create(name='Tech News', description='All tech news')
        response = self.client.get(reverse('dashboard:blog_category_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tech News')
        self.assertContains(response, 'New Category')
        self.assertContains(response, 'Create Blog Category')

        # Check blog_list view has "Create Category" button
        blog_list_response = self.client.get(reverse('dashboard:blog_list'))
        self.assertEqual(blog_list_response.status_code, 200)
        self.assertContains(blog_list_response, 'Create Category')
        self.assertContains(blog_list_response, 'Manage Categories')

        # Regular user should be forbidden / redirected
        self.client.logout()
        self.client.login(username='regular_test', password='testpassword123')
        response = self.client.get(reverse('dashboard:blog_category_list'))
        self.assertNotEqual(response.status_code, 200)

    def test_blog_category_create_standard_post(self):
        response = self.client.post(reverse('dashboard:blog_category_create'), {
            'name': 'Cloud Computing',
            'description': 'Articles about cloud',
            'display_order': 1,
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(BlogCategory.objects.filter(name='Cloud Computing').exists())

    def test_blog_category_create_ajax_post(self):
        response = self.client.post(
            reverse('dashboard:blog_category_create'),
            {
                'name': 'Cybersecurity',
                'description': 'Security tutorials',
                'display_order': 2,
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get('success'))
        self.assertEqual(data.get('name'), 'Cybersecurity')
        self.assertEqual(data.get('slug'), 'cybersecurity')
        self.assertTrue(BlogCategory.objects.filter(name='Cybersecurity').exists())

    def test_blog_category_create_ajax_validation_error(self):
        # Empty name should fail validation
        response = self.client.post(
            reverse('dashboard:blog_category_create'),
            {'name': ''},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data.get('success'))
        self.assertIn('name', data.get('errors', {}))

    def test_blog_category_update_and_delete(self):
        cat = BlogCategory.objects.create(name='Data Science')
        edit_url = reverse('dashboard:blog_category_edit', kwargs={'pk': cat.pk})
        response = self.client.post(edit_url, {
            'name': 'Advanced Data Science',
            'description': 'Updated description',
            'display_order': 5
        })
        self.assertEqual(response.status_code, 302)
        cat.refresh_from_db()
        self.assertEqual(cat.name, 'Advanced Data Science')

        delete_url = reverse('dashboard:blog_category_delete', kwargs={'pk': cat.pk})
        del_response = self.client.post(delete_url)
        self.assertEqual(del_response.status_code, 302)
        self.assertFalse(BlogCategory.objects.filter(pk=cat.pk).exists())

    def test_blog_list_category_filtering(self):
        cat_ai = BlogCategory.objects.create(name='AI')
        cat_web = BlogCategory.objects.create(name='Web')

        post1 = BlogPost.objects.create(
            title='AI Advances',
            author=self.staff_user,
            category=cat_ai,
            status='published'
        )
        post2 = BlogPost.objects.create(
            title='Web Frameworks',
            author=self.staff_user,
            category=cat_web,
            status='published'
        )

        # Filter by AI
        response = self.client.get(reverse('dashboard:blog_list') + f'?category={cat_ai.slug}')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AI Advances')
        self.assertNotContains(response, 'Web Frameworks')

        # Filter by Web
        response = self.client.get(reverse('dashboard:blog_list') + f'?category={cat_web.slug}')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Web Frameworks')
        self.assertNotContains(response, 'AI Advances')

    def test_blog_post_form_recent_and_trending_checkboxes(self):
        cat = BlogCategory.objects.create(name='DevOps')
        response = self.client.post(reverse('dashboard:blog_create'), {
            'title': 'Docker Containerization Guide',
            'category': cat.id,
            'content': 'Comprehensive guide on Docker containerization best practices.',
            'status': 'published',
            'is_recent': True,
            'is_trending': True,
        })
        self.assertEqual(response.status_code, 302)
        post = BlogPost.objects.get(title='Docker Containerization Guide')
        self.assertTrue(post.is_recent)
        self.assertTrue(post.is_trending)

    def test_blog_detail_sidebar_sections_and_exclusion(self):
        cat = BlogCategory.objects.create(name='Tech')

        # Current post (also marked is_recent and is_trending to test self-exclusion)
        current_post = BlogPost.objects.create(
            title='Current Active Post',
            content='Content for current active post.',
            author=self.staff_user,
            category=cat,
            status='published',
            is_recent=True,
            is_trending=True,
        )

        # Another recent post
        recent_post = BlogPost.objects.create(
            title='Brand New Release Post',
            content='Description of brand new release.',
            author=self.staff_user,
            category=cat,
            status='published',
            is_recent=True,
            is_trending=False,
        )

        # Another trending post
        trending_post = BlogPost.objects.create(
            title='Super Popular Viral Article',
            content='Viral trends and news.',
            author=self.staff_user,
            category=cat,
            status='published',
            is_recent=False,
            is_trending=True,
            views_count=500,
        )

        # Regular post not marked for either
        plain_post = BlogPost.objects.create(
            title='Unmarked Ordinary Article',
            content='Just ordinary text.',
            author=self.staff_user,
            category=cat,
            status='published',
            is_recent=False,
            is_trending=False,
        )

        response = self.client.get(current_post.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        # Both sidebar sections should be visible
        self.assertContains(response, 'Trending / Must Read')
        self.assertContains(response, 'Recent Articles')

        # Trending and Recent articles should be present with links
        self.assertContains(response, 'Super Popular Viral Article')
        self.assertContains(response, 'Brand New Release Post')
        self.assertContains(response, trending_post.get_absolute_url())
        self.assertContains(response, recent_post.get_absolute_url())

        # Unmarked post should not appear in either sidebar section
        self.assertNotIn(plain_post, response.context['recent_articles'])
        self.assertNotIn(plain_post, response.context['trending_articles'])

        # Current post should NOT appear in the sidebar list (self-exclusion)
        # Check context
        self.assertNotIn(current_post, response.context['recent_articles'])
        self.assertNotIn(current_post, response.context['trending_articles'])
        self.assertIn(recent_post, response.context['recent_articles'])
        self.assertIn(trending_post, response.context['trending_articles'])

    def test_blog_detail_sidebar_hides_when_no_articles_marked(self):
        cat = BlogCategory.objects.create(name='Design')
        post = BlogPost.objects.create(
            title='UI/UX Principles',
            content='Clean design principles.',
            author=self.staff_user,
            category=cat,
            status='published',
            is_recent=False,
            is_trending=False,
        )

        response = self.client.get(post.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        # Sections should be completely hidden when 0 articles are marked
        self.assertNotContains(response, 'Trending / Must Read')
        self.assertNotContains(response, 'Recent Articles')
