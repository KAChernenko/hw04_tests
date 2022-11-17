from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post_author = User.objects.create_user(
            username='post_author',
        )
        cls.another_user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test_slug',
            description='Тестовое описание группы',
        )
        cls.edited_group = Group.objects.create(
            title='Название группы после редактирования',
            slug='test-edited',
            description='Тестовое описание группы после редактирования'
        )
        cls.post = Post.objects.create(
            author=cls.post_author,
            text='Тестовый текст для поста',
            group=cls.group,
        )

    def setUp(self):
        self.guest_user = Client()
        self.authorized_user = Client()
        self.authorized_user.force_login(self.post_author)

    def test_authorized_user_create_post(self):
        """Проверка создания записи авторизированным пользователем"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст поста',
            'group': self.group.id,
        }
        response = self.authorized_user.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': self.post_author.username})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        post = Post.objects.latest('id')
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.post_author)
        self.assertEqual(post.group_id, form_data['group'])

    def test_no_create_post(self):
        """Проверка запрета добавления поста в базу данных
           неавторизованым пользователем"""
        posts_count = Post.objects.count()
        form_data = {'text': 'Текст поста',
                     'group': self.group.id}
        response = self.guest_user.post(reverse('posts:post_create'),
                                        data=form_data,
                                        follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        error = 'Поcт добавлен в базу данных по ошибке'
        self.assertNotEqual(Post.objects.count(),
                            posts_count + 1,
                            error)

    def test_authorized_user_edit_post(self):
        """Проверка редактирования записи авторизированным пользователем"""
        form_data = {
            'text': 'Отредактированный текст поста',
            'group': self.group.id
        }
        response = self.authorized_user.post(
            reverse(
                'posts:post_edit',
                args=[self.post.id]),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        post = Post.objects.latest('id')
        self.assertEqual(post.author, self.post_author)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group_id, form_data['group'])

    def test_no_edit_post(self):
        """Проверка запрета редактирования неавторизованным пользователем"""
        posts_count = Post.objects.count()
        form_data = {'text': 'Отредактированный текст поста',
                     'group': self.edited_group.id
                     }
        response = self.guest_user.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        error = 'Поcт добавлен в базу данных ошибочно'
        self.assertNotEqual(Post.objects.count(),
                            posts_count + 1,
                            error)
        edited_post = Post.objects.get(id=self.post.id)
        self.assertNotEqual(edited_post.text, form_data['text'])
        self.assertNotEqual(edited_post.group.id, form_data['group'])

    def test_form_post_edit_post_by_noname(self):
        """Проверка запрета редактирования не автором поста"""
        posts_count = Post.objects.count()
        form_data = {'text': 'Отредактированный текст поста',
                     'group': self.edited_group.id
                     }
        self.authorized_user.force_login(self.another_user)
        response = self.authorized_user.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(Post.objects.count(), posts_count)
        edited_post = Post.objects.get(id=self.post.id)
        self.assertNotEqual(edited_post.text, form_data['text'])
        self.assertNotEqual(edited_post.group.id, form_data['group'])
