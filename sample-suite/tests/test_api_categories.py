def test_categories_link_children_to_parents(api):
    categories = api.categories()
    by_id = {category.id: category for category in categories}
    children = [category for category in categories if category.parent_id]
    assert children
    for child in children:
        assert child.parent_id in by_id
        assert child.name
        assert child.slug
