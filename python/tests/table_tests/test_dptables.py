from __future__ import annotations

import unittest
from itertools import combinations_with_replacement
from typing import ClassVar

from phevaluator.tables import CHOOSE
from phevaluator.tables import DP
from phevaluator.tables import SUITS

MADE_HAND_CARD_COUNT = 5


class TestSuitsTable(unittest.TestCase):
    DP: ClassVar[list[int]] = [0] * len(SUITS)

    @classmethod
    def setUpClass(cls) -> None:
        for k in [5, 6, 7, 8, 9]:
            cls.update_k(cls.DP, k)

    @staticmethod
    def update_k(table: list[int], k: int) -> None:
        iterable = list(range(k + 1))
        combs = combinations_with_replacement(iterable, 3)

        for comb in combs:
            # comb is in lexicographically sorted order
            cnts = (comb[0], comb[1] - comb[0], comb[2] - comb[1], k - comb[2])
            for suit, cnt in enumerate(cnts):
                if cnt >= MADE_HAND_CARD_COUNT:
                    idx = (
                        0x1 * cnts[0] + 0x8 * cnts[1] + 0x40 * cnts[2] + 0x200 * cnts[3]
                    )

                    # TODO(@ohwi): Check these cases:
                    # https://github.com/HenryRLee/PokerHandEvaluator/issues/93
                    #   There exist three cases that idxes are same.
                    #   For two different cnts in case of k=9.
                    #   The cases are 72, 520, 576.
                    if idx in [72, 520, 576] and SUITS[idx] != suit + 1:
                        continue

                    table[idx] = suit + 1

    def test_suits_table(self) -> None:
        self.assertListEqual(self.DP, SUITS)


class TestChooseTable(unittest.TestCase):
    DP: ClassVar[list[list[int]]] = [
        [0] * len(CHOOSE[idx]) for idx in range(len(CHOOSE))
    ]
    VISIT: ClassVar[list[list[int]]] = [
        [0] * len(CHOOSE[idx]) for idx in range(len(CHOOSE))
    ]

    @classmethod
    def setUpClass(cls) -> None:
        for n, row in enumerate(CHOOSE):
            for r in range(len(row)):
                cls.nCr(n, r)

    @classmethod
    def nCr(cls, n: int, r: int) -> int:  # noqa: N802
        if n < r:
            return 0
        if r == 0:
            cls.DP[n][r] = 1
            return 1
        if cls.VISIT[n][r] == 0:
            cls.DP[n][r] = cls.nCr(n - 1, r) + cls.nCr(n - 1, r - 1)
            cls.VISIT[n][r] = 1
        return cls.DP[n][r]

    def test_choose_table(self) -> None:
        self.assertListEqual(self.DP, CHOOSE)


class TestDpTable(unittest.TestCase):
    DP: ClassVar[list[list[list[int]]]] = [
        [[0] * len(DP[i][j]) for j in range(len(DP[i]))] for i in range(len(DP))
    ]

    @classmethod
    def setUpClass(cls) -> None:
        cls.fill_table()

    @classmethod
    def fill_table(cls) -> None:
        # Recursion formula:
        # dp[l][i][j] = dp[l-1][i][j] + dp[1][i][j-l+1]
        #
        # We need base cases of dp[1][i][j] to calculate.
        #
        # Base cases:
        # dp[1][i][j] is something like combination with
        # replacement(iHj), but each bag cannot be bigger than 4.
        # (1) dp[1][1][j] = 1 for 0 <= j <= 4, 0 for j > 4
        #     dp[1][0][j] = 0 for i = 0 (invalid)
        # (2) dp[1][i>1][j] = SUM { dp[1][i-1][j-q] }
        #     for q from 0 to 4 where j-q >= 0.
        #     This is like setting the most left number to q.
        # We need (2) because of the restriction.

        # Make base cases
        for j in range(5):
            cls.DP[1][1][j] = 1
        for i in range(2, 14):
            for j in range(10):
                for q in range(5):
                    if j - q >= 0:
                        cls.DP[1][i][j] += cls.DP[1][i - 1][j - q]

        # Make recursion
        for l in range(2, 5):
            for i in range(14):
                for j in range(10):
                    cls.DP[l][i][j] = cls.DP[l - 1][i][j]
                    if j - l + 1 >= 0:
                        cls.DP[l][i][j] += cls.DP[1][i][j - l + 1]

    def test_dp_table(self) -> None:
        self.assertListEqual(self.DP, DP)


if __name__ == "__main__":
    unittest.main()
