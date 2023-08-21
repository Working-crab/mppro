from collections.abc import Callable, Iterable, Mapping
import json
from typing import Any
import aiohttp
import asyncio
import time
import multiprocessing
import user_agent
import clickhouse_driver
import random
from threading import Thread
from class_list.main_var import Main_var

class Process(multiprocessing.Process):
    def __init__(self, group: None = None, target: Callable[..., object] | None = None, name: str | None = None, args: Iterable[Any] = (), kwargs: Mapping[str, Any] = [], *, daemon: bool | None = None, id_product = []) -> None:
        super().__init__(group, target, name, args, kwargs, daemon=daemon)
        self.id_product_list = id_product
        print(len(self.id_product_list),self.name)
        self.client = clickhouse_driver.Client.from_url(Main_var.DB_URL)