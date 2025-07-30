import json
import httpx
from uuid import UUID
from dataclasses import dataclass, field


@dataclass
class File:
    name: str
    id: UUID | None = field(default=None)
    content: bytes | None = field(default=None)


class APIService:
    """
    A service class responsible for communicating with the remote API,
    including authentication and file operations.
    """

    def __init__(self, host: str):
        if not host.startswith(("http://", "https://")):
            host = f"http://{host}"

        self.base_url = host.rstrip("/")
        self.file_url = f"{self.base_url}/api/v1/files/"
        self.auth_url = f"{self.base_url}/api/v1/token/"
        self.client = httpx.Client()

    def authenticate(self, access_token: str, refresh_token: str) -> None:
        """
        Authenticates the client using the provided access or refresh tokens.

        If the access token is invalid but the refresh token is valid,
        it attempts to refresh the access token.

        Args:
            access_token (str): access token.
            refresh_token (str): refresh token.

        Raises:
            Exception: If both tokens are invalid.
        """
        if access_token is None or refresh_token is None:
            raise ValueError("Access and Refresh tokens must be provided.")

        if self.__verify_token(access_token):
            token = access_token
        else:
            success, token_or_msg = self.__refresh(refresh_token)
            if not success:
                raise Exception("Failed to authenticate. Please login again.")
            token = token_or_msg

        self.client.close()
        self.client = httpx.Client(headers={"Authorization": f"Bearer {token}"})

    def list(self) -> list[File]:
        """
        Retrieves a list of all files from the server.

        Returns:
            List[File]: A list of File objects.
        """
        res = self.client.get(self.file_url)
        res.raise_for_status()
        data = res.json()
        return [File(id=file["id"], name=file["name"]) for file in data]

    def create(self, file: File) -> tuple[UUID, bool]:
        """
        Creates a new file entry on the server.

        Args:
            file (File): The file object containing name and content.

        Returns:
            Tuple[Optional[UUID], bool]: A tuple with the new file's UUID and success flag.
        """
        try:
            res = self.client.post(
                self.file_url, data={"name": file.name, "content": file.content}
            )
            res.raise_for_status()
            data = json.loads(res.content)
            return data["id"], True

        except (httpx.RequestError, ValueError, KeyError):
            return None, False

    def retrieve(self, id: UUID) -> File:
        """
        Retrieves a specific file by its ID.

        Args:
            id (UUID): The unique identifier of the file.

        Returns:
            File: The retrieved file object.

        Raises:
            httpx.HTTPStatusError: If the file is not found.
        """

        try:
            res = self.client.get(f"{self.file_url}{id}/")
            res.raise_for_status()
            data = res.json()
            return File(name=data["name"], id=data["id"], content=data["content"])
        except Exception as e:
            raise e
        
    def delete(self, id: UUID) -> None:
        """
        Deletes a specific file by its ID.

        Args:
            id (UUID): The unique identifier of the file.
        """
        res = self.client.delete(f"{self.file_url}{id}/")
        res.raise_for_status()
        
    def login(self, username: str, password: str) -> tuple[str, str]:
        """
        Logs in using username and password to obtain access and refresh tokens.

        Args:
            username (str): The username.
            password (str): The password.

        Returns:
            Tuple[str, str]: Access and refresh tokens.

        Raises:
            Exception: If login fails or server returns an error.
        """
        res = httpx.post(
            self.auth_url, data={"username": username, "password": password}
        )
        res.raise_for_status()
        data = res.json()
        if res.status_code == 200:
            access = data["access"]
            refresh = data["refresh"]
            return access, refresh
        raise Exception(data["detail"])

    def __verify_token(self, token: str) -> bool:
        """
        Verifies a token by sending it to the authentication service.

        Args:
            token (str): The token string to be verified.

        Returns:
            bool: True if the token is valid (HTTP 200), False otherwise.
        """
        url = f"{self.auth_url}verify/"
        try:
            response = httpx.post(url, data={"token": token}, timeout=5.0)
            return response.status_code == 200
        except httpx.RequestError as exc:
            # print(f"Token verification request failed: {exc}")
            return False

    def __refresh(self, refresh_token: str) -> tuple[bool, str]:
        if not self.__verify_token(refresh_token):
            return False, "Not a valid refresh token"
        res = httpx.post(self.auth_url + "refresh/", data={"refresh": refresh_token})
        if res.status_code == 200:
            access_token = json.loads(res.content)["access"]
            return True, access_token
        return False, "failed to refresh token"
    def __refresh(self, refresh_token: str) -> tuple[bool, str]:
        """
        Attempts to refresh the access token using a refresh token.

        Args:
            refresh_token (str): The refresh token.

        Returns:
            Tuple[bool, str]: (True, access_token) if successful,
                              (False, error_message) if failed.
        """
        if not self.__verify_token(refresh_token):
            return False, "Not a valid refresh token"

        try:
            res = httpx.post(f"{self.auth_url}refresh/", data={"refresh": refresh_token})
            if res.status_code == 200:
                access_token = res.json()["access"]
                return True, access_token
            return False, res.json().get("detail", "Failed to refresh token")
        except httpx.RequestError:
            return False, "Request error during token refresh"