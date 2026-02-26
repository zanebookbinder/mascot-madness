from dataclasses import dataclass


@dataclass
class FightResult:
    winner: str
    loser: str
    win_probability: int  # 0-100: how likely/dominant this outcome was
    narrative: str

    def __post_init__(self) -> None:
        if not 0 <= self.win_probability <= 100:
            raise ValueError(
                f"win_probability must be 0-100, got {self.win_probability}"
            )
        if not self.winner:
            raise ValueError("winner cannot be empty")
        if not self.loser:
            raise ValueError("loser cannot be empty")
        if not self.narrative:
            raise ValueError("narrative cannot be empty")
