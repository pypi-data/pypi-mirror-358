# -*- coding: utf-8 -*-
"""
---------------------------------------------
Copyright (c) 2025 ZhangYundi
Licensed under the MIT License. 
Created on 2025/6/26 11:34
Email: yundi.xxii@outlook.com
Description: 命令行工具
---------------------------------------------
"""

import typer

app = typer.Typer()

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        typer.echo("[QUDA-ML] CLI.")
        typer.echo("Run `quda-ml --help` to get more information.")

@app.command()
def init_config():

    """生成模版配置，复制自: quda/ml/conf"""

    from pathlib import Path
    import shutil
    from importlib.resources import files

    source_conf_dir = files("quda.ml").joinpath("conf")
    # 当前工作目录下的 conf/
    target_conf_dir = Path.cwd() / "conf"
    if target_conf_dir.exists():
        typer.echo(f"[QUDA-ML] - {target_conf_dir} already exists.")
        return
    try:
        shutil.copytree(source_conf_dir, target_conf_dir)
        typer.echo(f"[QUDA-ML] - {target_conf_dir} created.")
    except Exception as e:
        typer.secho(f"[QUDA-ML] - Failed to create {target_conf_dir}\n{e}", fg=typer.colors.RED)

@app.command()
def run(config_path: str, config_name: str):
    from hydra import main
    from .workflow import run
    main(version_base=None, config_path=config_path, config_name=config_name)(run)()


if __name__ == '__main__':
    app()

