from enum import Enum
from typing import Union, Tuple, Dict, Any
import App
from App import ItemType
from App import Character
"""""
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

#TODO legg til team i init og sjekk at det er gyldig, og legg til i teamet der, slipper å kalle add_to_team etterpå flere ganger

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
        else:
            print(f"{self.character.name} is already in a team. Cannot add to another team OR be added again.")

    def check_team_membership(self) -> Teams:
        if self in User.Arch_Mother:
            return Teams.ARCH_MOTHER
        elif self in User.Hidden_King:
            return Teams.HIDDEN_KING
        else:
            raise ValueError("Not part off any team.")

    def add_weight(self, itemType, updated_value, debug = False) -> None:
        old = self.character.typeWeights.get()
        print(f"Old weight for {itemType}: {old}")
        if old is None:
            print(f"[WARN] Missing key in typeWeights for {itemType} \-> creating with0.0")
            old = 0.0
        self.character.typeWeights[itemType] = old + updated_value
        if debug:
            print(f"Updated {itemType}: {old} \-> {self.character.typeWeights[itemType]}")

    def is_fed_calc(self, debug = False) -> None:
        global ctype
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

        if debug:
            print(f"Total KDA / All teammate KDA added upp: {total_kda:.2f}")
            print(f"Team Average KDA: {team_avg_kda:.2f}")
            print(f"{self.character.name}'s KDA: {selfkda:.2f}")
            print(f"Before Type Weights: {self.character.typeWeights}")

        ctype = self.character.characterType
        ctype_name = getattr(ctype, "name", str(ctype)).upper()

        if selfkda > team_avg_kda:
            if debug:
                print("got past the selfkda > team_avg_kda check")
            if ctype_name == "SUPPORT":
                if debug:
                    print(f"{self.character.name} is a support, so they get more sustain items.")
                self.add_weight(ItemType.SUSTAIN, 0.4, debug=debug)
            elif ctype_name == "TANK":
                if debug:
                    print(f"{self.character.name} is a tank, so they get more sustain and gun items.")
                self.add_weight(ItemType.SUSTAIN, 0.4, debug=debug)
                self.add_weight(ItemType.GUN, 0.4, debug=debug)
            elif ctype_name == "DPS":
                if debug:
                    print(f"{self.character.name} is a DPS, so they get more gun and spirit items.")
                self.add_weight(ItemType.GUN, 0.4, debug=debug)

            print(
                f"{self.character.name} is fed with a KDA of {selfkda:.2f} compared to the team average of {team_avg_kda:.2f}.")
        elif selfkda < team_avg_kda:
            self.add_weight(ItemType.SUSTAIN, 0.4, debug=debug)
            print(
                f"{self.character.name} is not fed with a KDA of {selfkda:.2f} compared to the team average of {team_avg_kda:.2f}.")
        if debug:
            print(f"After Type Weights: {self.character.typeWeights}")
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

"""""