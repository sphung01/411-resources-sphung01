#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5050/api"

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
# Health Checks
###############################################

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

###############################################
# Boxer Management
###############################################

create_boxer() {
  name=$1
  weight=$2
  height=$3
  reach=$4
  age=$5

  echo "Creating boxer ($name)..."
  response=$(curl -s -X POST "$BASE_URL/add-boxer" \
    -H "Content-Type: application/json" \
    -d "{\"name\":\"$name\", \"weight\":$weight, \"height\":$height, \"reach\":$reach, \"age\":$age}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer created: $name"
    if [ "$ECHO_JSON" = true ]; then echo "$response" | jq .; fi
  else
    echo "Failed to create boxer: $name"
    exit 1
  fi
}



delete_boxer() {
  boxer_id=$1
  echo "Deleting boxer by ID ($boxer_id)..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-boxer/$boxer_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer deleted: ID $boxer_id"
  else
    echo "Failed to delete boxer ID $boxer_id"
    exit 1
  fi
}

get_boxer_by_id() {
  boxer_id=$1
  echo "Getting boxer by ID ($boxer_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-boxer-by-id/$boxer_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer retrieved by ID $boxer_id"
    if [ "$ECHO_JSON" = true ]; then echo "$response" | jq .; fi
  else
    echo "Failed to retrieve boxer by ID $boxer_id"
    exit 1
  fi
}

get_boxer_by_name() {
  name=$1
  echo "Getting boxer by name ($name)..."
  response=$(curl -s -X GET "$BASE_URL/get-boxer-by-name/$name")
  
  echo $response
 
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer retrieved: $name"
    if [ "$ECHO_JSON" = true ]; then echo "$response" | jq .; fi
  else
    echo "Failed to retrieve boxer by name $name"
    exit 1
  fi
}

####### RING
######## RING
fight(){
  ring=$1
  echo "Starting the match"
  response=$(curl -s -X GET "$BASE_URL/fight")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Match ended successfully"
    if [ "$ECHO_JSON" = true ]; then echo "$response" | jq .; fi
  else
    echo "Failed to trigger fight"
    exit 1
  fi
}

clear_boxers(){
  echo "Clearing all boxers from the ring..."
  response=$(curl -s -X POST "$BASE_URL/clear-boxers")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Ring cleared successfully"
    if [ "$ECHO_JSON" = true ]; then echo "$response" | jq .; fi
  else
    echo "Failed to clear ring"
    exit 1
  fi
}

enter_ring(){
  boxer=$1
  echo "Boxer: $boxer is entering the ring..."
  response=$(curl -s -X POST "$BASE_URL/enter-ring" \
    -H "Content-Type: application/json" \
    -d "{\"name\":\"$boxer\"}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer $boxer entered the ring successfully"
    if [ "$ECHO_JSON" = true ]; then echo "$response" | jq .; fi
  else
    echo "Failed to enter boxer $boxer into the ring"
    exit 1
  fi
}

get_boxers(){
  echo "Retrieving boxers in the ring..."
  response=$(curl -s -X GET "$BASE_URL/get-boxers")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Retrieved boxers successfully"
    if [ "$ECHO_JSON" = true ]; then echo "$response" | jq .; fi
  else
    echo "Failed to retrieve boxers"
    exit 1
  fi
}



#####Leaderboard
get_boxer_leaderboard() {
  sort_by=$1
  echo "Getting leaderboard sorted by $sort_by..."
  response=$(curl -s -X GET "$BASE_URL/leaderboard?sort=$sort_by")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Leaderboard sorted by $sort_by:"
    if [ "$ECHO_JSON" = true ]; then echo "$response" | jq .; fi
  else
    echo "Failed to retrieve leaderboard sorted by $sort_by"
    exit 1
  fi
}

###############################################
# Smoke Test Execution
###############################################

check_health
check_db

# Create boxers
create_boxer "Claressa Shields" 215 180 2.0 35
create_boxer "Katie Taylor" 210 171 2.1 32
create_boxer "Yakosta Valla" 155 178 2.0 30
create_boxer "Savannah Marshall" 155 175 1.9 33
create_boxer "Amanda Serrano" 200 150 2.2 29

# Delete boxer by ID
delete_boxer 1

# Get boxer by ID and name
get_boxer_by_id 2
get_boxer_by_name "Katie%20Taylor"

clear_boxers

enter_ring "Katie%20Taylor"
enter_ring "Claressa%20Shields"
fight
get_boxers
# Leaderboard sorting
get_boxer_leaderboard "wins"
get_boxer_leaderboard "win_pct"


echo " All smoketest pass!"
