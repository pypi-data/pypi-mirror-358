import httpx
import re

from src.tools import response_handler

BASE_URL = "/_ilm/"


class IndexLifecycleManagement:
    def __init__(self, auth):
        self.clt = httpx.Client(
            base_url=f"https://{auth.name}.es{".privatelink" if auth.private_link else ""}.{auth.location}.azure.elastic-cloud.com:{auth.port}",
            headers=httpx.Headers(
                {
                    "Content-Type": "application/json",
                    "Authorization": f"ApiKey {auth.api_key}",
                }
            ),
        )

    def get(self):
        r = self.clt.get(BASE_URL + "policy/")
        return response_handler(r)

    def list(self, custom_only=False, filter=None):
        pattern = re.compile(filter) if filter else None
        r = self.get()
        for name in sorted(r.keys()):
            if custom_only and not name.startswith("sce-"):
                continue
            if pattern and not pattern.search(name):
                continue
            try:
                print(f"\nPolicy: {name}")
                for phase in r[name]["policy"]["phases"]:
                    print(
                        f"  Phase: {phase}  Minimum Age: {r[name]["policy"]['phases'][phase]['min_age']}"
                    )
                    for action in r[name]["policy"]["phases"][phase]["actions"]:
                        print(f"    Action: {action}")
                        for key, value in r[name]["policy"]["phases"][phase]["actions"][
                            action
                        ].items():
                            print(f"      {key}: {value}")
                print("  in_use_by:")
                for key, value in r[name]["in_use_by"].items():
                    if len(value) == 0:
                        continue
                    print(f"    {key}: {value}")
            except KeyError as e:
                print(f"Policy: {name}, Error: {e}")
                print(f"Response: {r[name]}")

    def create(self, name, body):
        r = self.clt.put(BASE_URL + "policy/" + name, json=body)
        return response_handler(r)

    def delete(self, name):
        r = self.clt.delete(BASE_URL + "policy/" + name)
        return response_handler(r)

    def status(self):
        r = self.clt.get(BASE_URL + "_status")
        return response_handler(r)
