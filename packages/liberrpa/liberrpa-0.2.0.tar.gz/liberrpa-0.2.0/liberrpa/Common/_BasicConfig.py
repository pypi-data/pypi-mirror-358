# FileName: _BasicConfig.py
__author__ = "Jiyan Hu"
__email__ = "mailwork.hu@gmail.com"
__license__ = "GNU Affero General Public License v3.0 or later"
__copyright__ = f"Copyright (C) 2025 {__author__}"


import os
from pathlib import Path
import socket
import json5
from typing import TypedDict, Literal, Any


class DictBasicConfig(TypedDict):
    outputLogPath: str
    localServerPort: int
    uiAnalyzerTheme: Literal["light", "dark"]
    uiAnalyzerMinimizeWindow: bool


def get_basic_config_dict() -> DictBasicConfig:

    strLiberRPAPath: str = get_liberrpa_folder_path()

    dictReplaceKeywords: dict[str, str] = {
        "${LiberRPA}": strLiberRPAPath,
        "${UserName}": os.getlogin(),
        "${HostName}": socket.gethostname(),
    }

    dictProject: dict[str, Any] = json5.loads(Path("./project.json").read_text(encoding="utf-8"))  # type: ignore

    if os.getenv("LogFolderName") in ["_ChromeGetLocalServerPort", "_LiberRPALocalServer"]:
        dictReplaceKeywords["${ToolName}"] = "BuildinTools"

    elif dictProject.get("executorPackage") == True:
        dictReplaceKeywords["${ToolName}"] = "Executor"

    else:
        # Suppose other Python programs are running in vscode.
        dictReplaceKeywords["${ToolName}"] = "Editor"

    # Open the json file to get original dict.
    dictBasicConfig: DictBasicConfig = json5.loads(
        Path(strLiberRPAPath).joinpath("./configFiles/basic.jsonc").read_text(encoding="utf-8", errors="strict")
    )  # type: ignore - type is right

    # Replace predefined variables
    for strKeyOuter in dictBasicConfig:
        if isinstance(dictBasicConfig[strKeyOuter], str):
            for strKeyInner in dictReplaceKeywords:
                dictBasicConfig[strKeyOuter] = dictBasicConfig[strKeyOuter].replace(
                    strKeyInner, dictReplaceKeywords[strKeyInner]
                )
    return dictBasicConfig


def get_liberrpa_folder_path() -> str:
    strPath = os.environ.get("LiberRPA")
    if strPath:
        return strPath
    else:
        raise ValueError(
            f'Didn\'t find LiberRPA in System Environment Variable. You should run the "InitLiberRPA.exe" in the LiberRPA root folder. It will add a "LiberRPA" variable in your computer\'s User Environment Variables.'
        )


def get_liberrpa_ico_path(component: Literal["LiberRPALocalServer"] | None = None) -> str:
    strLiberRPAPath = get_liberrpa_folder_path()
    if component == "LiberRPALocalServer":
        strIconPath = Path(strLiberRPAPath) / "envs/assets/icon/LiberRPA_icon_v3_color_LocalServer.ico"
    else:
        strIconPath = Path(strLiberRPAPath) / "envs/assets/icon/LiberRPA_icon_v3_color.ico"
    if not Path(strIconPath).is_file():
        raise FileNotFoundError("LiberRPA icon file is missing: " + str(strIconPath))
    print("strIconPath=", strIconPath)
    return str(strIconPath)


if __name__ == "__main__":
    print(type(get_basic_config_dict()))
    print(get_basic_config_dict())
