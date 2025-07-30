from webapp.bridge import out_ts_file
from typing import TypedDict,Literal

__expose2web_functions__ = []

class Application:
    def __init__(self) -> None:
        pass



class FrontendLocalFile(TypedDict):
    """
    window: 窗口名称
    file: 本地html文件路径
    """
    window: str
    file: str




def run(
    *,
    app: Application = Application(),
    build: bool = False,
    build_type: Literal['full','frontend','app'] = 'full',
    frontend_server:str|None = None,
    frontend_local_file:FrontendLocalFile|list[FrontendLocalFile]|None = None,
    output_dts_file:str|None = None,
):
    
    if output_dts_file:
        out_ts_file(output_dts_file)
    
    if build:
        pass

    else:
        pass


if __name__ == "__main__":
    run()
