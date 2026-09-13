import json
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from accounts.models import User, UserRole
from assistant.models import DocumentChunk
from assistant.rag import cosine_similarity, rank_chunks
from core.ollama_client import OllamaError


def json_post(client, url, data):
    return client.post(url, data=json.dumps(data), content_type="application/json")


class RagRankingTests(TestCase):
    def setUp(self):
        self.close_chunk = DocumentChunk.objects.create(
            document_slug="library-clearance", document_title="Library Clearance",
            chunk_index=0, content="Return your books.", embedding=[1, 0, 0],
        )
        self.far_chunk = DocumentChunk.objects.create(
            document_slug="treasurer-clearance", document_title="Treasurer Clearance",
            chunk_index=0, content="Settle your fees.", embedding=[0, 1, 0],
        )

    def test_cosine_similarity_of_identical_vectors_is_one(self):
        self.assertAlmostEqual(cosine_similarity([1, 0, 0], [1, 0, 0]), 1.0)

    def test_cosine_similarity_of_orthogonal_vectors_is_zero(self):
        self.assertAlmostEqual(cosine_similarity([1, 0, 0], [0, 1, 0]), 0.0)

    def test_rank_chunks_orders_by_similarity_descending(self):
        ranked = rank_chunks(question_embedding=[1, 0, 0], top_k=2)
        self.assertEqual([chunk.id for _, chunk in ranked], [self.close_chunk.id, self.far_chunk.id])


class ChatViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="student@demo.test", password="password", name="Juan", role=UserRole.STUDENT
        )
        DocumentChunk.objects.create(
            document_slug="library-clearance", document_title="Library Clearance",
            chunk_index=0, content="Return your books.", embedding=[1, 0, 0],
        )

    def test_requires_login(self):
        response = json_post(self.client, reverse("assistant.chat"), {"message": "hi"})
        self.assertEqual(response.status_code, 302)

    def test_requires_a_message(self):
        self.client.force_login(self.user)
        response = json_post(self.client, reverse("assistant.chat"), {"message": "  "})
        self.assertEqual(response.status_code, 400)

    @patch("assistant.views.generate", return_value="You need to return your books.")
    @patch("assistant.views.embed", return_value=[1, 0, 0])
    def test_chat_ranks_by_similarity_and_cites_sources(self, mock_embed, mock_generate):
        self.client.force_login(self.user)
        response = json_post(self.client, reverse("assistant.chat"), {"message": "library clearance?"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["answer"], "You need to return your books.")
        self.assertEqual(data["sources"][0]["title"], "Library Clearance")

    @patch("assistant.views.embed", side_effect=OllamaError("unreachable"))
    def test_chat_returns_503_when_ollama_is_unreachable(self, mock_embed):
        self.client.force_login(self.user)
        response = json_post(self.client, reverse("assistant.chat"), {"message": "hi"})
        self.assertEqual(response.status_code, 503)


class StatusViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="student@demo.test", password="password", name="Juan", role=UserRole.STUDENT
        )

    def test_requires_login(self):
        response = self.client.get(reverse("assistant.status"))
        self.assertEqual(response.status_code, 302)

    @patch("assistant.views.is_available", return_value=True)
    def test_reports_connected(self, mock_is_available):
        self.client.force_login(self.user)
        response = self.client.get(reverse("assistant.status"))
        self.assertEqual(response.json(), {"connected": True})

    @patch("assistant.views.is_available", return_value=False)
    def test_reports_disconnected(self, mock_is_available):
        self.client.force_login(self.user)
        response = self.client.get(reverse("assistant.status"))
        self.assertEqual(response.json(), {"connected": False})
