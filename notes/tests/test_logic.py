from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.http import HttpResponseRedirect
from django.urls import reverse
from pytils.translit import slugify

from notes.models import Note

User = get_user_model()
LOGIN_URL = reverse('users:login')


class TestNoteCreating(TestCase):
    ADD_URL = reverse('notes:add')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.note = Note.objects.create(title='Заголовок',
                                       text='Текст',
                                       author=cls.author,
                                       slug='unique-slug')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

    def test_anonymous_user_cant_create_notes(self):
        """
        Анонимный пользователь не может создавать свои заметки.
        Его переносит на страницу логина.
        """
        response = self.client.post(self.ADD_URL)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertTrue(response.url.startswith(LOGIN_URL))

    def test_authorized_user_can_create_notes(self):
        """
        Авторизованный пользователь может создавать свои заметки.
        """
        self.author_client.post(self.ADD_URL,
                                data={'text': 'Текст заметки',
                                      'title': 'Заголовок заметки'})
        note_count = Note.objects.count()
        self.assertEqual(note_count, 2)

    def test_connot_create_note_with_dublicate_slug(self):
        """
        Создание заметки с уже существующим slug не допустимо.
        """
        self.author_client.post(self.ADD_URL,
                                data={
                                      'title': 'Вторая заметка',
                                      'text': 'Содержание второй заметки',
                                      'slug': 'unique-slug',
                                })
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

    def test_autocreate_slug(self):
        """
        Проверяет, что уникальный slug заполняется автоматически.
        """
        self.author_client.post(self.ADD_URL,
                                data={
                                      'title': 'Вторая заметка',
                                      'text': 'Содержание второй заметки',
                                })
        note_count = Note.objects.count()
        self.assertEqual(note_count, 2)

        created_note = Note.objects.filter(title='Вторая заметка').first()
        expected_slug = slugify('Вторая заметка')
        self.assertEqual(created_note.slug, expected_slug)


class TestNoteEdit(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.not_author = User.objects.create(username='Не автор')
        cls.note = Note.objects.create(title='Заголовок',
                                       text='Текст',
                                       author=cls.author,
                                       slug='author-note'
                                       )
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.other_user_client = Client()
        cls.other_user_client.force_login(cls.not_author)
        cls.slug = cls.note.slug
        cls.edit_url = reverse('notes:edit', args=(cls.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.slug,))
        cls.list_url = reverse('notes:list')

    def test_other_user_cant_edit_notes(self):
        """
        Пользователь не может редактировать чужие заметки.
        """
        new_title = 'Изменённый заголовок'
        new_text = 'Изменённый текст'
        self.other_user_client.post(self.edit_url,
                                    data={'title': new_title,
                                          'text': new_text,
                                          'slug': 'author-note'})

        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

        unchanged_note = Note.objects.get(slug='author-note')
        self.assertEqual(unchanged_note.title, 'Заголовок')
        self.assertEqual(unchanged_note.text, 'Текст')

    def test_autorized_user_can_edit_notes(self):
        """
        Автор может редактировать свои заметки.
        """
        new_title = 'Изменённый заголовок'
        new_text = 'Изменённый текст'
        self.author_client.post(self.edit_url,
                                data={'title': new_title,
                                      'text': new_text})

        updated_note = Note.objects.get(author=self.author, id=self.note.id)
        self.assertEqual(updated_note.title, new_title)
        self.assertEqual(updated_note.text, new_text)
        self.assertEqual(updated_note.author, self.author)

    def test_other_user_cant_delete_notes(self):
        """
        Пользователь не может удалять чужие заметки.
        """
        response = self.other_user_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_autorized_user_can_delete_notes(self):
        """
        Автор может удалять свои заметки.
        """
        response = self.author_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 0)
