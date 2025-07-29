from re import Pattern


class PreCondition:
    """
    Pre-condition that has to be meet before starting search for main pattern.

    Attributes
    ----------
    pattern:
        Pattern that has to be matched in order to fulfill condition.
    within:
        Only matches of the main pattern within the first n lines after meeting this condition are considered.
    per_match:
        Condition is reset after each match. For any following main match to be considered the condition first has to be met again first.
    """

    def __init__(
        self,
        pattern: str | Pattern[str],
        /,
        *,
        within: int | None = None,
        per_match: bool = False,
    ) -> None:
        """
        Pre-condition that has to be meet before starting search for main pattern.

        Parameters
        ----------
        pattern:
            Pattern that has to be matched in order to fulfill condition.
        within:
            Only matches of the main pattern within the first n lines after meeting this condition are considered.
        per_match:
            Condition is reset after each match. For any following main match to be considered the condition first has to be met again first.
        """
        self.pattern: str | Pattern[str] = pattern
        self.within: int | None = within
        self.per_match: bool = per_match
        self.condition_information: ConditionStatus = ConditionStatus()


class ConditionStatus:
    """Keeps track where the condition are found"""

    def __init__(self, condition_found: bool = False, line: str | None = None):
        self.condition_found = condition_found
        self.line = line

    def __bool__(self) -> bool:
        return self.condition_found
