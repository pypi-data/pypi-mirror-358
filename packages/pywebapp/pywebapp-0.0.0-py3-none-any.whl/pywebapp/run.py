import typer
import os
from PyInstaller import __main__ as pyi
import shutil


main = typer.Typer()
CUR_PATH = os.path.dirname(os.path.abspath(__file__))

@main.command('build-ui')
def build_ui():
    output_path = os.path.join(CUR_PATH,"asset","frontend")
    # 先删除
    if os.path.exists(output_path):
        shutil.rmtree(output_path)
            
    # 再创建
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    # 再打包
    os.chdir(os.path.join(CUR_PATH,"frontend"))
    os.system("npm run build")
    os.chdir(CUR_PATH)


@main.command('build-exe')
def build_exe():
    if not os.path.exists("./photostyle.spec"):
        pyi.run(["-F", "-w", '--add-data','asset;./asset','-i','logo.ico',"photostyle.py"])
        
    pyi.run(['photostyle.spec'])
    

@main.command('build')
def build():
    build_ui()
    build_exe()
    

if __name__ == "__main__":
    main()