from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

    HOME_URL = reverse('notes:home')
    LIST_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')

        cls.note = Note.objects.create(title='Заметка',
                                       text='Текст',
                                       author=cls.author,)

    def test_authorized_client_sees_all_their_own_notes(self):
        """
        Проверяет, что авторизованный пользователь видит свои заметки в списке.
        """
        self.client.force_login(self.author)
        response = self.client.get(self.LIST_URL)

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_anonymous_can_access_home(self):
        """
        Проверяет, что неавторизованный пользователь
        может открыть главную страницу.
        """
        response = self.client.get(self.HOME_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_note_page_contains_form(self):
        """
        Проверяет, что на страницу редактирования заметки передаётся форма
        с данными заметки.
        """
        self.client.force_login(self.author)
        url = reverse('notes:edit', kwargs={'slug': self.note.slug})
        response = self.client.get(url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
