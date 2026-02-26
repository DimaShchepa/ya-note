from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        """
        Создаёт тестовые данные один раз для всех тестов класса
        """
        cls.author = User.objects.create(username='Автор')
        cls.other_user = User.objects.create_user(username='Не автор')
        cls.note = Note.objects.create(title='Заголовок',
                                       text='Текст',
                                       author=cls.author)
        cls.slug = cls.note.slug

    def test_home_page(self):
        """
        Главная страница доступна анонимному пользователю.
        """
        url = reverse('notes:home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability(self):
        """
        Проверяет, что аутентифицированный пользователь может открыть:
        - главную страницу;
        - страницу заметки;
        - список заметок;
        - страницу успешного добаврения заметки;
        - страницу добавления новой заметки;
        - страницу входа;
        - страницу регистрации.
        """
        self.client.force_login(self.author)

        urls = (
            ('notes:home', None),
            ('notes:detail', (self.slug,)),
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
            ('users:login', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_othet_user_cannot_access_pages(self):
        """
        Проверяется, что пользователь не может видеть чужие заметки,
        не может удалять и редактировать их - возвращается ошибка 404.
        """
        self.client.force_login(self.other_user)

        urls = (
            ('notes:detail', (self.slug,)),
            ('notes:edit', (self.slug,)),
            ('notes:delete', (self.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_anonymous_access(self):
        """
        При попытке анонимного пользователя, зайти на защищенные страницы,
        происходит редирект на страницу входа.
        """
        login_url = reverse('users:login')
        urls = (
            ('notes:detail', (self.slug,)),
            ('notes:edit', (self.slug,)),
            ('notes:delete', (self.slug,)),
        )
        for name, args in urls:
            url = reverse(name, args=args)
            redirect_url = f'{login_url}?next={url}'
            response = self.client.get(url)
            self.assertRedirects(response, redirect_url)
