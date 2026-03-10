from enum import Enum

from App import Character

class Teams(Enum):
    ARCH_MOTHER = 1
    HIDDEN_KING = 2
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

    def add_to_team(self, team: Teams) -> None:
        if self not in User.Arch_Mother and self not in User.Hidden_King:
            if team == Teams.ARCH_MOTHER:
                User.Arch_Mother.add(self)
                print("Added to team Arch Mother:", self.character.name)
            elif team == Teams.HIDDEN_KING:
                User.Hidden_King.add(self)
                print("Added to team Hidden King:", self.character.name)
            else:
                raise ValueError("Invalid team name. Must be 'Arch Mother' or 'Hidden King'.")

    @classmethod
    def check_team_characters(cls, team: Teams) -> None:
        if team == Teams.ARCH_MOTHER:
            team_list = [user.character.name for user in cls.Arch_Mother]
            print("Arch Mother Mommy Supporters:", team_list)
        elif team == Teams.HIDDEN_KING:
            team_list = [user.character.name for user in cls.Hidden_King]
            print("Hidden King Daddy Supporters:", team_list)
        else:
            raise ValueError("Invalid team name. Must be 'Arch Mother' or 'Hidden King'.")

