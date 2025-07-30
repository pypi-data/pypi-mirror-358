import os
import re
import subprocess
import tempfile
import urllib.error
import urllib.request
import zipfile
from functools import cache
from pathlib import Path
from typing import Any, Tuple

from bs4 import BeautifulSoup
from bs4.element import Tag

from rmm import util
from rmm.mod import Mod, ModFolder

STEAMCMD_WINDOWS_URL = "https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip"


class SteamDownloader:
    @staticmethod
    def download_steamcmd_windows(path: Path) -> None:
        download_path = path / "steamcmd.zip"
        max_retries = 10
        print("Installing SteamCMD")
        for count in range(max_retries + 1):
            try:
                urllib.request.urlretrieve(STEAMCMD_WINDOWS_URL, download_path)
            except urllib.error.URLError as e:
                if count < max_retries:
                    continue
                raise e

        print("Extracting steamcmd.zip...")
        with zipfile.ZipFile(download_path, "r") as zr:
            zr.extractall(path)

        os.chdir(path)
        try:
            for n in util.execute("steamcmd +login anonymous +quit"):
                print(n, end="")
        except subprocess.CalledProcessError:
            pass

    @staticmethod
    def find_path() -> tuple[Path, Path]:
        home_path = None
        mod_path = None
        try:
            for d in Path(tempfile.gettempdir()).iterdir():
                if d.name[0:4] == "rmm-" and d.is_dir() and (d / ".rmm").is_file():
                    home_path = d
                    break
        except FileNotFoundError:
            pass

        if util.platform() == "win32":
            home_path = Path(tempfile.gettempdir()) / "rmm"
            home_path.mkdir(parents=True, exist_ok=True)

        if not home_path:
            home_path = Path(tempfile.mkdtemp(prefix="rmm-"))
            with (home_path / ".rmm").open("w"):
                pass

        if not home_path:
            raise Exception("Error could not get temporary directory")

        if util.platform() == "win32":
            mod_path = home_path / "SteamApps/workshop/content/294100/"
        elif util.platform() == "darwin":
            mod_path = (
                home_path / "Library/Application Support/Steam/SteamApps/workshop/content/294100/"
            )
        else:
            mod_path = home_path / util.extract_download_path()
        return (home_path, mod_path)

    @staticmethod
    def download(mods: list[int]) -> Tuple[list[Mod], Path]:
        home_path, mod_path = SteamDownloader.find_path()

        if not home_path:
            raise Exception("Error could not get temporary directory")

        workshop_item_arg = " +workshop_download_item 294100 "
        if util.platform() == "win32":
            os.chdir(home_path)
            if not (home_path / "steamcmd.exe").exists():
                SteamDownloader.download_steamcmd_windows(home_path)

            query = f"steamcmd +login anonymous {workshop_item_arg + workshop_item_arg.join(str(m) for m in mods)} +quit"
            print()
            for n in util.execute(query):
                print(n, end="")
        else:
            query = f'env HOME="{home_path!s}" steamcmd +login anonymous {workshop_item_arg + workshop_item_arg.join(str(m) for m in mods)} +quit >&2'
            util.run_sh(query)

        # TODO: ugly work around for weird steam problem
        if util.platform() == "linux" and not mod_path.exists():
            mod_path = SteamDownloader.replace_path(mod_path)

        return (ModFolder.read(mod_path), mod_path)

    @staticmethod
    def replace_path(path: Path) -> Path:
        path_parts = []
        found = False
        for n in reversed(path.parts):
            if n == ".steam" and not found:
                path_parts.append("Steam")
                found = True
            else:
                path_parts.append(n)

        return Path(*reversed(path_parts))


class WorkshopResult:
    def __init__(
        self,
        steamid: int,
        name: str = "",
        author: str = "",
        description: str = "",
        update_time: str = "",
        size: str = "",
        rating: str = "",
        create_time: str = "",
        num_ratings: str = "",
        required_items: dict[str, Any] = dict(),
    ) -> None:
        self._steamid = steamid
        self.name = name
        self.author = author
        self.description = description
        self.update_time = update_time
        self.size = size
        self.create_time = create_time
        self.num_ratings = num_ratings
        self.rating = rating

    def __str__(self) -> str:
        return "\n".join(
            [
                prop + ": " + str(getattr(self, prop))
                for prop in self.__dict__
                if not callable(self.__dict__[prop])
            ]
        )

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, WorkshopResult):
            raise NotImplementedError
        return self._steamid == other._steamid

    def __hash__(self) -> int:
        return hash(self._steamid)

    @property
    def steamid(self) -> int:
        return self._steamid

    @steamid.setter
    def steamid(self, *args) -> None:  # noqa: ANN002
        raise AttributeError("WorkshopResult.steamid is immutable")


class WorkshopWebScraper:
    headers = {  # noqa: RUF012
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36"
    }
    index_query = "https://steamcommunity.com/workshop/browse/?appid=294100&searchtext={}"
    detail_query = "https://steamcommunity.com/sharedfiles/filedetails/?id={}"

    @classmethod
    def _request(cls, url: str, term: str):  # noqa: ANN206
        max_retries = 5
        for n in range(max_retries + 1):
            try:
                return urllib.request.urlopen(
                    urllib.request.Request(
                        url.format(term.replace(" ", "+")),
                        headers=WorkshopWebScraper.headers,
                    )
                )
            except urllib.error.URLError as e:
                if n < max_retries:
                    continue
                raise e

    @classmethod
    @cache
    def detail(cls, steamid: int, wsResult: WorkshopResult | None = None) -> WorkshopResult:
        results = BeautifulSoup(
            cls._request(cls.detail_query, str(steamid)),
            "html.parser",
        )
        if wsResult is None:
            wsResult = WorkshopResult(steamid)

        details = results.find_all("div", class_="detailsStatRight")

        # size of mods
        try:
            size = details[0].get_text()
            wsResult.size = size
        except IndexError:
            pass
        # create time
        try:
            created = details[1].get_text()
            wsResult.create_time = created
        except IndexError:
            pass
        # update time
        try:
            updated = details[2].get_text()
            wsResult.update_time = updated
        except IndexError:
            pass
        # description
        try:
            description = results.find("div", class_="workshopItemDescription")
            if description:
                description = description.get_text()
                wsResult.description = description
        except AttributeError:
            pass
        # no. of rating
        try:
            num_ratings = results.find("div", class_="numRatings")
            if num_ratings:
                num_ratings = num_ratings.get_text()
                wsResult.num_ratings = num_ratings
        except AttributeError:
            pass
        # rating
        try:
            rating = re.search(
                "([1-5])(?:-star)",
                str(results.find("div", class_="fileRatingDetails").img),
            )
            if rating:
                rating = rating.group(1)
                wsResult.rating = rating
        except AttributeError:
            pass

        # required item: list[WorkshopResult]
        required_mods = list()
        reqItms = results.find("div", id="RequiredItems")
        if reqItms:
            for itm in reqItms.children:
                if isinstance(itm, Tag):
                    modid = int(re.search(r"\d+", itm["href"]).group())
                    # adding (*) at beginning of name to indicate a dependencies
                    modname = "(*) " + itm.find("div").get_text().strip()
                    required_mods.append(WorkshopResult(modid, name=modname))
        wsResult.required_items = required_mods

        return wsResult

    @classmethod
    def search(cls, term: str, reverse: bool = False) -> list[WorkshopResult]:
        page_result = BeautifulSoup(
            cls._request(cls.index_query, term),
            "html.parser",
        ).find_all("div", class_="workshopItem")

        results = []
        for r in page_result:
            try:
                item_title = r.find("div", class_="workshopItemTitle").get_text()
                author_name = r.find("div", class_="workshopItemAuthorName").get_text()[3:]
                steamid = int(re.search(r"\d+", r.find("a", class_="ugc")["href"]).group())
            except (AttributeError, ValueError):
                continue
            results.append(WorkshopResult(steamid, name=item_title, author=author_name))

        if reverse:
            return list(reversed(results))
        return results
