# Shellcord
Generate runbooks and READMEs from your shell sessions.




## Installation

## Usage


## Supported platforms
Note that this tool is in alpha and still not thoroughly tested on shells/platforms besides the following:
### Python
* 3.7
* 3.9
### Operating systems
* Linux `5.11.0-49-generic x86_64 GNU/Linux `

### Shells
Confirmed working in:
* zsh: `zsh 5.8 (x86_64-ubuntu-linux-gnu)`
* bash: `GNU bash, version 5.1.4(1)-release (x86_64-pc-linux-gnu)`



### Limitations
Ideally, this tool would be a simple invocation of [script](https://man7.org/linux/man-pages/man1/script.1.html) with some logic to generate a runbook from that typescript file. However, given that `script` only uses a psuedo-terminal, getting the exit code is non-trivial without basically making your own shell. So we do the next best thing and use each individual shells `precmd/PROMPT_COMMAND` instead. 

Currently, shellcord collects:
* The command being run
* The exit code of that command

Ideally though, it would also be able to get stdout so the generated runbook has example output.

## Development
This tool is currently under development and any support is more than welcome, especially if you want to get shellcord working in your shell of choice.

Please cut issues as you see fit based on usage and feel free to send pull-requests.

### Testing 
Run the tests `poetry run python3 -m pytest`



### How it works
Shellcord works by modifying the shell's `precmd/PROMP_COMMAND` or whatever equivalent with our own function which will:
* Generate a unique id for each command
* Get the exit code of the last command run
* Get the actual command which was run last
* Dump all that data to a `scord-log` file

Once all the command data has been collected, shellcord will then use the `scord-log` file to generate a runbook based on the parameters selected.


### Components
* init.sh: Used to setup a scord session and modify precmd
* de-init.sh: Used to close the session and undo all the precmd work 
* shellcord.py: Used to generate runbooks and tag commands