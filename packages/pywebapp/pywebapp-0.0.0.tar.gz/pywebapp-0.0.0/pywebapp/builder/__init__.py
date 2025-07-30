import os
import shutil


class FrontendConfigs:
    project_dir: str|None = None
    dist_dir: str|None = None
    build_script: str = "npm run build"
    dev_script: str = "npm run dev"
    entry_file: str = "index.html"
    entry_url:str = 'http://localhost:5173/'
    

def frontend_build():
    if FrontendConfigs.project_dir is None or FrontendConfigs.dist_dir is None:
        raise RuntimeError("project_dir or dist_dir is None")
    
    # 先删除
    if os.path.exists(FrontendConfigs.dist_dir):
        shutil.rmtree(FrontendConfigs.dist_dir)
    # 再创建
    if not os.path.exists(FrontendConfigs.dist_dir):
        os.makedirs(FrontendConfigs.dist_dir)
    
    # 再打包
    os.chdir(FrontendConfigs.project_dir)  # 切换到项目目录
    os.system(FrontendConfigs.build_script)  # 执行打包命令


def frontend_dev():
    if FrontendConfigs.project_dir is None or FrontendConfigs.dist_dir is None:
        raise RuntimeError("project_dir or dist_dir is None")
    os.chdir(FrontendConfigs.project_dir)  # 切换到项目目录
    os.system(FrontendConfigs.dev_script)  # 执行打包命令



class ApplicationConfigs:
    name: str|None = None
    spec_file: str = "photostyle.spec"
    add_data: str = "asset;./asset"  # 注意分号分隔
    icon_file: str = "logo.ico"
    entry_point: str = "photostyle.py"


def application_build():
    work_dir = os.path.dirname(os.path.abspath(__file__))
    from PyInstaller import __main__ as pyi
    app_name = ApplicationConfigs.name
    if app_name is None:
        raise RuntimeError("name is None")
    
    if not os.path.exists(f"./{app_name}.spec"):
        pyi.run(["-F", "-w", '--add-data','asset;./asset','-i','logo.ico',"photostyle.py"])
        
    pyi.run(['photostyle.spec'])




class Configs:
    pass