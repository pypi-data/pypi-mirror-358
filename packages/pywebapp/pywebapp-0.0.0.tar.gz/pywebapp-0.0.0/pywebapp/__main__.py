import typer
import os

main = typer.Typer()

@main.command('init')
def init(use_defaults: bool = typer.Option(False, "--defaults", "-d", help="使用默认配置")):
    """交互式初始化项目"""
    print("初始化项目",use_defaults)
    project_name = typer.prompt("项目名称")
    version = typer.prompt("版本号", default="1.0.0")
    description = typer.prompt("项目描述", default="")
    
    print(f"创建项目: {project_name}@{version}")
    print(f"描述: {description}")



@main.command('build')
def build():
    print("build")

@main.command('run')
def run():
    # 查看当前目录是否存在 abc.json 文件
    if os.path.exists("abc.json"):
        print("abc.json 文件存在")
    print("run")

@main.command('dev')
def dev():
    print("dev")


# 参数
@main.command('create')
def create(name:str):
    print("create",name)


if __name__ == "__main__":
    main()