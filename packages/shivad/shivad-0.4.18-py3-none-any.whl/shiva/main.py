# Copyright (c) 2024 Boris Soldatov
# SPDX-License-Identifier: MIT
#
# This file is part of an open source project licensed under the MIT License.
# See the LICENSE file in the project root for more information.

import asyncio
import os
import platform
import signal
from asyncio.exceptions import CancelledError

import flatdict
import uvicorn
import yaml
from fastapi import FastAPI
from shiva.lib.tools import Config
from loguru import logger

from shiva.common.daemon import Shiva
from shiva.common.logging import setup_loggers

# App init
app = FastAPI(debug=False)
app.logger = logger
app.shiva = None
config_path = None


# # Setup events
@app.on_event('shutdown')
async def shutdown_daemon():
    logger.info('Shutting down')
    await app.shiva.stop_async()
    logger.info('All instances stopped!')


@app.on_event('startup')
async def run_daemon(*args, **kwargs):
    logger.warning('Starting setup...')
    # loop = asyncio.get_running_loop()
    config_helper = Config(config_path)
    config = config_helper.get_config()
    # Logging
    setup_loggers(config)

    daemon = Shiva(config, None, app)
    app.shiva = daemon
    loop = asyncio.get_event_loop()
    daemon.loop = loop

    # Prepare daemon
    await daemon.prepare()

    # Run daemon
    loop.create_task(daemon.run())
    if platform.system() != 'Windows':
        loop.add_signal_handler(signal.SIGINT, daemon.stop)
        loop.add_signal_handler(signal.SIGHUP, daemon.stop)
        loop.add_signal_handler(signal.SIGTERM, daemon.stop)


def main(config):
    try:
        import os
        import sys
        print(f'CWD: {os.getcwd()}')
        sys.path.append(os.getcwd())
        global config_path
        if config:
            config_path = config
        config_path = config_path or os.environ.get('SHIVA_CONFIG') or './config.yml'

        # Get port/host if available
        config_helper = Config(config_path)
        config = config_helper.get_config()
        port = 8085
        host = '0.0.0.0'

        if type(config.get('common')) == dict:
            web = config['common'].get('web')
            if web:
                host = web.get('host', host)
                port = web.get('port', port)

        logger.info(f'Running web instance on: {host}:{port}')
        uvicorn.run("shiva.main:app", host=host, port=port, log_level="error")
    except CancelledError:
        logger.warning('Web application stopped!')
