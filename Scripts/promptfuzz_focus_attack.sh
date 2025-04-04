#!/bin/bash

PYTHON_SCRIPT="./Experiment/run.py"
PHASE="focus"
MODE="hijacking"
NO_MUTATE="False"
ALL_DEFENSES="True"
RETRIEVAL_METHOD="cluster"
CLUSTER_NUM=5
THRESHOLD_COEFFICIENT=0.5
FEW_SHOT="True"
DYNAMIC_ALLOCATE="True"
FEW_SHOT_NUM=3
MUTATOR_WEIGHTS_HIJACKING=(0.21 0.23 0.13 0.23 0.2)
MUTATOR_WEIGHTS_EXTRATION=(0.1 0.1 0.4 0.2 0.2)

# Check if NO_MUTATE, ALL_DEFENSES, FEW_SHOT, and DYNAMIC_ALLOCATE should be set to true
NO_MUTATE_FLAG=""
ALL_DEFENSES_FLAG=""
FEW_SHOT_FLAG=""
DYNAMIC_ALLOCATE_FLAG=""
MUTATOR_WEIGHTS=""

if [ "$NO_MUTATE" = "True" ]; then
  NO_MUTATE_FLAG="--no_mutate"
fi

if [ "$ALL_DEFENSES" = "True" ]; then
  ALL_DEFENSES_FLAG="--all_defenses"
fi

if [ "$FEW_SHOT" = "True" ]; then
  FEW_SHOT_FLAG="--few_shot"
fi

if [ "$DYNAMIC_ALLOCATE" = "True" ]; then
  DYNAMIC_ALLOCATE_FLAG="--dynamic_allocate"
fi

if [ "$MODE" = "hijacking" ]; then
  MUTATOR_WEIGHTS=${MUTATOR_WEIGHTS_HIJACKING[@]}
else
  MUTATOR_WEIGHTS=${MUTATOR_WEIGHTS_EXTRATION[@]}
fi


# Set the log path
LOG_PATH="Logs/${PHASE}/${MODE}"

MODEL_PATH="meta-llama/Llama-3.3-70B-Instruct"
SERVER_URL="http://localhost:54321/v1"

# Create the log directory if it does not exist
mkdir -p "$LOG_PATH"

# Run the Python script
CUDA_VISIBLE_DEVICES=0 python -u "$PYTHON_SCRIPT" --phase $PHASE --mode $MODE $NO_MUTATE_FLAG $ALL_DEFENSES_FLAG $FEW_SHOT_FLAG $DYNAMIC_ALLOCATE_FLAG --retrieval_method $RETRIEVAL_METHOD --cluster_num $CLUSTER_NUM --threshold_coefficient $THRESHOLD_COEFFICIENT --few_shot_num $FEW_SHOT_NUM --mutator_weights $MUTATOR_WEIGHTS --model_path $MODEL_PATH --server_url $SERVER_URL > "${LOG_PATH}/all_defenses.log" 2>&1

echo "All tasks finished."
