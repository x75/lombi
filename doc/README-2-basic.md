# List of orders in Terminal ( bash and shell) :


$ ls ( means show me the list of the files)
$ cd ( means show me the directory files)
$  ssh ( mean move to another main directory)
$ rmate ( run the code in the directory remotely)
$ mk dir ( make a new directory )

$ mv  ( mv is used to move one or more files or directories from one
-place to another in file system like UNIX. It has two distinct functions: (i) It rename a file or folder. (ii) It moves group of files to different directory.)

$ vim ( vim is a text editor that is upwards compatible to Vi. There are a lot of enhancements above Vi: multi level undo, multiple windows and buffers, syntax highlighting, command line editing, file name completion, a complete help system, visual selection, and others.)

$ mkdir (command to create a directory )

$ ^c  ( stop )

$ ssh  ((Secure Shell) is a network protocol that enables secure remote connections between two systems. System admins use SSH utilities to manage machines, copy, or move files between systems. Because SSH transmits data over encrypted channels, security is at a high level.)



$ cd work (command, also known as chdir (change directory), is a command-line shell command used to change the current working directory in various operating systems. It can be used in shell scripts and batch files.)

$ screen

Screen has the following command-line options:
-a
include all capabilities (with some minor exceptions) in each window's termcap, even if screen must redraw parts of the display in order to implement a function.
-A
Adapt the sizes of all windows to the size of the current terminal. By default, screen tries to restore its old window sizes when attaching to resizable terminals (those with "WS" in its description, e.g. suncmd or some xterm).
-c file
override the default configuration file from "$HOME/.screenrc" to file.
-d|-D [pid.tty.host]
does not start screen, but detaches the elsewhere running screen session. It has the same effect as typing "C-a d" from screen's controlling terminal. -D is the equivalent to the power detach key. If no session can be detached, this option is ignored. In combination with the -r/-R option more powerful effects can be achieved:
-d -r
Reattach a session and if necessary detach it first.
-d -R
Reattach a session and if necessary detach or even create it first.
-d -RR
Reattach a session and if necessary detach or create it. Use the first session if more than one session is available.
-D -r
Reattach a session. If necessary detach and logout remotely first.
-D -R
Attach here and now. In detail this means: If a session is running, then reattach. If necessary detach and logout remotely first. If it was not running create it and notify the user. This is the author's favorite.
-D -RR
Attach here and now. Whatever that means, just do it.
Note: It is always a good idea to check the status of your
sessions by means of "screen -list".
-e xy
specifies the command character to be x and the character generating a literal command character to y (when typed after the command character). The default is "C-a" and 'a', which can be specified as "-e^Aa". When creating a screen session, this option sets the default command character. In a multiuser session all users added will start off with this command character. But when attaching to an already running session, this option changes only the command character of the attaching user. This option is equivalent to either the commands "defescape" or "escape" respectively.
-f, -fn, and -fa
turns flow-control on, off, or "automatic switching mode". This can also be defined through the "defflow" .screenrc command.
-h num
Specifies the history scrollback buffer to be num lines high.

-i
will cause the interrupt key (usually C-c) to interrupt the display immediately when flow-control is on. See the "defflow" .screenrc command for details. The use of this option is discouraged.
-l and -ln
turns login mode on or off (for /etc/utmp updating). This can also be defined through the "deflogin" .screenrc command.
-ls and -list
does not start screen, but prints a list of pid.tty.host strings identifying your screen sessions. Sessions marked 'detached' can be resumed with "screen -r". Those marked 'attached' are running and have a controlling terminal. If the session runs in multiuser mode, it is marked 'multi'. Sessions marked as 'unreachable' either live on a different host or are 'dead'. An unreachable session is considered dead, when its name matches either the name of the local host, or the specified parameter, if any. See the -r flag for a description how to construct matches. Sessions marked as 'dead' should be thoroughly checked and removed. Ask your system administrator if you are not sure. Remove sessions with the -wipe option.
-L
tells screen to turn on automatic output logging for the windows.
-m
causes screen to ignore the $STY environment variable. With "screen -m" creation of a new session is enforced, regardless whether screen is called from within another screen session or not. This flag has a special meaning in connection with the '-d' option:
-d
-m Start screen in "detached" mode. This creates a new session but doesn't attach to it. This is useful for system startup scripts.
-D -m This also starts screen in "detached" mode, but doesn't fork a new process. The command exits if the session terminates.
-O selects a more optimal output mode for your terminal rather than true VT100 emulation (only affects auto-margin terminals without 'LP'). This can also be set in your .screenrc by specifying 'OP' in a "termcap" command.
-p number_or_name
Preselect a window. This is usefull when you want to reattach to a specific windor or you want to send a command via the "-X" option to a specific window. As with screen's select commant, "-" selects the blank window. As a special case for reattach, "=" brings up the windowlist on the blank window.
-q
Suppress printing of error messages. In combination with "-ls" the exit value is as follows: 9 indicates a directory without sessions. 10 indicates a directory with running but not attachable sessions. 11 (or more) indicates 1 (or more) usable sessions. In combination with "-r" the exit value is as follows: 10 indicates that there is no session to resume. 12 (or more) indicates that there are 2 (or more) sessions to resume and you should specify which one to choose. In all other cases "-q" has no effect.
-r [pid.tty.host]
-r sessionowner/[pid.tty.host]
resumes a detached screen session. No other options (except combinations with -d/-D) may be specified, though an optional prefix of [pid.]tty.host may be needed to distinguish between multiple detached screen sessions. The second form is used to connect to another user's screen session which runs in multiuser mode. This indicates that screen should look for sessions in another user's directory. This requires setuid-root.
-R
attempts to resume the first detached screen session it finds. If successful, all other command-line options are ignored. If no detached session exists, starts a new session using the specified options, just as if -R had not been specified. The option is set by default if screen is run as a login-shell (actually screen uses "-xRR" in that case). For combinations with the -d/-D option see there.
-s
sets the default shell to the program specified, instead of the value in the environment variable $SHELL (or "/bin/sh" if not defined). This can also be defined through the "shell" .screenrc command.
-S sessionname
When creating a new session, this option can be used to specify a meaningful name for the session. This name identifies the session for "screen -list" and "screen -r" actions. It substitutes the default [tty.host] suffix.
-t name
sets the title (a.k.a.) for the default shell or specified program. See also the "shelltitle" .screenrc command.
-U
Run screen in UTF-8 mode. This option tells screen that your terminal sends and understands UTF-8 encoded characters. It also sets the default encoding for new windows to 'utf8'.
-v
Print version number.
-wipe [match]
does the same as "screen -ls", but removes destroyed sessions instead of marking them as 'dead'. An unreachable session is considered dead, when its name matches either the name of the local host, or the explicitly given parameter, if any. See the -r flag for a description how to construct matches.
-x
Attach to a not detached screen session. (Multi display mode).
-X
Send the specified command to a running screen session. You can use the -d or -r option to tell screen to look only for attached or detached screen sessions. Note that this command doesn't work if the session is password protected.





---------------------

$ sudo apt – get update
$ sudo apt install (   ) - and write the name of the library to install
$ git commit + workflow
$ git init ( create new repository )
$ git status ( what’s up )
$ git remote -v
$ git add ( to add file name)
$ git config
$ echo $
$ emacs
$
