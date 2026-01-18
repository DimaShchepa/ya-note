from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.http import HttpResponseRedirect
from django.urls import reverse

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
                                       author=cls.author)
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

    def test_anonymous_user_cant_create_notes(self):
        response = self.client.post(self.ADD_URL)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertTrue(response.url.startswith(LOGIN_URL))

    def test_authorized_user_can_create_notes(self):
        self.author_client.post(self.ADD_URL,
                                data={'text': 'Текст заметки',
                                      'title': 'Заголовок заметки'})
        note_count = Note.objects.count()
        self.assertEqual(note_count, 2)


class TestNoteEdit(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.note = Note.objects.create(title='Заголовок',
                                       text='Текст',
                                       author=cls.author,
                                       )
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.slug = cls.note.slug
        cls.edit_url = reverse('notes:edit', args=(cls.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.slug,))
        cls.list_url = reverse('notes:list')

    def test_anonymous_user_cant_edit_notes(self):
        response = self.client.post(self.edit_url)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertTrue(response.url.startswith(LOGIN_URL))

    def test_autorized_user_can_edit_notes(self):
        new_title = 'Изменённый заголовок'
        new_text = 'Изменённый текст'
        self.author_client.post(self.edit_url,
                                data={'title': new_title,
                                      'text': new_text})

        updated_note = Note.objects.get(author=self.author, id=self.note.id)
        self.assertEqual(updated_note.title, new_title)
        self.assertEqual(updated_note.text, new_text)
        self.assertEqual(updated_note.author, self.author)

    def test_anonymous_user_cant_delete_notes(self):
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertTrue(response.url.startswith(LOGIN_URL))

    def test_autorized_user_can_delete_notes(self):
        response = self.author_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 0)
