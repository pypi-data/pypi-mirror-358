"""円や直線の特徴量のクラス

CircularFeature: 円の特徴量。外心の中心と半径の2乗
LineFeature: 直線の特徴量。直線の係数
"""

import math
from dataclasses import dataclass
from fractions import Fraction

import numpy as np


@dataclass(frozen=True)
class LineFeature:
    """a + x + b * y + c == 0"""

    a: int
    b: int
    c: int

    def __repr__(self) -> str:
        """文字列化"""
        return f"{self.a} * x + {self.b} * y + {self.c} == 0"


@dataclass(frozen=True)
class CircularFeature:
    """外心の中心と半径の2乗"""

    center_x: Fraction
    center_y: Fraction
    radius2: Fraction

    def __repr__(self) -> str:
        """文字列化"""
        return f"({float(self.center_x):.2f}, {float(self.center_y):.2f}): {self.radius2**0.5:.2f}"


type Point = tuple[int, int]
type Feature = LineFeature | CircularFeature


def get_feature(p0: Point, p1: Point, p2: Point) -> Feature:
    """特徴量を返す"""
    if p0 == p1 or p2 in {p0, p1}:
        msg = "Three points must be different."
        raise ValueError(msg)
    if (p1[1] - p0[1]) * (p2[0] - p0[0]) == (p2[1] - p0[1]) * (p1[0] - p0[0]):
        return get_line_feature(p0, p1)
    return get_circular_feature(p0, p1, p2)


def get_line_feature(p0: Point, p1: Point) -> LineFeature:
    """直線の特徴量を返す"""
    a = p1[1] - p0[1]
    b = p0[0] - p1[0]
    c = -a * p0[0] - b * p0[1]
    common_divisor = math.gcd(math.gcd(a, b), c)
    if common_divisor:
        a //= common_divisor
        b //= common_divisor
        c //= common_divisor
    if a < 0 or (a == 0 and b < 0):
        a, b, c = -a, -b, -c
    return LineFeature(a, b, c)


def get_circular_feature(p0_: Point, p1_: Point, p2_: Point) -> CircularFeature:  # noqa: PLR0914
    """円の特徴量を返す"""
    # 計算しやすくするため多次元配列に変換
    p0 = np.array(p0_, dtype=np.int64)
    p1 = np.array(p1_, dtype=np.int64)
    p2 = np.array(p2_, dtype=np.int64)
    # 差分のノルム
    v01 = (p0 - p1) @ (p0 - p1)
    v12 = (p1 - p2) @ (p1 - p2)
    v20 = (p2 - p0) @ (p2 - p0)
    # 中間結果
    w01 = v01 * (v12 + v20 - v01)
    w12 = v12 * (v20 + v01 - v12)
    w20 = v20 * (v01 + v12 - v20)
    p0x, p0y = map(int, p0)
    w = int(w01 + w12 + w20)
    px, py = map(int, w12 * p0 + w20 * p1 + w01 * p2)
    # 中心
    cx = Fraction(px, w)
    cy = Fraction(py, w)
    # 半径の2乗
    radius2 = (cx - p0x) ** 2 + (cy - p0y) ** 2
    return CircularFeature(cx, cy, radius2)
