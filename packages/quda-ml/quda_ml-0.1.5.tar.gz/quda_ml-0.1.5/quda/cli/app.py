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

    from quda.ml.workflow import run as workflow_run

    return workflow_run(config_path, config_name)
