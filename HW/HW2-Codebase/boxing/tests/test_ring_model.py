import pytest
from ..boxing.models.boxers_model import Boxer, update_boxer_stats
from boxing.models.ring_model import RingModel
from unittest.mock import patch

@pytest.fixture
def test_ring_model():
    return RingModel()


@pytest.fixture
def test_boxer_1():
    return Boxer(id=1, name="Boxer 1", age=30, weight=180, reach=72)


@pytest.fixture
def test_boxer_2():
    return Boxer(id=2, name="Boxer 2", age=28, weight=175, reach=70)


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
        ring_model.enter_ring(Boxer(id=3, name="Boxer 3", age=24, weight=185, reach=74))


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
    with patch("boxing.models.ring_model.get_random", return_value=0.1):
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
    skill = boxer_1.get_fighting_skill(boxer_1)
    expected_skill = (boxer_1.weight * len(boxer_1.name)) + (boxer_1.reach / 10) - 1
    assert skill == expected_skill


@patch("boxing.models.ring_model.update_boxer_stats")
def test_fight_update_stats(mock_update, ring_model, boxer_1, boxer_2):
    # Test that stats are updated after a fight
    ring_model.enter_ring(boxer_1)
    ring_model.enter_ring(boxer_2)

    # Mock the get_random function to control the randomness
    with patch("boxing.models.ring_model.get_random", return_value=0.1):
        winner = ring_model.fight()

    # Check that the update_boxer_stats was called
    mock_update.assert_any_call(boxer_1.id, "win")
    mock_update.assert_any_call(boxer_2.id, "loss")