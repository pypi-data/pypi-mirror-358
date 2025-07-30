import httpx

from src.tools import response_handler


class Snapshot:
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

    def get_repos(self):
        r = self.clt.get("/_snapshot/_all")
        return response_handler(r)

    def list(self):
        for repo in self.get_repos():
            print(f"Repository: {repo}")

            r = self.clt.get("/_snapshot/found-snapshots/_all")
            if r.status_code == 200:

                for snapshot in r.json()["snapshots"]:
                    print(
                        f"Snapshot: {snapshot['snapshot']}, State: {snapshot['state']}, Start Time: {snapshot['start_time']}, Shards: {snapshot['shards']['total']},  Failed: {snapshot['shards']['failed']}"
                    )
            else:
                return response_handler(r)
