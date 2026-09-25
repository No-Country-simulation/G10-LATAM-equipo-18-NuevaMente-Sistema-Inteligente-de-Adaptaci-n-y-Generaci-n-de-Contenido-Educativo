import pytest
from unittest.mock import patch, MagicMock
from app.services.graph_rag_service import GraphRAGService

@patch("app.services.graph_rag_service.genai.Client")
def test_graph_rag_gemini_success(mock_client):
    service = GraphRAGService()
    
    # Mocking la respuesta de Gemini
    mock_response = MagicMock()
    mock_response.text = '{"nodes": [{"id": "NodeA"}], "edges": []}'
    mock_client.return_value.models.generate_content.return_value = mock_response
    
    json_data, concepts, pre_reqs = service.build_concept_dag("Este es un texto sobre NodeA.")
    
    assert "NodeA" in json_data
    assert len(concepts) > 0

@patch("app.services.graph_rag_service.EmbeddingService")
@patch("app.services.graph_rag_service.genai.Client")
def test_graph_rag_fallback_jina(mock_client, mock_embedding_class):
    service = GraphRAGService()
    
    # Hacemos que Gemini arroje excepción para forzar el fallback
    mock_client.return_value.models.generate_content.side_effect = Exception("API Falló")
    
    # Mockeamos EmbeddingService de Jina
    mock_jina_instance = MagicMock()
    mock_jina_instance.embed_text.return_value = [0.1, 0.2]
    mock_jina_instance.embed_batch.return_value = [[0.1, 0.2], [0.9, 0.1]]
    mock_embedding_class.return_value = mock_jina_instance
    
    texto_largo = "Hola mundo. Programacion Avanzada en Python y OCI."
    json_data, concepts, pre_reqs = service.build_concept_dag(texto_largo)
    
    # El fallback no arroja excepción, devuelve algo básico o los conceptos extraídos
    assert isinstance(json_data, str)
    # Verifica que el fallback intentó usar Jina Embedding (embed_text y embed_batch)
    mock_jina_instance.embed_text.assert_called_once()
    mock_jina_instance.embed_batch.assert_called_once()
