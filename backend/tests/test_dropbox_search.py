from app.services.dropbox_search import search_similar_files

def test_dropbox_search_no_token():
    res = search_similar_files("er_sol_rou_14kw.3dm")
    assert isinstance(res, list) and len(res) >= 1
    assert "filename" in res[0]
