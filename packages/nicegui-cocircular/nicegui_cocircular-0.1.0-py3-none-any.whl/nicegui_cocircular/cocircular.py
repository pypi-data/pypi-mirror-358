"""共円

格子をクリックして点を作成していき、4点が同心円になったらゲームオーバー
"""

from itertools import product
from logging import DEBUG, basicConfig, getLogger
from typing import ClassVar

import numpy as np
from nicegui import ui

from .feature import Feature, Point, get_feature

LAST_CLICKED_COLOR = -1
logger = getLogger(__name__)


class Square(ui.button):
    """マス"""

    colors: ClassVar[dict[int, str]] = {0: "black", 1: "blue", 2: "green", 3: "orange", 4: "yellow", 5: "pink"}

    def __init__(self, game: "Game", y: int, x: int) -> None:
        """初期化"""
        super().__init__()
        self.game = game
        self.y = y
        self.x = x
        self.on("click", lambda: self.game.click(y, x))
        self.classes("w-10 h-10 bg-white")
        self.build()

    def build(self) -> None:
        """構築"""
        self.text = self.icon = None
        self.props("text-color=white")
        c = self.game.circular[self.y, self.x]
        color = self.colors.get(c, "red")
        self.props(f"text-color={color}")
        text = "⬤" if self.game.grid[self.y, self.x] else "╋"
        self.text = text


class Game:
    """ゲーム"""

    def __init__(self, *, grid_size: int, show_cache: bool = False) -> None:
        """初期化"""
        self.cache: dict[Feature, set[Point]] = {}
        self.show_cache = show_cache
        self.grid_size = grid_size
        self.grid = np.zeros((grid_size, grid_size), dtype=bool)
        self.circular = np.full_like(self.grid, 0, dtype=np.int8)
        with ui.row():
            ui.button("Restart", on_click=self.restart)
            self.label = ui.label()
        with ui.grid(columns=grid_size).classes("gap-0"):
            self.squares = [Square(self, y, x) for y in range(grid_size) for x in range(grid_size)]
        self.restart()

    def restart(self) -> None:
        """再ゲーム"""
        self.cache.clear()
        self.grid.fill(0)
        self.circular.fill(0)
        self.msg = "Click the grid."
        self.refresh()
        if self.show_cache:
            logger.debug("Restart")

    def point(self) -> int:
        """ポイント"""
        return self.grid.sum()

    def game_over(self) -> bool:
        """ゲームオーバーかどうかを返す"""
        return self.circular.any()

    def refresh(self) -> None:
        """再描画"""
        for square in self.squares:
            square.build()
        self.label.text = self.msg

    def click(self, y: int, x: int) -> None:
        """点を置く"""
        if self.grid[y, x] or self.game_over():
            return
        self.judge(y, x)
        self.grid[y, x] = True
        self.refresh()

    def judge(self, y: int, x: int) -> None:
        """判定"""
        found = set()
        n_found = 0
        indexes = [(j, i) for j, i in product(range(self.grid_size), range(self.grid_size)) if self.grid[j, i]]
        for k, (y0, x0) in enumerate(indexes):
            for y1, x1 in indexes[k + 1 :]:
                key = get_feature((x0, y0), (x1, y1), (x, y))  # 特徴計算時の引数のみx → yの順
                if key not in self.cache:
                    self.cache[key] = lst = set()
                else:
                    lst = self.cache[key]
                    found.add(key)
                    cur = len(found)
                    if n_found < cur:
                        n_found = cur
                        for j, i in lst:
                            self.circular[j, i] = n_found
                lst.add((y0, x0))
                lst.add((y1, x1))
                lst.add((y, x))
        if not found:
            self.msg = f"{self.point() + 1} points."
        else:
            self.circular[y, x] = LAST_CLICKED_COLOR
            status = f"({self.point() + 1} points, {n_found} circles)"
            if n_found == 1:
                self.msg, type_ = f"Failure {status}", "negative"
            else:
                self.msg, type_ = f"Success! {status}", "positive"
            ui.notify(self.msg, type=type_)
            if self.show_cache:
                for kv in self.cache.items():
                    logger.debug(kv)


def run_game(*, grid_size: int = 10, show_cache: bool = False, port: int | None = None) -> None:
    """ゲーム実行"""
    basicConfig(level=DEBUG, format="%(message)s")
    Game(grid_size=grid_size, show_cache=show_cache)
    ui.run(title="CoCircular", reload=False, port=port)
