import requests

PUBLIC_API = "https://pub.orcid.org/v3.0/"


def get_author(orcid: str, full: bool = False) -> dict:
    response = requests.get(f"{PUBLIC_API}{orcid}", headers={"Accept": "application/json"}, timeout=2.0)
    if response.status_code != 200:
        raise requests.exceptions.HTTPError(f"REST API returned: {response.status_code}")

    data = response.json()
    if full:
        return data
    given_name = data["person"].get("name", {}).get("given-names", {}).get("value")
    family_name = data["person"].get("name", {}).get("family-name", {}).get("value")

    return {"given_name": given_name, "family_name": family_name}
