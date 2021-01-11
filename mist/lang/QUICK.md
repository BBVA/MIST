<!---
name: Quick Start
link: quick.html
order: 2
--->

# Quick Start (ping)

Let us start with a very simple program explained step by step.

Create a new file (i.e. quickStart.mist) and open it with your favorite editor.

You can run it at every step with the command:

``` console
$ mist run quickStart.mist
```

First of all, we are going to define a host data item. With this command we declare
a new structure, "myHosts", on the knowledge base that can be used to manage data
for hosts.

``` text
  data myHosts {
    host
    os
  }
```

After that, we populate the structure myHosts with data for two hosts:

``` text
  put "127.0.0.1" "linux" => myHosts
  put "192.168.1.32" "windows" => myHosts
```

Now we can print the structure with this command:

``` text
  print myHosts
```

Or just print the last host ip with this command:

``` text
  print myHosts.ip
```

Now, we are going to print the ip of all my hosts using "iterate" command.

``` text
  iterate myHosts => host {
    print host.ip
  }
```

Let us do something more interesting, we are going to define a structure for our hosts up.

``` text
  data myHostsStatus {
    host
    status
  }
```

And now, we are going to run a ping over all my hosts and leave the result in our new structure.

``` text
  iterate myHosts => host {
    ping {
      input {
        ip <= host.ip
      }
      output {
        result
        console
      }
      then {
        check result is Success {
          put ip 'Up' => myHostsStatus
        }
        check result is Error {
          put ip 'Down' => myHostsStatus
        }
      }
    }
  }

  print myHostsStatus
```

Finally this is all the code together:

``` text
  data myHosts {
    host
    status
  }

  put "127.0.0.1" "linux" => myHosts
  put "192.168.1.32" "windows" => myHosts

  # Print all myHosts
  print myHosts

  # Print last myHosts ip
  print myHosts.ip

  # Print all myHosts ips
  iterate myHosts => host {
      print host.ip
  }

  data myHostsStatus {
    host
    status
  }

  iterate myHosts => host {
    ping {
      input {
        ip <= host.ip
      }
      output {
        result
        console
      }
      then {
        check result is Success {
          put ip 'Up' => myHostsStatus
        }
        check result is Error {
          put ip 'Down' => myHostsStatus
        }
      }
    }
  }

  print myHostsStatus
```