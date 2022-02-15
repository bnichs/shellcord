



deinit(){
  # Replace the temp function name with the original: precmd
  new_pre_cmd_text=$(declare -f orig_precmd | sed  "1s/orig_//")
  eval "$new_pre_cmd_text"
}



if [ -z ${SCORD_INIT+x} ]; then
  echo "Shellcord is not setup, nothing to de-init";
#  export SCORD_INIT=1
else
  echo "Shutting down shellcord..."
  unset SCORD_INIT
  unset SCORD_CMD
  unset SCORD_SESSION
  deinit
#  exit # Exit the script session
fi


unset SCORD_INIT
unset SCORD_CMD
unset SCORD_SESSION

#trap - DEBUG
#
#echo "Exited"
#
#exit

#trap 'x=$?; echo "exit: $x" >> ./foo.log' DEBUG
#script --return -T timing.txt foo.log


#trap "echo Hello" DEBUG
