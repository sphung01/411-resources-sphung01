import logging
import math
from typing import List

from boxing.models.boxers_model import Boxer, update_boxer_stats
from boxing.utils.logger import configure_logger
from boxing.utils.api_utils import get_random


logger = logging.getLogger(__name__)
configure_logger(logger)


class RingModel:
    def __init__(self):
        """
        Automatically initalizes the ring object
        """
        self.ring: List[Boxer] = []

    def fight(self) -> str:
        """
        Path Parameter:
            - self: An object that has its own ring data

        Returns: 
            - The winner in the fight 

        Raises:
            - If there are more than 2 boxers in the ring

        """
        if len(self.ring) < 2:
            raise ValueError("There must be two boxers to start a fight.")

        boxer_1, boxer_2 = self.get_boxers()

        skill_1 = self.get_fighting_skill(boxer_1)
        skill_2 = self.get_fighting_skill(boxer_2)

        # Compute the absolute skill difference
        # And normalize using a logistic function for better probability scaling
        delta = abs(skill_1 - skill_2)
        normalized_delta = 1 / (1 + math.e ** (-delta))

        logger.info(f"Generating random number")
        random_number = get_random()

        if random_number < normalized_delta:
            winner = boxer_1
            loser = boxer_2
            logger.info(f"{boxer_2.name} lost! {boxer_1.name} is the winner!")
        else:
            winner = boxer_2
            loser = boxer_1
            logger.info(f"{boxer_1.name} lost! {boxer_2.name} is the winner!")

        logger.info(f"Updating both of the boxers' stats...")
        update_boxer_stats(winner.id, 'win')
        update_boxer_stats(loser.id, 'loss')
        logger.info(f"Record updated!")

        logger.info(f"Clearing the ring...")
        self.clear_ring()
        logger.info(f"Ring is now cleared!")

        return winner.name

    def clear_ring(self):
        if not self.ring:
            return
        self.ring.clear()

    def enter_ring(self, boxer: Boxer):
        if not isinstance(boxer, Boxer):
            raise TypeError(f"Invalid type: Expected 'Boxer', got '{type(boxer).__name__}'")

        if len(self.ring) >= 2:
            raise ValueError("Ring is full, cannot add more boxers.")

        self.ring.append(boxer)

    def get_boxers(self) -> List[Boxer]:
        """
        Path Parameter:
            get_boxer (self) Takes in the ring object

        Returns:
            List of boxers in the ring
            
        Raises:
            Error if the boxing ring is empty
        """
        if not self.ring:
            pass
        else:
            pass

        return self.ring

    def get_fighting_skill(self, boxer: Boxer) -> float:
        # Arbitrary calculations
        age_modifier = -1 if boxer.age < 25 else (-2 if boxer.age > 35 else 0)
        skill = (boxer.weight * len(boxer.name)) + (boxer.reach / 10) + age_modifier

        return skill
    
