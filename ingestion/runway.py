def fetch_runway_status(runway_client):
    return runway_client.get_current_release_status()