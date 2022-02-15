



deinit_zsh(){
  # Replace the temp function name with the original: precmd
  new_pre_cmd_text=$(declare -f orig_precmd | sed  "1s/orig_//")
  eval "$new_pre_cmd_text"
}

deinit_bash(){
  export PROMPT_COMMAND="$OLD_PROMPT_COMMAND"
  unset OLD_PROMPT_COMMAND
}


deinit_poly(){
  if [ -n "$ZSH_VERSION" ]; then
     deinit_zsh
  elif [ -n "$BASH_VERSION" ]; then
     deinit_bash
  else
    echo "Unsupported shell"
  fi
}


save_log(){
  log_loc="scord-$SCORD_SESSION.csv"
  echo "Saving log file to $log_loc"

  mv "$SCORD_LOG_FILE" "$log_loc"
}


if [ -z ${SCORD_INIT+x} ]; then
  echo "Shellcord is not setup, nothing to de-init";
#  export SCORD_INIT=1
else
  echo "Shutting down shellcord..."
  deinit_poly
#  exit # Exit the script session

  save_log
fi



# The script was called, so clean ourselves up regardless of previous run state
unset SCORD_INIT
unset SCORD_CMD
unset SCORD_SESSION
