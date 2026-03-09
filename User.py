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
        if team_name == "Arch Mother":
            User.Arch_Mother.add(self)
        elif team_name == "Hidden King":
            User.Hidden_King.add(self)
        else:
            raise ValueError("Invalid team name. Must be 'Arch Mother' or 'Hidden King'.")


    