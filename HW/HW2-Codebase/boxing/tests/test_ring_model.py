import pytest

from boxing.models.ring_model import RingModel
from boxing.models.boxers_model import Boxer


@pytest.fixture
def ring_model():
    return RingModel()


@pytest.fixture
def boxer_1():
    return Boxer(id=1, name="Boxer 1", age=30, weight=180, height=167, reach=72)


@pytest.fixture
def boxer_2():
    return Boxer(id=2, name="Boxer 2", age=28, weight=175, height=169, reach=70)


def test_enter_ring(ring_model, boxer_1):
    # Test adding a boxer to the ring
    ring_model.enter_ring(boxer_1)
    assert len(ring_model.ring) == 1
    assert ring_model.ring[0] == boxer_1


def test_enter_ring_full(ring_model, boxer_1, boxer_2):
    # Test adding more than 2 boxers to the ring (should raise an error)
    ring_model.enter_ring(boxer_1)
    ring_model.enter_ring(boxer_2)
    
    with pytest.raises(ValueError, match="Ring is full, cannot add more boxers."):
        ring_model.enter_ring(Boxer(id=3, name="Boxer 3", age=24, weight=185, height=170, reach=74))


def test_get_boxers_empty(ring_model):
    # Test getting boxers from an empty ring (should raise an error)
    with pytest.raises(ValueError, match="The boxing ring is empty."):
        ring_model.get_boxers()


def test_get_boxers(ring_model, boxer_1, boxer_2):
    # Test getting boxers when the ring has boxers
    ring_model.enter_ring(boxer_1)
    ring_model.enter_ring(boxer_2)
    boxers = ring_model.get_boxers()
    
    assert len(boxers) == 2
    assert boxers[0] == boxer_1
    assert boxers[1] == boxer_2


def test_fight(ring_model, boxer_1, boxer_2):
    # Test the fight function
    ring_model.enter_ring(boxer_1)
    ring_model.enter_ring(boxer_2)

    # Mock the get_random function to control the randomness
    winner = ring_model.fight()

    assert winner in [boxer_1.name, boxer_2.name]


def test_fight_not_enough_boxers(ring_model, boxer_1):
    # Test starting a fight with less than 2 boxers (should raise an error)
    ring_model.enter_ring(boxer_1)
    
    with pytest.raises(ValueError, match="There must be two boxers to start a fight."):
        ring_model.fight()


def test_clear_ring(ring_model, boxer_1, boxer_2):
    # Test clearing the ring
    ring_model.enter_ring(boxer_1)
    ring_model.enter_ring(boxer_2)

    # Verify ring has boxers
    assert len(ring_model.ring) == 2

    # Call clear_ring and check if the ring is empty
    ring_model.clear_ring()
    assert len(ring_model.ring) == 0


def test_get_fighting_skill(boxer_1):
    # Test calculating a boxer's fighting skill
    ring_model = RingModel()  # Create an instance of RingModel
    skill = ring_model.get_fighting_skill(boxer_1)  # Call method on instance
    
    expected_skill = (boxer_1.weight * len(boxer_1.name)) + (boxer_1.reach / 10)
    assert skill == expected_skill
