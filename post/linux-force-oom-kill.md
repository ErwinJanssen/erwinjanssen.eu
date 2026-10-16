---
title: Force OOM kill for a Linux process
date: 2025-12-16
abstract: |-
  A short how-to on using cgroups to force an OOM kill on a specific Linux
  process, including systemd services and standalone processes.
categories:
  - Linux
---

## Introduction

Recently, I needed a way to force the Linux OOM killer to terminate a specific
process. The goal was to test certain systemd failover behavior, because it
turns out that systemd handles an OOM kill (`Result: oom-kill`) differently than
a process being stopped using `kill` (`Result: signal`).

Since I could not readily find sources on how to do this -- most resources
discuss how to trigger the OOM killer in general, but not target a specific
process -- I decided to write up what I ended up doing, both as a reference for
myself and in case it proves useful to someone else.

## Mechanism

The most reliable and controlled method to trigger the OOM killer for a process
is to use [control groups][kernel.org-cgroups] (cgroups). If the target process
has its own dedicated cgroup, writing a very low value (or zero) to `memory.max`
will cause the next memory allocation to exceed the limit, triggering the OOM
killer.

This requires that your process/service does not share its cgroup, otherwise you
will also cause other processes to be terminated.

::: {.callout-note}

The kill occurs on allocation. An idle process such as `sleep` may survive until
it attempts to allocate memory.

:::

::: {.callout-note}

The control file `memory.max` is specific to cgroup v2, which is used by the
majority of recent Linux distributions. For cgroup v1 the control file is called
`memory.limit_in_bytes` and the hierarchy is slightly different. The rest of
this post will assume cgroup v2.

:::

## systemd services

When the target process is running as a systemd service, these cgroups are
already in place. For a service `foo.service` with no custom resource slices, it
can be done like this:

```sh
echo 0 > /sys/fs/cgroup/system.slice/foo.service/memory.max
```

The command above assumes you are running it as root. If not, you can use `sudo`
like this:

```sh
echo 0 | sudo tee /sys/fs/cgroup/system.slice/foo.service/memory.max
```

This command assumes you know which specific cgroup you need, which is fine for
one-off usage. If you need something more robust you can retrieve the
`ControlGroup` property of the service, which will have a value like
`/system.slice/foo.service`. This also works with nested cgroups and resources
slices. Example:

```sh
echo 0 > "/sys/fs/cgroup$(systemctl show --property=ControlGroup --value foo.service)/memory.max"
```

::: {.callout-note}

Avoid using `systemctl set-property` because this will persist the low memory
limit and will prevent the service from starting again.

:::

## Process without a cgroup

You might have a long-running process that you want to OOM kill, but the process
lacks a dedicated cgroup. This can be solved by creating one for it, as
demonstrated by the following snippet (requires root):

```sh
# Substitute this with the actual process ID
TARGET_PID=1234

# Create the cgroup
CGROUP=/sys/fs/cgroup/oom-kill
mkdir "$CGROUP"

# Move the process into the cgroup
echo "$TARGET_PID" > "$CGROUP/cgroup.procs"

# Lower the memory limit to trigger OOM kill
echo 0 > "$CGROUP/memory.max"

# Wait for process to be killed and cleaned up
sleep 1

# Clean up the cgroup
rmdir "$CGROUP"
```

You can verify that this works by checking `journalctl` or `dmesg` to see that
the Linux OOM killer intervened.

## Conclusion

Forcing an OOM kill is useful for testing failover behavior or debugging memory
constraints. This method using cgroups is an effective way to target a specific
process and avoid unintended side effects.

[kernel.org-cgroups]: https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html#memory-interface-files
