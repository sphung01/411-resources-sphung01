from contextlib import contextmanager
import re
import sqlite3

import pytest

from boxing.models.boxers_model import (
    Boxer,
    create_boxer,
    delete_boxer,
    get_leaderboard,
    get_boxer_by_id,
    get_boxer_by_name,
    get_weight_class,
    update_boxer_stats

)

######################################################
#
#    Fixtures
#
######################################################

def normalize_whitespace(sql_query: str) -> str:
    return re.sub(r'\s+', ' ', sql_query).strip()

# Mocking the database connection for tests
@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    # Mock the connection's cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Default return for queries
    mock_cursor.fetchall.return_value = []
    mock_cursor.commit.return_value = None

    # Mock the get_db_connection context manager from sql_utils
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn  # Yield the mocked connection object

    mocker.patch("boxing.models.boxers_model.get_db_connection", mock_get_db_connection)

    return mock_cursor  # Return the mock cursor so we can set expectations per test

######################################################
#
#    Add and delete
#
######################################################

def test_create_boxer(mock_cursor):
    """ Testing adding a boxer """
    create_boxer(name="Boxer name", weight= 125, height=178, reach=2.0, age: 30)

    expected_query = normalize_whitespace("""
        INSERT INTO boxers (name, weight, height, reach, age)
        VALUES (?, ?, ?, ?, ?)
    """)

    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = ("Boxer Name", 125, 178, 2.0, 30)

    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_create_boxer_duplicate(mock_cursor):
    """Test creating a boxer with a duplicate name (should raise an error).

    """
    # Simulate that the database will raise an IntegrityError due to a duplicate entry
    mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed: boxer.name")

    with pytest.raises(ValueError, match="Boxer with name 'Boxer name' already exists."):
        create_boxer(name="Boxer name", weight= 125, height=178, reach=2.0, age: 30)

def test_create_boxer_invalid_weight():
    """Test error when trying to create a boxer with a invalid weight < 125

    """
    with pytest.raises(ValueError, match=r"Invalid weight: 115 \(must be greater than 125\)."):
        create_boxer(name="Boxer name", weight= 115, height=178, reach=2.0, age: 30)

    with pytest.raises(ValueError, match=r"Invalid weight: invalid \(must be a positive integer\)."):
        create_boxer(name="Boxer name", weight= -125, height=178, reach=2.0, age: 30)


def test_create_boxer_invalid_height():
    """Test error when trying to create a boxer with a invalid weight < 125

    """
    with pytest.raises(ValueError, match=r"Invalid height: -115 \(must be greater than 0\)."):
        create_boxer(name="Boxer name", weight= 125, height=-115, reach=2.0, age: 30)

    with pytest.raises(ValueError, match=r"Invalid height: invalid \(must be a positive integer\)."):
        create_boxer(name="Boxer name", weight= 125, height="Invalid", reach=2.0, age: 30)


def test_create_boxer_invalid_reach():
    """Test error when trying to create a boxer with a invalid reach <= 0

    """
    with pytest.raises(ValueError, match=r"Invalid reach: 0 \(must be greater than 0\)."):
        create_boxer(name="Boxer name", weight= 125, height=178, reach=0, age: 30)

    with pytest.raises(ValueError, match=r"Invalid reach: invalid \(must be a positive integer\)."):
        create_boxer(name="Boxer name", weight= 125, height=170, reach=-5, age: 30)

def test_create_boxer_invalid_age():
    """Test error when trying to create a boxer with a invalid age < 18

    """
    with pytest.raises(ValueError, match=r"Invalid age: 17 \(must be greater than 17\)."):
        create_boxer(name="Boxer name", weight= 125, height=178, reach=2.0, age: 17)

    with pytest.raises(ValueError, match=r"Invalid age: invalid \(age must be less than equal to 40\)."):
        create_boxer(name="Boxer name", weight= 125, height=170, reach=-2.0, age: 60)

def test_delete_boxer(mock_cursor):
    """Test deleting a boxer from the table by boxer ID.

    """
    # Simulate the existence of a boxer w/ id=1
    # We can use any value other than None
    mock_cursor.fetchone.return_value = (True)

    delete_boxer(1)

    expected_select_sql = normalize_whitespace("SELECT id FROM boxers WHERE id = ?")
    expected_delete_sql = normalize_whitespace("DELETE FROM boxers WHERE id = ?")

    # Access both calls to `execute()` using `call_args_list`
    actual_select_sql = normalize_whitespace(mock_cursor.execute.call_args_list[0][0][0])
    actual_delete_sql = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    assert actual_select_sql == expected_select_sql, "The SELECT query did not match the expected structure."
    assert actual_delete_sql == expected_delete_sql, "The UPDATE query did not match the expected structure."

    # Ensure the correct arguments were used in both SQL queries
    expected_select_args = (1,)
    expected_delete_args = (1,)

    actual_select_args = mock_cursor.execute.call_args_list[0][0][1]
    actual_delete_args = mock_cursor.execute.call_args_list[1][0][1]

    assert actual_select_args == expected_select_args, f"The SELECT query arguments did not match. Expected {expected_select_args}, got {actual_select_args}."
    assert actual_delete_args == expected_delete_args, f"The UPDATE query arguments did not match. Expected {expected_delete_args}, got {actual_delete_args}."

def test_delete_boxer_bad_id(mock_cursor):
    """Test error when trying to delete a non-existent Boxer id.

    """
    # Simulate that no boxer exists with the given ID
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Boxer with ID 900800 not found"):
        delete_song(900800)


def test_get_leaderboards(mock_cursor):
    """Test retrieving the current leaderboard.

    """
    mock_cursor.fetchall.return_value = [
        (1, "Boxer A", 125, 178, 2.0, 30, 1, 2,False),
        (2, "Boxer B", 130, 179, 2.1, 32, 3, 3, False),
        (3, "Boxer C", 135, 180, 2.2, 32, 5, 1, False)
    ]

    leaderboard = get_leaderboard()

    expected_result = [
        {"id": 1, "boxer": "Boxer A", "weight": 125, "height": 178, "age": 30, "wins": 210, "play_count": 10},
        {"id": 2, "boxer": "Boxer B", "weight": 130, "height": 179, "age": 32, "wins": 180, "play_count": 20},
        {"id": 3, "boxer": "Boxer C", "weight": 135, "height": 180, "age": 32, "duration": 200, "play_count": 5}
    ]

    assert leaderboard == expected_result, f"Expected {expected_result}, but got {songs}"

    expected_query = normalize_whitespace("""
        SELECT id, name, weight, height, reach, age, fights, wins,
               (wins * 1.0 / fights) AS win_pct
        FROM boxers
        WHERE fights > 0
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."


    ######################################################
#
#    Get Boxer
#
######################################################


def test_get_boxer_by_id(mock_cursor):
    """Test getting a boxer by id.

    """
    mock_cursor.fetchone.return_value = (1, "Boxer Name", 125, 178, 2.0, 30, False)

    result = get_boxer_by_id(1)

    expected_result = Boxer(1, "Boxer Name", 125, 178, 2.0, 30)

    assert result == expected_result, f"Expected {expected_result}, got {result}"

    expected_query = normalize_whitespace(" SELECT id, name, weight, height, reach, age FROM boxers WHERE id = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = (1,)

    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


def test_get_boxer_by_id_bad_id(mock_cursor):
    """Test error when getting a non-existent boxer.

    """
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Boxer with ID 900800 not found"):
        get_song_by_id(900800)




def test_get_boxer_by_name(mock_cursor):
    """Test getting a boxer by name.

    """
    mock_cursor.fetchone.return_value = (1, "Boxer Name", 125, 178, 2.0, 30, False)

    result = get_boxer_by_name("Boxer Name")

    expected_result = Boxer(1, "Boxer Name", 125, 178, 2.0, 30)

    assert result == expected_result, f"Expected {expected_result}, got {result}"

    expected_query = normalize_whitespace("SELECT id, name, weight, height, reach, age FROM boxers WHERE name = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = ("Boxer Name",)

    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


def test_get_boxer_by_name_bad_name(mock_cursor):
    """Test error when getting a non-existent boxer.

    """
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Boxer with name 900 not found"):
        get_song_by_id("900")


######################################################
#
#    Update stats
#
######################################################


def test_update_play_count(mock_cursor):
    """Test updating the play count of a song.

    """
    mock_cursor.fetchone.return_value = True

    song_id = 1
    update_play_count(song_id)

    expected_query = normalize_whitespace("""
        UPDATE songs SET play_count = play_count + 1 WHERE id = ?
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args_list[1][0][1]
    expected_arguments = (song_id,)

    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


