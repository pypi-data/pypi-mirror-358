import pyramscope

def test_get_id():
    a = []
    obj_id = pyramscope.get_id(a)
    assert isinstance(obj_id, int)

def test_get_refs():
    a = []
    refs = pyramscope.get_refs(a)
    assert isinstance(refs, list)

def test_get_top_heavy_objects():
    a = [list(range(100)), dict(a=1), "string"]
    top = pyramscope.get_top_heavy_objects(a, 2)
    assert isinstance(top, list)
    assert len(top) <= 2
