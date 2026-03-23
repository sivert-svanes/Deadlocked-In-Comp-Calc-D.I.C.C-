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
        if team == Teams.ARCH_MOTHER:
            if len(User.Arch_Mother) >= 5:
                print("Arch Mother team is full. Cannot add more members.")
                return
        elif team == Teams.HIDDEN_KING:
            if len(User.Hidden_King) >= 5:
                print("Hidden King team is full. Cannot add more members.")
                return
        if self not in User.Arch_Mother and self not in User.Hidden_King:
            if team == Teams.ARCH_MOTHER:
                User.Arch_Mother.add(self)
                print("Added to team Arch Mother:", self.character.name)
            elif team == Teams.HIDDEN_KING:
                User.Hidden_King.add(self)
                print("Added to team Hidden King:", self.character.name)
            else:
                raise ValueError("Invalid team name. Must be 'Arch Mother' or 'Hidden King'.")
    def check_team_membership(self) -> Teams:
        if self in User.Arch_Mother:
            return Teams.ARCH_MOTHER
        elif self in User.Hidden_King:
            return Teams.HIDDEN_KING
        else:
            raise ValueError("Not part off any team.")
    def is_fed_calc(self, debug = False) -> None:
        selfkda = (self.kills + (self.assists / 2)) / max(1, self.deaths)  # Avoids division by zero
        team_check = self.check_team_membership()
        team_variable = User.Arch_Mother if team_check == Teams.ARCH_MOTHER else User.Hidden_King
        teammates = [user for user in team_variable if user is not self]
        if len(teammates) == 0:
            raise ValueError(f"No teammates to compare for {self.character.name}.")

        total_kda = 0
        team_avg_kda = 0
        for user in teammates:
            user_kda = (user.kills + (user.assists / 2)) / max(1, user.deaths)
            total_kda += user_kda
            team_avg_kda = total_kda / len(teammates)
        if debug == True:
            print(f"Total KDA: {total_kda}")
            print(f"Team Average KDA: {team_avg_kda}")
            print(f"{self.character.name}'s KDA: {selfkda}")

        if selfkda > team_avg_kda:
            print(f"{self.character.name} is fed with a KDA of {selfkda:.2f} compared to the team average of {team_avg_kda:.2f}.")
        elif selfkda < team_avg_kda:
            print(f"{self.character.name} is not fed with a KDA of {selfkda:.2f} compared to the team average of {team_avg_kda:.2f}.")

    @classmethod
    def check_team_characters(cls, team: Teams) -> None:
        if team == Teams.ARCH_MOTHER:
            team_list = [user.character.name for user in cls.Arch_Mother]
            print("Arch Mommy Supporters:", team_list)
        elif team == Teams.HIDDEN_KING:
            team_list = [user.character.name for user in cls.Hidden_King]
            print("Hidden Daddy Supporters:", team_list)
        else:
            raise ValueError("Invalid team name. Must be 'Arch Mother' or 'Hidden King'.")

