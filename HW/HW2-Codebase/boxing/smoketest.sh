#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5000/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done


###############################################
#
# Health checks
#
###############################################

# Function to check the health of the service
check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

# Function to check the database connection
check_db() {
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Database connection is healthy."
  else
    echo "Database check failed."
    exit 1
  fi
}

##########################################################
#
# Boxer Management
#
##########################################################

create_boxer() {
  name=$1
  weight=$2
  height=$3
  reach=$4
  age=$5

    echo "Creating boxer ($name)..."
  response=$(curl -s -X POST "$BASE_URL/create-boxer" \
    -H "Content-Type: application/json" \
    -d "{\"name\":\"$name\", \"weight\":$weight, \"height\":$height, \"reach\":$reach, \"age\":$age}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer created successfully: $name."
    if [ "$ECHO_JSON" = true ]; then echo "$response" | jq .; fi
  else
    echo "Failed to create boxer: $name."
    exit 1
  fi

}

delete_boxer() {
  boxer_id=$1

  echo "Deleting boxer by ID ($boxer_id)..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-boxer/$boxer_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer deleted successfully by ID ($boxer_id)."
  else
    echo "Failed to delete boxer by ID ($boxer_id)."
    exit 1
  fi
}

get_boxer_by_id() {
    boxer_id=$1

  echo "Getting boxer by ID ($boxer_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-boxer/$boxer_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer retrieved successfully by ID ($boxer_id)."
    if [ "$ECHO_JSON" = true ]; then echo "$response" | jq .; fi
  else
    echo "Failed to get boxer by ID ($boxer_id)."
    exit 1
  fi
}

get_boxer_by_name() {
  name=$1

  echo "Getting boxer by name ($name)..."
  response=$(curl -s -X GET "$BASE_URL/get-boxer-by-name/$name")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer retrieved successfully by name ($name)."
    if [ "$ECHO_JSON" = true ]; then echo "$response" | jq .; fi
  else
    echo "Failed to get boxer by name ($name)."
    exit 1
  fi
}


get_boxer_leaderboard() {
  sort_by=$1

  echo "Getting boxer leaderboard sorted by $sort_by..."
  response=$(curl -s -X GET "$BASE_URL/boxer-leaderboard?sort_by=$sort_by")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Leaderboard retrieved successfully (sorted by $sort_by)."
    if [ "$ECHO_JSON" = true ]; then echo "$response" | jq .; fi
  else
    echo "Failed to retrieve boxer leaderboard."
    exit 1
  fi
}

update_boxer_stats() {
  boxer_id=$1
  result=$2

  echo "Updating boxer ID $boxer_id with result: $result..."
  response=$(curl -s -X POST "$BASE_URL/update-boxer-stats" \
    -H "Content-Type: application/json" \
    -d "{\"boxer_id\": $boxer_id, \"result\": \"$result\"}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer stats updated successfully for ID $boxer_id."
    if [ "$ECHO_JSON" = true ]; then echo "$response" | jq .; fi
  else
    echo "Failed to update boxer stats for ID $boxer_id."
    exit 1
  fi

}


# Initialize the database
sqlite3 db/playlist.db < sql/init_db.sql

# Health checks
check_health
check_db


# Create boxers
create_boxer "Claressa Shields" 215 180 2.0 35
create_boxer "Katie Taylor" 210 171 2.1 32
create_boxer "Yakosta Valla" 155 178 2.0 30
create_boxer "Savannah Marshall" 155 175 1.9 33
create_boxer "Amanda Serrano" 200 150 2.2 29

# delete boxer 
delete_boxer_by_id 1

# get boxer by id
get_boxer_by_id 2
# get boxer by name
get_boxer_by_name "Amanda Serrano"

# update boxer stats
update_boxer_stats 2 win
update_boxer_stats 3 loss

# leaderboard
get_boxer_leaderboard "wins"
get_boxer_leaderboard "win_pct"