from unittest.mock import patch

from django.test import Client, TestCase
from django.urls import reverse

from .models import UserRelatorio


class FakeCursor:
    def __init__(self, fetchall_results):
        self.fetchall_results = list(fetchall_results)
        self.execute_calls = []
        self.closed = False

    def execute(self, query, params=None, **kwargs):
        self.execute_calls.append((query, params or kwargs or None))

    def fetchall(self):
        if not self.fetchall_results:
            return []
        return self.fetchall_results.pop(0)

    def close(self):
        self.closed = True


class FakeConnection:
    def __init__(self, cursor):
        self._cursor = cursor
        self.closed = False

    def cursor(self):
        return self._cursor

    def close(self):
        self.closed = True


class RelatorioViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserRelatorio.objects.create(
            username='relatorio',
            password='senha',
            ativo=True,
        )
        session = self.client.session
        session['relatorio_user_id'] = self.user.id
        session.save()

    def test_relatorio_renderiza_quantidades_de_reposicao(self):
        fake_cursor = FakeCursor([
            [('Maria da Silva', 101)],
            [(
                55,
                '{"1":"Maria"}',
                '2026-05-11',
                '08:30',
                2,
                'Observacao',
                1,
                'Sala 1',
                'UTI',
                7,
                'S',
                'S',
                'N',
                'NA',
                'S',
                'S',
                'N',
                3,
                2,
                1,
                4,
            )],
        ])
        fake_connection = FakeConnection(fake_cursor)

        with patch('registro.views.get_oracle_connection', return_value=fake_connection):
            response = self.client.get(reverse('relatorio_view'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<td class="d-none">3</td>', html=True)
        self.assertContains(response, '<td class="d-none">2</td>', html=True)
        self.assertContains(response, '<td class="d-none">1</td>', html=True)
        self.assertContains(response, '<td class="d-none">4</td>', html=True)

        registro = response.context['registros'][0]
        self.assertEqual(registro['papel_hig'], 3)
        self.assertEqual(registro['papel_toalha'], 2)
        self.assertEqual(registro['alcool'], 1)
        self.assertEqual(registro['sabonete'], 4)
