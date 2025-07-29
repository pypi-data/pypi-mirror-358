# -*- coding: utf-8 -*-
"""
---------------------------------------------
Copyright (c) 2025 ZhangYundi
Licensed under the MIT License. 
Created on 2025/6/26 15:52
Email: yundi.xxii@outlook.com
Description: 应用层
---------------------------------------------
"""

import typer

def init_config():
    from quda.ml import init_config

    init_config()

def run_config(config_path: str, config_name: str):
    import os
    from hydra import main
    from quda.ml.workflow import run as workflow_run

    abs_config_path = os.path.abspath(config_path)
    if not os.path.exists(abs_config_path):
        typer.secho(f"Missing {abs_config_path}", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    main(version_base=None, config_path=abs_config_path, config_name=config_name)(workflow_run)()
