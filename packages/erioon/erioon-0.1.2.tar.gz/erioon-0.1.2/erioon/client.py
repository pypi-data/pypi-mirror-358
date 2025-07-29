import os
import json
import requests
from datetime import datetime, timezone
from erioon.database import Database

class ErioonClient:
    def __init__(self, api, email, password, base_url="https://sdk.erioon.com"):
        self.api = api
        self.email = email
        self.password = password
        self.base_url = base_url
        self.user_id = None
        self.token_path = os.path.expanduser(f"~/.erioon_token_{self._safe_filename(email)}")
        self.login_metadata = None

        try:
            self.login_metadata = self._load_or_login()
            self._update_metadata_fields()
        except Exception as e:
            print(f"[ErioonClient] Initialization error: {e}")

    def _safe_filename(self, text):
        return "".join(c if c.isalnum() else "_" for c in text)

    def _do_login_and_cache(self):
        metadata = self._login()
        with open(self.token_path, "w") as f:
            json.dump(metadata, f)
        return metadata

    def _load_or_login(self):
        if os.path.exists(self.token_path):
            with open(self.token_path, "r") as f:
                metadata = json.load(f)
            if self._is_sas_expired(metadata):
                return self._do_login_and_cache()
            return metadata
        else:
            return self._do_login_and_cache()

    def _login(self):
        url = f"{self.base_url}/login_with_credentials"
        payload = {"api_key": self.api, "email": self.email, "password": self.password}
        headers = {"Content-Type": "application/json"}

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            self.login_metadata = data
            self._update_metadata_fields()
            return data
        else:
            try:
                msg = response.json().get("error", "Login failed")
            except Exception:
                msg = response.text
            print(f"[ErioonClient] Login failed: {msg}")
            raise RuntimeError(msg)

    def _update_metadata_fields(self):
        if self.login_metadata:
            self.user_id = self.login_metadata.get("_id")
            self.cluster = self.login_metadata.get("cluster")
            self.database = self.login_metadata.get("database")
            self.sas_tokens = self.login_metadata.get("sas_tokens", {})

    def _clear_cached_token(self):
        if os.path.exists(self.token_path):
            os.remove(self.token_path)
        self.user_id = None
        self.login_metadata = None

    def _is_sas_expired(self, metadata):
        expiry_str = metadata.get("sas_token_expiry") or metadata.get("expiry")
        if not expiry_str:
            return True
        try:
            expiry_dt = datetime.fromisoformat(expiry_str.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            return now >= expiry_dt
        except Exception:
            return True

    def __getitem__(self, db_id):
        if not self.user_id:
            print(f"[ErioonClient] Not authenticated. Cannot access database {db_id}.")
            raise ValueError("Client not authenticated.")

        try:
            return self._get_database_info(db_id)
        except Exception as e:
            print(f"[ErioonClient] Access failed for DB {db_id}, retrying login... ({e})")
            self._clear_cached_token()

            try:
                self.login_metadata = self._do_login_and_cache()
                self._update_metadata_fields()
            except Exception as login_error:
                print(f"[ErioonClient] Re-login failed: {login_error}")
                raise RuntimeError(login_error)

            try:
                return self._get_database_info(db_id)
            except Exception as second_error:
                print(f"[ErioonClient] DB fetch after re-auth failed: {second_error}")
                raise RuntimeError(second_error)

    def _get_database_info(self, db_id):
        payload = {"user_id": self.user_id, "db_id": db_id}
        headers = {"Content-Type": "application/json"}
        response = requests.post(f"{self.base_url}/db_info", json=payload, headers=headers)

        if response.status_code == 200:
            db_info = response.json()
            sas_info = self.sas_tokens.get(db_id)
            if not sas_info:
                raise Exception(f"No SAS token info for database id {db_id}")

            container_url = sas_info.get("container_url")
            sas_token = sas_info.get("sas_token")

            if not container_url or not sas_token:
                raise Exception("Missing SAS URL components")

            if not sas_token.startswith("?"):
                sas_token = "?" + sas_token

            sas_url = container_url.split("?")[0] + sas_token

            return Database(
                user_id=self.user_id,
                metadata=db_info,
                database=self.database,
                cluster=self.cluster,
                sas_url=sas_url
            )
        else:
            try:
                error_json = response.json()
                error_msg = error_json.get("error", response.text)
            except Exception:
                error_msg = response.text
            raise Exception(f"Failed to fetch database info: {error_msg}")

    def __str__(self):
        return self.user_id if self.user_id else "[ErioonClient] Unauthenticated"

    def __repr__(self):
        return f"<ErioonClient user_id={self.user_id}>" if self.user_id else "<ErioonClient unauthenticated>"
