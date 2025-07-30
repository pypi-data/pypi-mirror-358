from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from multiprocessing import Pool
from pathlib import Path
from typing import TYPE_CHECKING, cast

from rmm import util

if TYPE_CHECKING:
    from rmm.steam import WorkshopResult

DEBUG = False


@dataclass
class Mod:
    packageid: str | None = field(default_factory=str)
    before: list[str] = field(default_factory=list)
    after: list[str] = field(default_factory=list)
    incompatible: list[str] = field(default_factory=list)
    dirname: Path | None = None
    author: str = "Unknown"
    name: str | None = None
    versions: list[str] = field(default_factory=list)
    steamid: int | None = None
    ignored: bool = False
    repo_url: str | None = None
    workshop_managed: bool | None = None
    enabled: bool | None = None

    def title(self) -> str:
        return self.packageid or f"{self.name} by {self.author}"

    def __post_init__(self) -> None:
        if self.packageid:
            self.packageid = self.packageid.lower()
        if self.before:
            self.before = [item.lower() for item in self.before]
        if self.after:
            self.after = [item.lower() for item in self.after]

    def __eq__(self, other: Mod | str | int) -> bool:
        if isinstance(other, Mod):
            return (self.packageid and self.packageid == other.packageid) or (
                self.steamid and self.steamid == other.steamid
            )
        if isinstance(other, str) and self.packageid:
            return self.packageid.lower() == other.lower()
        if isinstance(other, int) and self.steamid:
            return self.steamid == other
        return NotImplemented

    def __hash__(self) -> int:
        if not self.packageid:
            raise ValueError("InvalidPackageHash")
        return hash(self.packageid)

    @staticmethod
    def create_from_workshop_result(wr: WorkshopResult) -> Mod:
        return Mod(steamid=wr.steamid, name=wr.name, author=wr.author)

    @staticmethod
    def list_to_dict(mods: list[Mod]) -> dict[str, Mod]:
        return {mod.packageid: mod for mod in mods if mod.packageid}

    @staticmethod
    def create_from_path(path: Path) -> Mod | None:
        def find_about_xml(path: Path) -> Path | None:
            # Use glob to get the case-insensitive About.xml path
            matches = list(path.glob("About/[Aa][Bb][Oo][Uu][Tt].[Xx][Mm][Ll]"))
            return matches[0] if matches else None

        def parse_tree(file_path: Path) -> ET.ElementTree:
            return ET.parse(file_path)

        def extract_packageid(root: ET.Element) -> str | None:
            try:
                return cast(str, cast(ET.Element, root.find("packageId")).text).lower()
            except AttributeError:
                name = util.element_grab("name", root)
                author = util.element_grab("author", root)
                if name and author:
                    return f"{name.lower()}.{author.lower()}"
            if DEBUG:
                raise AttributeError("Could not find or infer package ID")
            return None

        def read_steamid(path: Path) -> int | None:
            try:
                file_content = (path / "About" / "PublishedFileId.txt").read_text().strip()
                return int(file_content.encode("ascii", errors="ignore").decode())
            except (OSError, ValueError):
                if DEBUG:
                    print(f"Error reading steamid from {path}")
                return None

        def read_ignored(path: Path) -> bool:
            try:
                return (path / ".rmm_ignore").is_file()
            except OSError as e:
                print(e)
                return False

        try:
            about_xml_path = find_about_xml(path)
            if not about_xml_path:
                if "Place mods here.txt" not in str(path):
                    print(f"No About.xml found in {path}")
                return None

            tree_root = parse_tree(about_xml_path)
            package_id = extract_packageid(tree_root)
            if not package_id:
                return None

            author = util.element_grab("author", tree_root)
            if not author:
                author = util.list_grab("author", tree_root)
            if isinstance(author, list):
                author = ", ".join(author)
            if not author:
                author = "Unknown"

            return Mod(
                packageid=package_id,
                before=util.list_grab("loadAfter", tree_root),
                after=util.list_grab("loadBefore", tree_root),
                incompatible=util.list_grab("incompatibleWith", tree_root),
                dirname=path.name,
                author=author,
                name=util.element_grab("name", tree_root),
                versions=util.list_grab("supportedVersions", tree_root),
                steamid=read_steamid(path),
                ignored=read_ignored(path),
            )

        except OSError:
            print(f"Ignoring {path}")
        except ET.ParseError:
            print(f"Ignoring {path}.\n\t{about_xml_path} contains invalid XML.")


class ModFolder:
    @staticmethod
    def read(path: Path) -> list[Mod]:
        with Pool(16) as p:
            mods = cast(
                list[Mod],
                list(
                    filter(
                        None,
                        p.map(
                            Mod.create_from_path,
                            path.iterdir(),
                        ),
                    )
                ),
            )

        return mods

    @staticmethod
    def read_dict(path: Path) -> dict[str, Mod]:
        return Mod.list_to_dict(ModFolder.read(path))

    @staticmethod
    def search(path: Path, search_term: str) -> list[Mod]:
        return [
            r
            for r in ModFolder.read(path)
            if (isinstance(r.name, str) and search_term.lower() in r.name.lower())
            or (isinstance(r.author, str) and search_term.lower() in r.author.lower())
            or search_term == r.steamid
        ]

    @staticmethod
    def search_dict(path: Path, search_term: str) -> dict[str, Mod]:
        return Mod.list_to_dict(ModFolder.search(path, search_term))


EXPANSION_PACKAGES = [
    Mod(packageid="ludeon.rimworld", author="Ludeon", name="RimWorld"),
    Mod(packageid="ludeon.rimworld.ideology", author="Ludeon", name="Ideology"),
    Mod(packageid="ludeon.rimworld.royalty", author="Ludeon", name="Royalty"),
    Mod(packageid="ludeon.rimworld.biotech", author="Ludeon", name="Biotech"),
]
