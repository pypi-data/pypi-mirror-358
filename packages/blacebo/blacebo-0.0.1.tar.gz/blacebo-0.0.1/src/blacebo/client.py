import base64
import httpx

from .endpoints.space import Space
from .endpoints.role import Role
from .endpoints.role_mapping import RoleMapping
from .endpoints.data_view import DataView
from .endpoints.kb_settings import KibanaSettings


class Client:

    def __init__(
        self,
        elasticsearch_host: str = None,
        kibana_host: str = None,
        port: int = 443,
        username: str = None,
        password: str = None,
        api_key: str = None,
    ):
        authorization = (
            f"ApiKey {api_key}"
            if api_key is not None
            else f"Basic {base64.b64encode(bytes(username + ":" + password, 'utf-8')).decode('utf-8')}"
        )

        self._kb = httpx.Client(
            base_url=f"https://{kibana_host}:{port}",
            headers=httpx.Headers(
                {
                    "Content-Type": "application/json",
                    "Authorization": authorization,
                    "kbn-xsrf": "true",
                }
            ),
        )
        self._es = httpx.Client(
            base_url=f"https://{elasticsearch_host}:{port}",
            headers=httpx.Headers(
                {
                    "Content-Type": "application/json",
                    "Authorization": authorization,
                }
            ),
        )

    @property
    def space(self):
        return Space(self._kb)

    @property
    def role(self):
        return Role(self._kb)

    @property
    def role_mapping(self):
        return RoleMapping(self._es)

    @property
    def data_view(self):
        return DataView(self._kb)

    @property
    def kibana_settings(self):
        return KibanaSettings(self._kb)


class CloudClient(Client):
    def __init__(
        self,
        cluster_name: str,
        location: str,
        private_link: bool = False,
        api_key: str = None,
        username: str = None,
        password: str = None,
    ):
        super().__init__(
            elasticsearch_host=f"{cluster_name}.es{".privatelink" if private_link else ""}.{location}.azure.elastic-cloud.com",
            kibana_host=f"{cluster_name}.kb{".privatelink" if private_link else ""}.{location}.azure.elastic-cloud.com",
            api_key=api_key,
            username=username,
            password=password,
        )
