from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from apps.blog.models import BlogPost, BlogCategory, Comment, PostLike

User = get_user_model()


class BlogCommentAndLikeTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.author = User.objects.create_user(
            username='blog_author',
            email='author@example.com',
            password='testpassword123',
            first_name='Author'
        )
        self.staff_user = User.objects.create_user(
            username='staff_mod',
            email='staff@example.com',
            password='testpassword123',
            is_staff=True
        )
        self.category = BlogCategory.objects.create(name='Tech', slug='tech')
        self.post = BlogPost.objects.create(
            title='Django Advanced Commenting and Liking',
            slug='django-advanced-commenting-and-liking',
            author=self.author,
            category=self.category,
            content='This is a detailed article explaining comments and likes.',
            status='published'
        )

    def test_comment_model_creation_and_defaults(self):
        comment = Comment.objects.create(
            post=self.post,
            name='Sarah Connor',
            body='Fantastic writeup on Django systems!'
        )
        self.assertTrue(comment.is_approved)
        self.assertIsNotNone(comment.created_at)
        self.assertEqual(comment.name, 'Sarah Connor')
        self.assertIsNone(comment.email)
        self.assertIn('Sarah Connor', str(comment))
        self.assertEqual(self.post.approved_comments_count, 1)

    def test_post_like_model_and_properties(self):
        self.assertEqual(self.post.likes_count, 0)
        like = PostLike.objects.create(
            post=self.post,
            session_key='test-session-key-12345',
            ip_address='127.0.0.1'
        )
        self.assertEqual(self.post.likes_count, 1)
        self.assertIn('Guest', str(like))

    def test_comment_submission_standard_post(self):
        url = reverse('blog:post_comment', kwargs={'slug': self.post.slug})
        response = self.client.post(url, {
            'name': 'John Doe',
            'body': 'Great article, thoroughly enjoyed reading it!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn(self.post.get_absolute_url(), response.url)

        self.assertEqual(Comment.objects.filter(post=self.post).count(), 1)
        comment = Comment.objects.get(post=self.post)
        self.assertEqual(comment.name, 'John Doe')
        self.assertEqual(comment.body, 'Great article, thoroughly enjoyed reading it!')
        self.assertTrue(comment.is_approved)
        self.assertIsNotNone(comment.created_at)

    def test_comment_submission_ajax_success(self):
        url = reverse('blog:post_comment', kwargs={'slug': self.post.slug})
        response = self.client.post(
            url,
            {'name': 'Jane Developer', 'body': 'This solved my immediate issue, thank you!'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['comment']['name'], 'Jane Developer')
        self.assertEqual(data['comment']['initial'], 'J')
        self.assertIn('2026', data['comment']['created_at'])
        self.assertIn('2026', data['comment']['date_short'])
        self.assertEqual(data['comments_count'], 1)

    def test_comment_submission_validation_errors(self):
        url = reverse('blog:post_comment', kwargs={'slug': self.post.slug})
        # Empty submission
        response = self.client.post(
            url,
            {'name': '', 'body': ''},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data['status'], 'error')
        self.assertIn('name', data['errors'])
        self.assertIn('body', data['errors'])

    def test_like_toggle_guest_user(self):
        url = reverse('blog:post_like_toggle', kwargs={'slug': self.post.slug})

        # First like (AJAX)
        response = self.client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertTrue(data['liked'])
        self.assertEqual(data['likes_count'], 1)
        self.assertEqual(PostLike.objects.filter(post=self.post).count(), 1)

        # Unlike (AJAX)
        response2 = self.client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response2.status_code, 200)
        data2 = response2.json()
        self.assertEqual(data2['status'], 'success')
        self.assertFalse(data2['liked'])
        self.assertEqual(data2['likes_count'], 0)
        self.assertEqual(PostLike.objects.filter(post=self.post).count(), 0)

    def test_like_toggle_authenticated_user(self):
        self.client.login(username='blog_author', password='testpassword123')
        url = reverse('blog:post_like_toggle', kwargs={'slug': self.post.slug})

        # Like
        response = self.client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['liked'])
        self.assertEqual(data['likes_count'], 1)

        like = PostLike.objects.get(post=self.post)
        self.assertEqual(like.user, self.author)

        # Unlike
        response = self.client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['liked'])
        self.assertEqual(data['likes_count'], 0)

    def test_post_detail_view_renders_comments_and_like_button(self):
        # Create comment and like
        Comment.objects.create(post=self.post, name='Alice Reader', body='Very insightful thoughts!')
        PostLike.objects.create(post=self.post, session_key='session-123')

        response = self.client.get(self.post.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Leave a Comment')
        self.assertContains(response, 'Alice Reader')
        self.assertContains(response, 'Very insightful thoughts!')
        self.assertContains(response, 'Like Article')
        self.assertContains(response, 'Comments &amp; Feedback')
        self.assertContains(response, 'id="like-btn"')
        self.assertContains(response, 'id="comment-post-form"')

    def test_dashboard_comment_moderation_views(self):
        comment = Comment.objects.create(
            post=self.post,
            name='Test Spammer',
            body='Visit my spam site for free gift cards!'
        )

        # Non-staff cannot access
        anon_response = self.client.get(reverse('dashboard:comment_list'))
        self.assertNotEqual(anon_response.status_code, 200)

        # Staff login
        self.client.login(username='staff_mod', password='testpassword123')

        # Staff can list comments
        list_response = self.client.get(reverse('dashboard:comment_list'))
        self.assertEqual(list_response.status_code, 200)
        self.assertContains(list_response, 'Test Spammer')
        self.assertContains(list_response, 'Visit my spam site')

        # Staff can toggle approval via AJAX
        toggle_url = reverse('dashboard:comment_toggle_approval', kwargs={'pk': comment.pk})
        toggle_res = self.client.post(toggle_url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(toggle_res.status_code, 200)
        comment.refresh_from_db()
        self.assertFalse(comment.is_approved)

        # Toggle back
        self.client.post(toggle_url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        comment.refresh_from_db()
        self.assertTrue(comment.is_approved)

        # Staff can delete comment
        delete_url = reverse('dashboard:comment_delete', kwargs={'pk': comment.pk})
        del_response = self.client.post(delete_url)
        self.assertEqual(del_response.status_code, 302)
        self.assertFalse(Comment.objects.filter(pk=comment.pk).exists())
