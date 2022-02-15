

SCORD_LOG_FILE=./cmds.log
export SCORD_LOG_FILE

DELIM="@%@%"


shuid(){
  # Generate a short guid
  uuidgen | cut -d'-' -f1
}


get_last_command(){
#  echo foo
  if [ -n "$ZSH_VERSION" ]; then
    history -1 | awk '{$1=""; print $0}'
  elif [ -n "$BASH_VERSION" ]; then
    history 2 | sed '2q;d' | awk '{$1=""; print $0}'
  else
    echo "Unsupported shell"
  fi
}


before_cmd(){
    # We use this in a bash context, but in zsh its passed in
    in_exit_status=$?
    if [ $# -eq 0 ]; then
      exit_status="$in_exit_status"
    else
      exit_status="$1"
    fi


    save_history "$SCORD_ID" "$exit_status"

    # make a new id for the next command
    SCORD_CMD=$(shuid)
    export SCORD_ID="scord-$SCORD_SESSION-$SCORD_CMD"
}


save_history(){
  scord_id=$1
  exit_status=$2
  cmd=$(get_last_command)

  echo "$cmd$DELIM$scord_id$DELIM$exit_status" >> $SCORD_LOG_FILE
}


init_scord_bash(){
  export OLD_PROMPT_COMMAND="$PROMPT_COMMAND"
  export PROMPT_COMMAND="before_cmd; ${PROMPT_COMMAND}"
}


init_scord_zsh(){
  eval orig_"$(declare -f precmd)"
  export orig_precmd


  precmd(){
    # Get the last commands exit
    exit_status=$?

    before_cmd "$exit_status"

    orig_precmd
  }
}


init_poly(){
  if [ -n "$ZSH_VERSION" ]; then
     init_scord_zsh
  elif [ -n "$BASH_VERSION" ]; then
     init_scord_bash
  else
    echo "Unsupported shell"
  fi
}


if [ -z ${SCORD_INIT+x} ]; then
  echo "Setting up shellcord";
  export SCORD_INIT=1

  SCORD_SESSION="$(shuid)"
  export SCORD_SESSION

  # Make the ids for the next command run
  SCORD_CMD="$(shuid)"
  export SCORD_CMD

  init_poly

else
  echo "Shellcord is already setup, not initializing"
fi
