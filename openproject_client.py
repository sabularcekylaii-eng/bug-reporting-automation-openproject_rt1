import requests

import config


class OpenProjectClient:
    def __init__(self):
        self.base_url = config.OP_BASE_URL
        self.auth = ("apikey", config.OP_API_TOKEN)

    def create_bug(self, title, steps, expected, actual, environment):
        description = (
            f"{actual}\n\n"
            f"Steps to Reproduce:\n{steps}\n\n"
            f"Expected Result:\n{expected}\n\n"
            f"Environment:\n{environment}"
        )

        payload = {
            "subject": title,
            "description": {
                "format": "markdown",
                "raw": description,
            },
            "_links": {
                "type": {"href": f"/api/v3/types/{config.OP_BUG_TYPE_ID}"},
                "project": {"href": f"/api/v3/projects/{config.OP_PROJECT_ID}"},
                "version": {"href": f"/api/v3/versions/{config.OP_NEXT_SPRINT_VERSION_ID}"},
            },
        }

        url = f"{self.base_url}/projects/{config.OP_PROJECT_IDENTIFIER}/work_packages"
        response = requests.post(url, json=payload, auth=self.auth)
        response.raise_for_status()

        data = response.json()
        wp_id = data["id"]
        return wp_id, config.OP_BACKLOGS_URL
