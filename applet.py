'''
This script is an applet to be integrated directly into TMUX
It will return a different status depending of the current state of the local system
'''
from enum import Enum
import psutil

# CPU
CPU_USAGE_WARN = 80
CPU_USAGE_CRIT = 90

# MEMORY
MEMORY_USAGE_WARN = 80
MEMORY_USAGE_CRIT = 90

# DISK
DISK_USAGE_WARN = 70
DISK_USAGE_CRIT = 90

# SWAP
SWAP_USAGE_WARN = 20
SWAP_USAGE_CRIT = 50

# COLORS
FG_COLOR_OK = 17
BG_COLOR_OK = 190
FG_COLOR_WARN = 0
BG_COLOR_WARN = 220
FG_COLOR_CRIT = 255
BG_COLOR_CRIT = 196

class StatusCode(Enum):
    '''
    Represent a check status code
    '''
    OK = 0
    WARNING = 1
    CRITICAL = 2
    UNKNOWN = -1

    def __str__(self):
        '''
        Returns the string representation of the status
        '''
        return self.name

class Status:
    '''
    Represent a check status/result
    '''
    def __init__(self, code: int, text: str):
        self.code = code
        self.text = text

    def __str__(self):
        return "{status}: {text}".format(status=self.code, text=self.text)


def check_cpu_usage(warn: int=CPU_USAGE_WARN, crit: int=CPU_USAGE_CRIT) -> Status:
    '''
    Check the CPU usage.
    Returns a warning or a critical depending of the realtime usage
    '''
    usage = psutil.cpu_percent(interval=1)
    if usage > crit:
        return Status(StatusCode.CRITICAL, "CPU: {usage}%".format(usage=usage))
    elif usage > warn:
        return Status(StatusCode.WARNING, "CPU: {usage}%".format(usage=usage))
    else:
        return Status(StatusCode.OK, "CPU: {usage}%".format(usage=usage))

def check_disk_usage(warn: int=DISK_USAGE_WARN, crit: int=DISK_USAGE_CRIT) -> Status:
    '''
    Check the utilization of each disk/partition.
    Returns a warning or a critical if any exceed the usage threshold
    '''
    disks = psutil.disk_partitions()
    disks_datas = [
        [disk.mountpoint, psutil.disk_usage(disk.mountpoint).percent]
        for disk in disks
    ]
    disks_criticals = [
        disk_data
        for disk_data in disks_datas
        if disk_data[1] > crit
    ]
    disks_warnings = [
        disk_data for disk_data in disks_datas
        if disk_data[1] > warn and disk_data[1] < crit
    ]

    if len(disks_criticals) > 0:
        return Status(
            StatusCode.CRITICAL,
            "Disk {mount}: {usage}%".format(
                mount=disks_criticals[0][0],
                usage=disks_criticals[0][1]
            )
        )
    elif len(disks_warnings) > 0:
        return Status(
            StatusCode.WARNING,
            "Disk {mount}: {usage}%".format(
                mount=disks_warnings[0][0],
                usage=disks_warnings[0][1]
            )
        )
    else:
        return Status(StatusCode.OK, "Disks OK")

def check_memory_usage(warn: int=MEMORY_USAGE_WARN, crit: int=MEMORY_USAGE_CRIT) -> Status:
    '''
    Check the memory utilization.
    Returns a warning or a critical depending of the realtime usage
    '''
    usage = psutil.virtual_memory()
    if usage.percent > crit:
        return Status(StatusCode.CRITICAL, "Memory: {usage}%".format(usage=usage.percent))
    elif usage.percent > warn:
        return Status(StatusCode.WARNING, "Memory: {usage}%".format(usage=usage.percent))
    else:
        return Status(StatusCode.OK, "Memory: {usage}%".format(usage=usage.percent))

def check_swap_usage(warn: int=SWAP_USAGE_WARN, crit: int=SWAP_USAGE_CRIT) -> Status:
    '''
    Check the swap utilization.
    Returns a warning or a critical depending of the realtime usage
    '''
    usage = psutil.swap_memory()
    if usage.percent > crit:
        return Status(StatusCode.CRITICAL, "Swap: {usage}%".format(usage=usage.percent))
    elif usage.percent > warn:
        return Status(StatusCode.WARNING, "Swap: {usage}%".format(usage=usage.percent))
    else:
        return Status(StatusCode.OK, "Swap: {usage}%".format(usage=usage.percent))

def main():
    '''
    Main entrypoint
    '''
    check_definitions = [
        check_cpu_usage,
        check_memory_usage,
        check_disk_usage,
        check_swap_usage,
    ]

    checks = [check() for check in check_definitions]
    have_criticals = any(e.code == StatusCode.CRITICAL for e in checks)
    have_warnings = any(e.code == StatusCode.WARNING for e in checks)

    if have_criticals:
        bg_color = BG_COLOR_CRIT
        fg_color = FG_COLOR_CRIT
        text = [e.text for e in checks if e.code == StatusCode.CRITICAL][0]
    elif have_warnings:
        bg_color = BG_COLOR_WARN
        fg_color = FG_COLOR_WARN
        text = [e.text for e in checks if e.code == StatusCode.WARNING][0]
    else:
        bg_color = BG_COLOR_OK
        fg_color = FG_COLOR_OK
        text = "OK"

    print(
        "#[fg=colour{bg_color},bg=colour238]" +
        "#[fg=colour{fg_color},bg=colour{bg_color}]" +
        "{text} #[fg=colour238,bg=colour{bg_color}]" +
        "#[fg=colour255,bg=colour238]".format(
            bg_color=bg_color,
            fg_color=fg_color,
            text=text)
    )

if __name__ == '__main__':
    main()
