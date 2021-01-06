Lumpi
=====

lombi explained
---------------

lombi[1] is a controller for "the hex", our first piece of robot
furniture[2] we created at the lab jetpack. the hex consists of six
triangular tiles as structural elements. each element is a
sensorimotor node (smnode). it is a cellular automaton on a triangular
grid. the update rule for each smnode are identical. in addition to
being influenced by neighbor states, each smnode responds to sensors
attached to it.

[1] lombi, Limbo, Lombi, Lompi - alluding to a lamp

[2] smart home appliances

jcl: hex instructions
---------------------

If you want to work on the hex this is a workflow of how to do it

1.  Turn on hex on the power chord main switch. Raspberry and sensorimotor

network will boot up, LEDs will be flashing briefly from sensorimotor init.

1.  On your machine open the atom editor

2.  In atom, go to Menu -&gt; Packages -&gt; Remote Atom -&gt; Start Server

This setup is using the remote-atom package, see https://atom.io/packages/remote-atom

3.  With the remote atom server started, now open or go to a terminal. In the terminal type

``` example
ssh hex
```

This will log you in on the hex raspberry. The full ssh command is

``` example
ssh -R 52698:localhost:52698 user@example.com
```

Suggest to setup ssh key authentication and put the ssh tunnel into ~.ssh/config

1.  Logged in on the hex raspberry you will see this prompt

``` example
pi@tauntaun:~ $ 
```

1.  With this prompt, type

``` example
pi@tauntaun:~ $ cd work/Limbo/
```

This takes you to the Limbo working directory

1.  Now you can run the code for the hex by typing

``` example
pi@tauntaun:~ $ python3 lombi-hex-1.py --hardware --clock-freq 0.1
```

or something similar

1.  In the same terminal, press Control-C twice to stop the script

2.  If you didn't do so already, type

``` example
pi@tauntaun:~ $ rmate lombi-hex-1.py
```

This will open the Python file on the hex raspberry in the Atom editor running on your local machine.

1.  Go to atom, change the code and save your changes

2.  Go to terminal run the script again, Control-C twice to stop it, repeat the loop

<!-- -->

1.  If there is an error saying -16 cannot access / open sensorimotor something, that means another script is already running. You need to stop that before you can run you script. To stop it type into the terminal

$ ps ax | grep python

The output should look like this

``` example
pi@tauntaun:~ $ ps ax| grep python
 1433 pts/3    Sl+    0:05 /usr/bin/python ./example_node_io.py
 1440 pts/4    S+     0:00 grep --color=auto python
pi@tauntaun:~ $ 
```

Using the number on the left (here it is 1433) of the sensorimotor script (here it's example<sub>nodeio</sub>.py), you can stop the process by typing

``` example
pi@tauntaun:~ $ kill 1433
```

This will stop the currently running script and free the sensorimotor driver for another program.


TODO
----

1/ refactor into combination of three components: the sensorimotor loop
spec, the sensorimotor driver, the simulation
driver.

2/ communication via OSC or other channel

3/ create startup script starting all components into multiprocessing
Processes
