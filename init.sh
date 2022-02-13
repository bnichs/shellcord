
#trap 'x=$?; echo "exit: $x" >> ./foo.log' DEBUG
#script --return -T timing.txt foo.log


LOG_FILE=./cmds.log


shuid(){
  # Generate a short guid
  uuidgen | cut -d'-' -f1
}


good_history(){
  scord_id=$1
  exit_status=$2

  echo "$scord_id: $exit_status" >> $LOG_FILE

#  echo "yay, exit: $exit_status" >> $LOG_FILE
#  if ((!exit_status)); then
#     history 1 >> history.txt
#  fi
}


export OLD_PROMPT_COMMAND="$PROMPT_COMMAND"

export PROMPT_COMMAND="good_history ${PROMPT_COMMAND}"


init_scord(){
  eval orig_"$(declare -f precmd)"

  SCORD_SESSION=$(shuid)

  precmd(){
    # Get the last commands exit
    exit_status=$?

    SCORD_CMD=$(shuid)
    SCORD_ID="scord-$SCORD_SESSION-$SCORD_CMD"

    good_history "$SCORD_ID" "$exit_status"
    orig_precmd
    echo "$SCORD_ID"
  }
}


if [ -z ${SCORD_INIT+x} ]; then
  echo "Setting up shellcord";
  export SCORD_INIT=1
  init_scord
else
  echo "Shellcord is already setup, not initializing"
fi


#trap "echo Hello" DEBUG
