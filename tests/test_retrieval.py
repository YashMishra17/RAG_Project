from app.retrieval import generate_response, query_system

def test_generate_response_demo():
    resp = generate_response(["chunk one", "chunk two"], "test query")
    assert isinstance(resp, str)
    assert "DEMO" in resp or len(resp) > 0

def test_query_system_empty_index():
    res = query_system("something")
    assert isinstance(res, list)
