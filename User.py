from App import Character


class User:

    Arch_Mother: set["User"] = set()
    Hidden_King: set["User"] = set()

    def __init__ (self, character: Character, kills: int = 0, deaths: int = 0, assists: int = 0):
        if not character:
            raise ValueError("Character cannot be None")

        self.character = character
        self.kills = kills
        self.deaths = deaths
        self.assists = assists


    def character_score_calculator(self):
        return

    def add_to_team(self, team_name: str) -> None:
        if self not in User.Arch_Mother and self not in User.Hidden_King:
            if team_name == "Arch Mother":
                User.Arch_Mother.add(self)
            elif team_name == "Hidden King":
                User.Hidden_King.add(self)
            else:
                raise ValueError("Invalid team name. Must be 'Arch Mother' or 'Hidden King'.")

    @classmethod
    def check_team_characters(cls, team_name: str) -> list[str]:
        if team_name == "Arch Mother":
            return [user.character.name for user in cls.Arch_Mother]
        if team_name == "Hidden King":
            return [user.character.name for user in cls.Hidden_King]
        raise ValueError("Invalid team name. Must be 'Arch Mother' or 'Hidden King'.")

