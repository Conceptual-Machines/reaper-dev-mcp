import json
import logging
import re
from dataclasses import dataclass
from typing import Annotated, Iterator

from bs4 import BeautifulSoup, NavigableString
from modules_generator import (
    API_HTML,
    LUA_KEYWORDS,
    REAPER_TYPES,
    UNSUPPORTED_NAMESPACES,
)

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

# These have come through as namespaces because of the _ in the function name, but they are not real namespaces.
FALSE_POSITIVE_NAMESPACES = (
    "GetEnvelopeInfo",
    "GetMediaItem",
    "GetMediaItemInfo",
    "GetMediaItemTake",
    "GetMediaItemTakeInfo",
    "GetMediaTrackInfo",
    "GetSet",
    "GetSetAutomationItemInfo",
    "GetSetEnvelopeInfo",
    "GetSetMediaItemInfo",
    "GetSetMediaItemTakeInfo",
    "GetSetMediaTrackInfo",
    "GetSetProjectInfo",
    "GetSetTrackSendInfo",
    "GetTrackSendInfo",
    "SetMediaItemInfo",
    "SetMediaItemTake",
    "SetMediaItemTakeInfo",
    "SetMediaTrackInfo",
    "SetTrackSendInfo",
    "file",
    "format",
    "get",
    "image",
    "kbd",
    "my",
    "parse",
    "reduce",
    "relative",
    "resolve",
    "time",
)

# These are namespaces that will be grouped under Reaper.
REAPER_NAMESPACES = (
    "Audio",
    "Dock",
    "Help",
    "Loop",
    "Main",
    "Master",
    "Menu",
    "Resample",
    "Splash",
    "ThemeLayout",
    "TimeMap",
    "Undo",
)


@dataclass
class ReaType:
    reascript_type: str
    name: str | None = None
    is_optional: bool = False
    description: str | None = None
    is_pointer: bool = False
    _default_value: str | None = None

    @property
    def is_reaper_type(self) -> bool:
        return self.reascript_type in REAPER_TYPES

    @property
    def is_reawrap_type(self) -> bool:
        return self.reawrap_type != self.reascript_type

    @property
    def reawrap_class(self) -> str:
        return f"ReaWrap{self.reascript_type}"

    @property
    def reawrap_type(self) -> str:
        if self.reascript_type == "ReaProject":
            return "Project"
        elif self.reascript_type == "MediaItem":
            return "Item"
        elif self.reascript_type == "MediaItemTake":
            return "Take"
        elif self.reascript_type == "MediaTrack":
            return "Track"
        elif self.reascript_type == "TrackEnvelope":
            return "Envelope"
        return self.reascript_type

    @property
    def lua_type(self) -> str:
        if self.is_reaper_type:
            return "userdata"
        if self.reascript_type in ("integer", "double", "float"):
            return "number"
        elif self.reascript_type == "boolean":
            return "boolean"
        elif self.reascript_type in ("string", "str"):
            return "string"
        else:
            return self.reascript_type

    @property
    def reawrap_lua_type(self) -> str:
        if self.is_reawrap_type:
            return "table"
        return self.lua_type

    @property
    def default_value(self) -> str:
        if self._default_value is None:
            if self.reascript_type == "boolean":
                self._default_value = "false"
            elif self.reascript_type == "number":
                self._default_value = "0"
            elif self.reascript_type == "string":
                self._default_value = '""'
            else:
                self._default_value = "nil"
        return self._default_value

    @default_value.setter
    def default_value(self, value: str):
        self._default_value = value


@dataclass
class ReaFunc:
    signature: Annotated[str, "The function signature including arguments."]
    reascript_name: Annotated[str, "The function name as per Reaper API."]
    fn_name_space: Annotated[
        str, "The ReaAPI function namespace, e.g Track, TrackFX, etc."
    ]
    arguments: Annotated[list[ReaType], "The function arguments."]
    return_values: Annotated[list[ReaType], "The function return values."]
    docs: Annotated[str, "The function documentation."]
    reawrap_name: Annotated[
        str | None,
        "The ReaWrap function name. Like reascript_name but snake_case and some further edits.",
    ] = None
    constants: list[ReaType] | None = None


def to_snake(s: str) -> str:
    # Add an underscore before each uppercase letter that is followed by a lowercase letter
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", s)
    # Add an underscore before each lowercase letter that is preceded by an uppercase letter
    s = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", s)
    # Convert the entire string to lowercase
    s = s.lower()
    return s


def get_html_from_file(html_file: str) -> BeautifulSoup:
    """Get the HTML content from a file."""
    with open(html_file, "r") as file:
        return BeautifulSoup(file, "html.parser")


def get_function_signature(parts: list[str]) -> str:
    """Get the function signature from a list of parts."""

    pattern = r"\w+\s*\(\s*[^)]*\s*\)"
    for part in parts:
        if re.match(pattern, part):
            return part
    raise ValueError(f"Could not find function signature in {parts}")


def get_arguments(signature: str) -> list[str]:
    """Get the arguments from a function signature."""
    pattern = r"\(([^)]*)\)"
    match = re.search(pattern, signature)
    if match:
        return match.group(1).split(",")
    raise ValueError(f"Could not find arguments in {signature}")


def parse_return_values(values: str) -> list[dict[str, str]]:
    """Parse the return values from a string."""
    if values:
        parts = values.split(",")
        types_and_names = [part.replace("=", "").strip() for part in parts]
        return list(iter_types_and_names(types_and_names))


def sanitize_name(parts: list[str]) -> str:
    """Sanitize the name of the argument. Convert to snake_case and remove any unwanted characters."""

    name = to_snake(parts[1]) if len(parts) > 1 else None
    if name in LUA_KEYWORDS:
        name = f"{name}_"
    if name:
        name = name.replace(".", "")
        if name.endswith("idx") and name != "idx":
            name = name.replace("idx", "_idx")
        elif name.endswith("name") and name != "name":
            name = name.replace("name", "_name")
        elif name.endswith("type") and name != "type":
            name = name.replace("type", "_type")
        elif name.endswith("val") and name != "val":
            name = name.replace("val", "_val")
        elif name.endswith("pos") and name != "pos":
            name = name.replace("pos", "_pos")
        elif name.startswith("is"):
            name = name.replace("is", "is_")
        elif name.startswith("swing") and name != "swing":
            name = name.replace("swing", "swing_")
        elif name.startswith("nudge") and name != "nudge":
            name = name.replace("nudge", "nudge_")
        elif name.startswith("timesig") and name != "timesig":
            name = name.replace("timesig", "time_sig")
        elif name == "guid_guid":
            name = "guid"
        if name.startswith("__"):
            name = name.replace("__", "")
        if "__" in name:
            name = name.replace("__", "_")
    return name


def iter_types_and_names(types_and_names: str) -> Iterator[ReaType]:
    """Iterate over the types and names and return a dict with keys type and name."""

    def get_type(type_: str) -> str:
        if type_ == "MediaItem_Take":
            return "MediaItemTake"
        return type_

    for value in types_and_names:
        if not value:
            return None
        parts = [p for p in value.split(" ") if p]
        name = sanitize_name(parts)
        if parts[0] == "optional":
            yield ReaType(name=name, reascript_type=parts[2], is_optional=True)
        elif len(parts) == 1:
            yield ReaType(reascript_type=get_type(parts[0]))
        else:
            yield ReaType(reascript_type=get_type(parts[0]), name=name)


def get_function_name(signature: str) -> str:
    """Get the function name from a function signature."""
    pattern = r"\b\w+(?=\s*\()"
    match = re.search(pattern, signature)
    if match:
        return match.group(0)
    raise ValueError(f"Could not find function name in {signature}")


def get_fn_name_space(fn_name_space_parts: list[str]) -> str:
    fn_namespace = fn_name_space_parts[0] if len(fn_name_space_parts) > 1 else None
    if fn_namespace and fn_namespace not in FALSE_POSITIVE_NAMESPACES:
        # we want to filter out false positives like "GetSetProjectInfo_String"
        return fn_namespace
    return None


def parse_lua_function(text: str) -> dict[str, str]:
    """Parse a Lua function from a string."""
    parts = text.split("reaper.", maxsplit=1)
    return_values = parse_return_values(parts[0] if parts[0] else None) or []
    signature = get_function_signature(parts)
    arguments = list(iter_types_and_names(get_arguments(signature)))
    name = get_function_name(signature)
    fn_name_space_parts = name.split("_", maxsplit=1)
    fn_name_space = get_fn_name_space(fn_name_space_parts)
    if fn_name_space == "TimeMap2":
        fn_name_space = "TimeMap"
    elif fn_name_space == "midi":
        fn_name_space = "MIDI"

    return {
        "signature": signature,
        "reascript_name": name,
        "fn_name_space": fn_name_space,
        "arguments": arguments,
        "return_values": return_values,
    }


def parse_constants_from_docs(docs_soup: BeautifulSoup) -> tuple[str, list[ReaType]]:
    """Parse the constants from the docs."""

    def convert_to_lua_type(type_: str) -> str:
        for rea_type in REAPER_TYPES:
            if rea_type in type_:
                return rea_type
        if type_.startswith("int"):
            return "number"
        elif type_.startswith("bool"):
            return "boolean"
        elif type_.startswith("char"):
            return "string"
        elif type_.startswith("str"):
            return "string"
        return type_

    def infer_type_from_description(description: str) -> str:
        for rea_type in REAPER_TYPES:
            if rea_type in description:
                return rea_type
        if "number" in description:
            return "number"
        elif "string" in description:
            return "string"
        elif "boolean" in description:
            return "boolean"
        return "any"

    pattern = r"^[A-Z]+(?:_[A-Z]+)*$"
    docs, constants = [], []
    for child in docs_soup.children:
        parts = [p.strip() for p in child.get_text(strip=True).split(":") if p.strip()]
        if len(parts) > 1:
            if re.match(pattern, parts[0]):
                name = parts[0]
                if len(parts) == 3:
                    type_ = convert_to_lua_type(parts[1])
                    description = parts[2]
                elif len(parts) == 2:
                    type_ = infer_type_from_description(parts[1])
                    description = parts[1]
                else:
                    type_ = convert_to_lua_type(parts[1])
                    description = "".join(parts[1:])
                constants.append(
                    ReaType(reascript_type=type_, name=name, description=description)
                )
            else:
                docs.append(child.get_text(strip=True))
        else:
            docs.append(child.get_text(strip=True))
    return "".join([d for d in docs if d]), constants


def iter_lua_functions(soup: BeautifulSoup, built_in: bool = False) -> dict[str, str]:
    """Iterate over the Lua functions in the REAPER API."""
    for func in soup.find("section", class_="functions_all").find_all(
        "div", class_="function_definition"
    ):
        l_func = func.find("div", class_="l_func")
        docs = func.find("p")
        docstr = docs.text.replace("\u00a0", "") if docs else None
        constants = None
        lua_func = parse_lua_function(l_func.text)
        if "Info" in lua_func["reascript_name"] and docs:
            docstr, constants = parse_constants_from_docs(docs)

        lua_func["docs"] = docstr
        lua_func["constants"] = constants

        yield ReaFunc(**lua_func)

    # built-in functions
    if built_in:
        for func in soup.find("section", class_="lua").find_all(
            "div", class_="function_definition"
        ):
            l_func = func.find("div", class_="l_func")
            docs = func.find("p")
            try:
                lua_func = parse_lua_function(l_func.text)
                lua_func["fn_name_space"] = "built_in"
                lua_func["docs"] = docs.text if docs else None
                yield ReaFunc(**lua_func)
            except ValueError as e:
                logger.error(f"Error parsing built-in function: {e} - {l_func.text}")


def group_functions_by_name_space(
    functions: list[ReaFunc],
) -> dict[str, list[ReaFunc]]:
    """Parse the REAPER API functions and group them by namespace.
    The criteria for namespaces are the following:
    If the function name has an underscore, the part before the underscore is the namespace, if upper case.
    If the first argument of a function is of `Reaper` type, the namespace is the type name.
    Functions that do not belong to a namespace are grouped under `Reaper`.
    Some exceptions are made for functions that belong to the `BR` and `CF` namespace, where the first argument, if it's
    of `Reaper` type, is used as the namespace.
    Ultimately, namespaces represent the LUA tables in the modules.
    """
    track_fx_exceptions = ("TrackFX_Delete", "TrackFX_GetCount")
    take_fx_exceptions = ("TakeFX_Delete", "TakeFX_GetCount")
    by_name_space = {}
    for l_func in functions:
        # the or condition is for user namespaces, e.g. BR, CF
        if (
            l_func.fn_name_space == "TrackFX" or "TrackFX" in l_func.reascript_name
        ) and l_func.reascript_name not in track_fx_exceptions:
            namespace = "TrackFX"
        # the or condition is for user namespaces, e.g. BR, CF
        elif (
            l_func.fn_name_space == "TakeFX" or "TakeFX" in l_func.reascript_name
        ) and l_func.reascript_name not in take_fx_exceptions:
            namespace = "TakeFX"
        elif (
            l_func.fn_name_space == "PCM"
            or l_func.arguments
            and l_func.arguments[0].reascript_type in ("PCM_source", "PCM_sink")
        ):
            namespace = "PCM"
        elif l_func.arguments and l_func.arguments[0].reascript_type in REAPER_TYPES:
            namespace = l_func.arguments[0].reascript_type

        elif l_func.fn_name_space in REAPER_NAMESPACES or l_func.fn_name_space is None:
            namespace = "Reaper"
        else:
            namespace = l_func.fn_name_space

        if namespace not in by_name_space:
            by_name_space[namespace] = []
        by_name_space[namespace].append(l_func)
    return by_name_space


def generate_reawrap_name(namespace: str, fn_name_space: str, reascript_name: str):
    """Remove the namespace from the function name and snake_case it and some further edits.
    :param namespace: The namespace of the function.
    :param fn_name_space: The ReaAPI function namespace, e.g. TrackFX, BR etc.
    :param reascript_name: The function name as per Reaper API.
    """
    ns_special_cases = ("MIDI", "Undo", "Audio", "Menu", "Splash", "ThemeLayout")
    functions_special_cases = {
        "TakeFX": {
            "get_fxguid": "get_guid",
            "get_fx_name": "get_name",
            "get_count": "get_fx_count",
        },
        "TrackFX": {
            "get_fxguid": "get_guid",
            "get_fx_name": "get_name",
            "get_count": "get_fx_count",
        },
        "MediaItemTake": {
            "get_count": "get_fx_count",
            "delete": "delete_fx",
        },
        "MediaTrack": {
            "get_count": "get_fx_count",
            "delete": "delete_fx",
        },
        "MediaItem": {
            "add_take_to": "add_take",
        },
        "ReaProject": {
            "get_project_name": "get_name",
        },
    }
    if "TimeMap2" in reascript_name:
        reascript_name = reascript_name.replace("TimeMap2", "TimeMap")

    if (
        fn_name_space and fn_name_space in reascript_name or namespace in reascript_name
    ) and fn_name_space not in ns_special_cases:  #
        reawrap_name = (
            reascript_name.replace(fn_name_space, "")
            if fn_name_space
            else reascript_name
        )
        reawrap_name = reawrap_name.replace(namespace, "")
    else:
        reawrap_name = reascript_name

    if reawrap_name.startswith("__"):
        reawrap_name = reawrap_name[2:]

    elif reawrap_name.startswith("_"):
        reawrap_name = reawrap_name[1:]

    reawrap_name = to_snake(reawrap_name)
    if reawrap_name in LUA_KEYWORDS:
        reawrap_name = f"{reawrap_name}_"
    reawrap_name = functions_special_cases.get(
        namespace, {reawrap_name: reawrap_name}
    ).get(reawrap_name, reawrap_name)
    return reawrap_name


def refine_functions(
    by_name_space: dict[str, list[ReaFunc]],
) -> dict[str, list[ReaFunc]]:
    """Once the functions are grouped by namespace, refine the name by removing the namespace and converting it to snake_case.
    Skip function that are declared as deprecated in the docs and remove duplicates."""

    refined = {}
    seen_funcs = {}
    for name_space, functions in sorted(
        by_name_space.items(), key=lambda item: item[0].lower()
    ):
        if name_space not in refined:
            refined[name_space] = []
        if name_space not in seen_funcs:
            seen_funcs[name_space] = set()
        for func in functions:
            reawrap_name = generate_reawrap_name(
                name_space, func.fn_name_space, func.reascript_name
            )
            func.reawrap_name = reawrap_name
            if reawrap_name not in seen_funcs[name_space]:
                # some ReaScript functions are duplicates and result in the same ReaWrap name, e.g. GetMediaItemTake and GetMediaItem_Take
                seen_funcs[name_space].add(reawrap_name)
                refined[name_space].append(func)

    return refined


def dedupe_functions(refined: dict[str, list[ReaFunc]]) -> dict[str, list[ReaFunc]]:
    """Further refinement. Remove duplicates from the functions or deprecated functions. Apply selective renaming."""
    deduped = {}
    for name_space, functions in refined.items():
        seen = set()
        deduped[name_space] = []
        for func in functions:
            if func.docs and "deprecated" in func.docs.lower():
                logger.debug(
                    f"Skipping deprecated function: {func.reascript_name} | namespace: {name_space}"
                )
                continue
            if func.docs and "discouraged" in func.docs.lower():
                logger.debug(
                    f"Skipping discouraged function: {func.reascript_name} | namespace: {name_space}"
                )
                continue
            if (
                func.reawrap_name == "count_selected_tracks"
                and name_space == "ReaProject"
            ):
                continue

            elif (
                func.reawrap_name == "count_selected_tracks2"
                and name_space == "ReaProject"
            ):
                func.reawrap_name = "count_selected_tracks"
                for arg in func.arguments:
                    if arg.name == "wantmaster":
                        arg.name = "want_master"
                        arg.is_optional = True
            elif (
                func.reawrap_name == "add_project_marker" and name_space == "ReaProject"
            ):
                continue
            elif (
                func.reawrap_name == "add_project_marker2"
                and name_space == "ReaProject"
            ):
                func.reawrap_name = "add_project_marker"
            elif (
                func.reawrap_name == "enum_project_markers2"
                and name_space == "ReaProject"
            ):
                continue

            elif (
                func.reawrap_name == "enum_project_markers3"
                and name_space == "ReaProject"
            ):
                func.reawrap_name = "enum_project_markers"

            elif (
                func.reawrap_name == "get_play_position_ex"
                and name_space == "ReaProject"
            ):
                func.reawrap_name = "get_play_position_lat_comp"

            elif (
                func.reawrap_name == "get_play_position2_ex"
                and name_space == "ReaProject"
            ):
                func.reawrap_name = "get_play_position"

            elif (
                func.reawrap_name == "get_project_time_signature2"
                and name_space == "ReaProject"
            ):
                func.reawrap_name = "get_project_time_signature"

            elif (
                func.reawrap_name == "get_selected_track" and name_space == "ReaProject"
            ):
                continue

            elif (
                func.reawrap_name == "get_selected_track2"
                and name_space == "ReaProject"
            ):
                func.reawrap_name = "get_selected_track"
                for arg in func.arguments:
                    if arg.name == "wantmaster":
                        arg.name = "want_master"
                        arg.is_optional = True

            if func.reawrap_name not in seen:
                seen.add(func.reawrap_name)
                deduped[name_space].append(func)
    return deduped


def get_functions_from_docs() -> dict[str, list[dict[str, str]]]:
    """Get LUA functions from the REAPER API docs."""
    soup = get_html_from_file(API_HTML)
    functions = list(iter_lua_functions(soup))
    by_name_space = group_functions_by_name_space(functions)
    refined = refine_functions(by_name_space)
    return dedupe_functions(refined)


def main():
    functions = get_functions_from_docs()
    for name_space, functions in functions.items():
        # print(name_space, len(functions))
        for func in functions:
            if func.constants:
                print(func)


if __name__ == "__main__":
    main()
