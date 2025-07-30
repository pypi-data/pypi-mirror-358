import re
import sys
import requests

from typing import Any
from array import array
from pathlib import Path
from dataclasses import dataclass
from .logger import StatusCode, log_status


@dataclass
class ServerConfigInfo:
    regex_flag: re.Pattern
    teams: dict[int, str]
    nop_team: tuple[int, str]
    url_flag_ids: str


class ServerConfig:
    def __init__(self, server_address: str, config_api_path: str = "/api/v1/config"):
        self.server_address = server_address
        self.config_api_path = config_api_path
        self.raw_config = self.__get_raw_config()

    def __get_auth_token(self) -> str:
        """
        Get the authentication token from the session file.

        Returns:
            str: The authentication token.
        """
        session_path = Path.home().joinpath(".config", "cookiefarm", "session")

        if not session_path.exists():
            log_status(StatusCode.FATAL, "Session file not found. Please login first.")
            sys.exit(1)

        with open(session_path) as session_file:
            token = session_file.read().strip()

        return token

    def __get_raw_config(self) -> dict[str, Any]:
        """
        Get the configuration from the server.

        Returns:
            dict[str, Any]: The configuration dictionary.
        Raises:
            ValueError: If the response from the server is not ok.
        """
        response = requests.get(
            f"http://{self.server_address}{self.config_api_path}",
            headers={
                "Content-Type": "application/json",
                "Cookie": f"token={self.__get_auth_token()}",
            },
        )
        if not response.ok:
            log_status(
                StatusCode.FATAL, "Failed to retrieve configuration from the server."
            )
            sys.exit(1)

        return response.json()

    def config(self) -> ServerConfigInfo:
        """
        Get the configuration information from the server.

        Returns:
            ServerConfigInfo: A ServerConfigInfo object containing regex_flag and teams.
        Raises:
            ValueError: If the response from the server is not ok.
        """
        config_json = self.raw_config

        regex_flag = re.compile(config_json["client"]["regex_flag"])
        format_ip_teams: str = config_json["client"]["format_ip_teams"]
        my_team = int(config_json["client"]["my_team_id"])
        nop_team: int = int(config_json["client"]["nop_team"])
        url_flag_ids: str = config_json["client"]["url_flag_ids"]

        if my_team < nop_team:
            x_1 = my_team
            x_2 = nop_team
        else:
            x_1 = nop_team
            x_2 = my_team

        ip_teams = array("H", range(x_1))

        for i in range(
            x_1 + 1, x_2
        ):
            ip_teams.append(i)

        for i in range(
            x_2 + 1, int(config_json["client"]["range_ip_teams"]) + 1
        ):
            ip_teams.append(i)


        for i in range(
            my_team + 1, int(config_json["client"]["range_ip_teams"]) + 1
        ):
            ip_teams.append(i)

        return ServerConfigInfo(
            re.compile(regex_flag),
            {i: format_ip_teams.format(i) for i in ip_teams},
            (nop_team, format_ip_teams.format(nop_team)),
            url_flag_ids
        )
