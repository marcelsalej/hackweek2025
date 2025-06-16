def fetch_confluence_updates(confluence_client, space_key):
    results = confluence_client.get_all_pages_from_space(space_key, limit=10)
    return [{"title": page["title"], "id": page["id"]} for page in results]