import os
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from functools import cache
from pathlib import Path
from pprint import pformat
from typing import Callable, Dict, List, Literal, Optional, Sequence, Set, Union

import cloudpickle
import dbus

from taskflows import _SYSTEMD_FILE_PREFIX, logger
from taskflows.config import taskflows_data_dir

from .constraints import HardwareConstraint, SystemLoadConstraint
from .docker import DockerContainer, delete_docker_container
from .exec import deserialize_and_call
from .schedule import Schedule

ServiceT = Union[str, "Service"]
ServicesT = Union[ServiceT, Sequence[ServiceT]]

systemd_dir = Path.home().joinpath(".config", "systemd", "user")


def extract_service_name(unit: str | Path) -> List[str]:
    return re.sub(f"^{_SYSTEMD_FILE_PREFIX}", "", Path(unit).stem)

@dataclass
class RestartPolicy:
    """Service restart policy."""

    # condition where the service should be restarted.
    condition: Literal[
        "always",
        "on-success",
        "on-failure",
        "on-abnormal",
        "on-abort",
        "on-watchdog",
        "no",
    ]
    # waiting time before each retry (seconds)
    delay: Optional[int] = None
    # hard ceiling on how many *failed* restarts are allowed within `window` before the task is left in `FAILED` state
    max_attempts: Optional[int] = None
    # sliding time window used to decide whether an attempt counts as “failed”. If the task stays up for the full `window`, the counter resets.  
    window: Optional[int] = None

    @property
    def unit_entries(self) -> Set[str]:
        entries = set()
        # 0 allows unlimited attempts.
        window = self.window or 0
        entries.add(f"StartLimitIntervalSec={window}")
        if self.max_restarts:
            entries.add(f"StartLimitBurst={self.max_attempts}")
        return entries

    @property
    def service_entries(self) -> Set[str]:
        entries = {f"Restart={self.policy}"}
        if self.delay:
            entries.add(f"RestartSec={self.delay}")
        return entries


@dataclass
class Venv(ABC):
    env_name: str

    @abstractmethod
    def create_env_command(self, command: str) -> str:
        pass


@dataclass
class MambaEnv(Venv):
    def create_env_command(self, command: str) -> str:
        """Generate mamba command."""
        for dist_t in ("mambaforge", "miniforge3"):
            mamba_exe = Path.home().joinpath(dist_t, "bin", "mamba")
            if mamba_exe.is_file():
                # return f"bash -c '{mamba_exe} run -n {self.env_name} {command}'"
                return f"{mamba_exe} run -n {self.env_name} {command}"
        raise FileNotFoundError("mamba executable not found!")


@dataclass
class Service:
    """A service to run a command on a specified schedule."""

    # name used to identify the service.
    name: str
    # command to execute.
    start_command: str | Callable[[], None]
    # command to execute to stop the service command.
    stop_command: Optional[str] = None
    # when the service should be started.
    start_schedule: Optional[Schedule | Sequence[Schedule]] = None
    # when the service should be stopped.
    stop_schedule: Optional[Schedule | Sequence[Schedule]] = None
    # command to execute when the service is restarted.
    restart_command: Optional[str] = None
    # virtual environment where commands should be executed.
    venv: Optional[Venv] = None
    # signal used to stop the service.
    kill_signal: str = "SIGTERM"
    description: Optional[str] = None
    restart_policy: Optional[str | RestartPolicy] = 'no'
    hardware_constraints: Optional[
        HardwareConstraint | Sequence[HardwareConstraint]
    ] = None
    system_load_constraints: Optional[
        SystemLoadConstraint | Sequence[SystemLoadConstraint]
    ] = None
    # make sure this service is fully started before begining startup of these services.
    start_before: Optional[ServicesT] = None
    # make sure these services are fully started before begining startup of this service.
    start_after: Optional[ServicesT] = None
    # Units listed in this option will be started simultaneously at the same time as the configuring unit is.
    # If the listed units fail to start, this unit will still be started anyway. Multiple units may be specified.
    wants: Optional[ServicesT] = None
    # Configures dependencies similar to `Wants`, but as long as this unit is up,
    # all units listed in `Upholds` are started whenever found to be inactive or failed, and no job is queued for them.
    # While a Wants= dependency on another unit has a one-time effect when this units started,
    # a `Upholds` dependency on it has a continuous effect, constantly restarting the unit if necessary.
    # This is an alternative to the Restart= setting of service units, to ensure they are kept running whatever happens.
    upholds: Optional[ServicesT] = None
    # Units listed in this option will be started simultaneously at the same time as the configuring unit is.
    # If one of the other units fails to activate, and an ordering dependency `After` on the failing unit is set, this unit will not be started.
    # This unit will be stopped (or restarted) if one of the other units is explicitly stopped (or restarted) via systemctl command (not just normal exit on process finished).
    requires: Optional[ServicesT] = None
    # Units listed in this option will be started simultaneously at the same time as the configuring unit is.
    # If the units listed here are not started already, they will not be started and the starting of this unit will fail immediately.
    # Note: this setting should usually be combined with `After`, to ensure this unit is not started before the other unit.
    requisite: Optional[ServicesT] = None
    # Same as `Requires`, but in order for this unit will be stopped (or restarted), if a listed unit is stopped (or restarted), explicitly or not.
    binds_to: Optional[ServicesT] = None
    # one or more units that are activated when this unit enters the "failed" state.
    # A service unit using Restart= enters the failed state only after the start limits are reached.
    on_failure: Optional[ServicesT] = None
    # one or more units that are activated when this unit enters the "inactive" state.
    on_success: Optional[ServicesT] = None
    # When systemd stops or restarts the units listed here, the action is propagated to this unit.
    # Note that this is a one-way dependency — changes to this unit do not affect the listed units.
    part_of: Optional[ServicesT] = None
    # A space-separated list of one or more units to which stop requests from this unit shall be propagated to,
    # or units from which stop requests shall be propagated to this unit, respectively.
    # Issuing a stop request on a unit will automatically also enqueue stop requests on all units that are linked to it using these two settings.
    propagate_stop_to: Optional[ServicesT] = None
    propagate_stop_from: Optional[ServicesT] = None
    # other units where starting the former will stop the latter and vice versa.
    conflicts: Optional[ServicesT] = None
    # Specifies a timeout (in seconds) that starts running when the queued job is actually started.
    # If limit is reached, the job will be cancelled, the unit however will not change state or even enter the "failed" mode.
    timeout: Optional[int] = None
    # path to a file with environment variables for the service.
    # TODO LoadCredential, LoadCredentialEncrypted, SetCredentialEncrypted
    env_file: Optional[str] = None
    # environment variables for the service.
    env: Optional[Dict[str, str]] = None
    # working directory for the service.
    working_directory: Optional[str | Path] = None
    # enable the service to start automatically on boot.
    enabled: bool = False

    def __post_init__(self):
        if self.venv is not None:
            if self.start_command:
                self.start_command = self.venv.create_env_command(self.start_command)
            if self.stop_command:
                self.stop_command = self.venv.create_env_command(self.stop_command)
            if self.restart_command:
                self.restart_command = self.venv.create_env_command(
                    self.restart_command
                )
        self._set_unit_and_service_entries()

    @property
    def timer_files(self) -> List[str]:
        """Paths to all systemd timer unit files for this service."""
        file_stem = self.base_file_stem
        files = []
        if self.start_schedule:
            files.append(f"{file_stem}.timer")
        if self.stop_schedule:
            files.append(f"stop-{file_stem}.timer")
        return [os.path.join(systemd_dir, f) for f in files]

    @property
    def service_files(self) -> List[str]:
        """Paths to all systemd service unit files for this service."""
        file_stem = self.base_file_stem
        files = [f"{file_stem}.service"]
        if self.stop_schedule:
            files.append(f"stop-{file_stem}.service")
        return [os.path.join(systemd_dir, f) for f in files]

    @property
    def unit_files(self) -> List[str]:
        """Get all service and timer files for this service."""
        return self.service_files + self.timer_files

    def create(self, defer_reload: bool = False):
        """Create this service."""
        logger.info("Creating service %s", self)
        # remove old version of this service if it exists.
        self.remove()
        for attr in ("start_command", "stop_command", "restart_command"):
            cmd = getattr(self, attr)
            if not isinstance(cmd, str):
                setattr(self, attr, deserialize_and_call(cmd, self.name, attr))
        self._write_timer_units()
        self._write_service_units()
        self.enable(timers_only=not self.enabled)
        # start timers now.
        _start_service(self.timer_files)
        if not defer_reload:
            reload_unit_files()

    def start(self):
        """Start this service."""
        _start_service(self.unit_files)

    def stop(self, timers: bool = False):
        """Stop this service."""
        _stop_service(self.unit_files if timers else self.service_files)

    def restart(self):
        """Restart this service."""
        _restart_service(self.service_files)

    def enable(self, timers_only: bool):
        """Enable this service."""
        if timers_only:
            _enable_service(self.timer_files)
        else:
            _enable_service(self.unit_files)

    def disable(self):
        """Disable this service."""
        _disable_service(self.unit_files)

    def remove(self):
        """Remove this service."""
        _remove_service(
            service_files=self.service_files,
            timer_files=self.timer_files,
        )

    def _write_timer_units(self):
        for is_stop_timer, schedule in (
            (False, self.start_schedule),
            (True, self.stop_schedule),
        ):
            if schedule is None:
                continue
            timer = set()
            if isinstance(schedule, (list, tuple)):
                for sched in schedule:
                    timer.update(sched.unit_entries)
            else:
                timer.update(schedule.unit_entries)
            content = [
                "[Unit]",
                f"Description={'stop ' if is_stop_timer else ''}timer for {self.name}",
                "[Timer]",
                *timer,
                "[Install]",
                "WantedBy=timers.target",
            ]
            self._write_systemd_file("timer", "\n".join(content), is_stop_timer)

    def _set_unit_and_service_entries(self):
        def join(args):
            if not isinstance(args, (list, tuple)):
                args = [args]
            return " ".join(args)
        unit = set()
        service = {
            f"ExecStart={self.start_command}",
            f"KillSignal={self.kill_signal}",
            "TimeoutStopSec=120s",
        }
        if self.stop_command:
            service.add(f"ExecStop={self.stop_command}")
        if self.restart_command:
            service.add(f"ExecReload={self.restart_command}")
        # TODO ExecStopPost?
        if self.working_directory:
            service.add(f"WorkingDirectory={self.working_directory}")
        if self.timeout:
            service.add(f"RuntimeMaxSec={self.timeout}")
        if self.env_file:
            service.add(f"EnvironmentFile={self.env_file}")
        if self.env:
            service.add(
                "\n".join([f'Environment="{k}={v}"' for k, v in self.env.items()])
            )
        if self.description:
            unit.add(f"Description={self.description}")
        if self.start_after:
            unit.add(f"After={join(self.start_after)}")
        if self.start_before:
            unit.add(f"Before={join(self.start_before)}")
        if self.conflicts:
            unit.add(f"Conflicts={join(self.conflicts)}")
        if self.on_success:
            unit.add(f"OnSuccess={join(self.on_success)}")
        if self.on_failure:
            unit.add(f"OnFailure={join(self.on_failure)}")
        if self.part_of:
            unit.add(f"PartOf={join(self.part_of)}")
        if self.wants:
            unit.add(f"Wants={join(self.wants)}")
        if self.upholds:
            unit.add(f"Upholds={join(self.upholds)}")
        if self.requires:
            unit.add(f"Requires={join(self.requires)}")
        if self.requisite:
            unit.add(f"Requisite={join(self.requisite)}")
        if self.conflicts:
            unit.add(f"Conflicts={join(self.conflicts)}")
        if self.binds_to:
            unit.add(f"BindsTo={join(self.binds_to)}")
        if self.propagate_stop_to:
            unit.add(f"PropagatesStopTo={join(self.propagate_stop_to)}")
        if self.propagate_stop_from:
            unit.add(f"StopPropagatedFrom={join(self.propagate_stop_from)}")
        if self.hardware_constraints:
            hcs = self.hardware_constraints if isinstance(self.hardware_constraints, (list, tuple)) else [self.hardware_constraints]
            for hc in hcs:
                unit.update(hc.unit_entries)
        if self.system_load_constraints:
            slcs = self.system_load_constraints if isinstance(self.system_load_constraints, (list, tuple)) else [self.system_load_constraints]
            for slc in slcs:
                unit.update(slc.unit_entries) 
        if self.restart_policy:
            rp = RestartPolicy(policy=self.restart_policy) if isinstance(self.restart_policy, str) else self.restart_policy
            unit.update(rp.unit_entries)
            service.update(rp.service_entries)
        self.unit_entries = unit
        self.service_entries = service

    def _write_service_units(self):
        srv_file = self._write_service_file(unit=self.unit_entries, service=self.service_entries)
        # TODO ExecCondition, ExecStartPre, ExecStartPost?
        if self.stop_schedule:
            service = [f"ExecStart=systemctl --user stop {os.path.basename(srv_file)}"]
            self._write_service_file(service=service, is_stop_unit=True)

    @property
    def base_file_stem(self) -> str:
        return f"{_SYSTEMD_FILE_PREFIX}{self.name.replace(' ', '_')}"

    def _write_service_file(
        self,
        unit: Optional[List[str]] = None,
        service: Optional[List[str]] = None,
        is_stop_unit: bool = False,
    ):
        content = []
        if unit:
            content += ["[Unit]", *unit]
        content += [
            "[Service]",
            *service,
            "[Install]",
            "WantedBy=default.target",
        ]
        return self._write_systemd_file(
            "service", "\n".join(content), is_stop_unit=is_stop_unit
        )

    def _write_systemd_file(
        self,
        unit_type: Literal["timer", "service"],
        content: str,
        is_stop_unit: bool = False,
    ) -> str:
        systemd_dir.mkdir(parents=True, exist_ok=True)
        file_stem = self.base_file_stem
        if is_stop_unit:
            file_stem = f"stop-{file_stem}"
        file = systemd_dir / f"{file_stem}.{unit_type}"
        if file.exists():
            logger.warning("Replacing existing unit: %s", file)
        else:
            logger.info("Creating new unit: %s", file)
        file.write_text(content)
        return str(file)

    def __repr__(self):
        return str(self)

    def __str__(self):
        meta = {
            "name": self.name,
            "command": self.start_command,
        }
        if self.description:
            meta["description"] = self.description
        if self.start_schedule:
            meta["schedule"] = self.start_schedule
        meta = ", ".join(f"{k}={v}" for k, v in meta.items())
        return f"{self.__class__.__name__}({meta})"


class DockerStartService(Service):
    """A service to start and stop a named/persisted Docker container."""

    def __init__(self, container: DockerContainer, **kwargs):
        self.container = container
        # for key in ("requires", "start_after"):
        #    kwargs[key] = []
        # kwargs["requires"].append("docker.service")
        # kwargs["start_after"].append("docker.service")
        # make sure container and service have the same name.
        name = kwargs.pop("name", None)
        if name is None:
            name = container.name
        else:
            container.name = name
        logger.info("Using name '%s' for service and container", name)
        if container.restart_policy not in ("no",None):
            # systemd needs to manage the restart policy.
            if container.restart_policy == "unless-stopped":
                # not direct mapping.
                kwargs["restart_policy"] = "always"
            else:
                kwargs["restart_policy"] = container.restart_policy
            container.restart_policy = "no"
        super().__init__(
            name=name,
            #start_after="docker.service",
            #requires="docker.service",
            start_command=f"docker start -a {name}",
            stop_command=f"docker stop -t 30 {name}",
            restart_command=f"docker restart {name}",
            **kwargs,
        )
        # use same cgroup for container and service.
        self.slice = f"{name}.slice"
        self.service_entries.add(f"Slice={self.slice}")
        # let docker handle the signal. TODO do this for anything that provides stop_command?
        self.service_entries.add("KillMode=none")
        # not relevant with KillMode=none
        self.service_entries.remove("KillSignal=SIGTERM")
        # SIGTERM from docker stop
        self.service_entries.add("SuccessExitStatus=0 143")
        self.service_entries.add("RestartForceExitStatus=255")
        self.service_entries.add("Delegate=yes")
        self.service_entries.add("TasksMax=infinity")
        # drop the duplicate log stream in journalctl
        self.service_entries.add("StandardOutput=null")
        self.service_entries.add("StandardError=null")
        # blocks until it is fully stopped
        self.service_entries.add(f"ExecStopPost=docker wait {name}")
        #self.service_entries.add("RestartSec=5s")
        #self.service_entries.add("StartLimitBurst=0")

    def create(self, defer_reload: bool = False):
        super().create(defer_reload=defer_reload)
        self.container.create(cgroup_parent=self.slice)

    def remove(self):
        """Remove this service."""
        _remove_service(
            service_files=self.service_files,
            timer_files=self.timer_files,
        )


class DockerRunService(Service):
    """A service to run a Docker container."""

    def __init__(self, container: DockerContainer, **kwargs):
        self.container = container
        name = kwargs.pop("name", None)
        # if both service and container have a name, use the service name for both.
        name = name or container.name
        logger.info("Using name '%s' for service and container", name)
        self.container.name = name
        # TODO need venv command.
        super().__init__(
            name=name,
            start_command=f"_run_docker_service {name}",
            stop_command=f"docker stop {name}",
            restart_command=f"docker restart {name}",
            **kwargs,
        )

    def create(self, defer_reload: bool = False):
        # start_command = f"_run_docker_service {self.name}"
        # self.start_command = (
        #    self.venv.create_env_command(start_command) if self.venv else start_command
        # )
        taskflows_data_dir.joinpath(f"{self.name}#_docker_run_srv.pickle").write_bytes(
            cloudpickle.dumps(self)
        )
        super().create(defer_reload=defer_reload)


@cache
def session_dbus():
    # SessionBus is for user session (like systemctl --user)
    return dbus.SessionBus()


@cache
def systemd_manager():
    bus = session_dbus()
    # Access the systemd D-Bus object
    systemd = bus.get_object("org.freedesktop.systemd1", "/org/freedesktop/systemd1")
    return dbus.Interface(systemd, dbus_interface="org.freedesktop.systemd1.Manager")


def reload_unit_files():
    systemd_manager().Reload()


def escape_path(path) -> str:
    """Escape a path so that it can be used in a systemd file."""
    return systemd_manager().EscapePath(path)


def get_schedule_info(unit: str):
    """Get the schedule information for a unit."""
    unit_stem = unit.replace(".service", "").replace(".timer", "")
    if not unit_stem.startswith(_SYSTEMD_FILE_PREFIX):
        unit_stem = f"{_SYSTEMD_FILE_PREFIX}{unit_stem}"
    manager = systemd_manager()
    bus = session_dbus()
    # service_path = manager.GetUnit(f"{unit_stem}.service")
    service_path = manager.LoadUnit(f"{unit_stem}.service")
    service = bus.get_object("org.freedesktop.systemd1", service_path)
    service_properties = dbus.Interface(
        service, dbus_interface="org.freedesktop.DBus.Properties"
    )
    schedule = {
        # timestamp of the last time a unit entered the active state.
        "Last Start": service_properties.Get(
            "org.freedesktop.systemd1.Unit", "ActiveEnterTimestamp"
        ),
        # timestamp of the last time a unit exited the active state.
        "Last Finish": service_properties.Get(
            "org.freedesktop.systemd1.Unit", "ActiveExitTimestamp"
        ),
    }
    timer_path = manager.LoadUnit(f"{unit_stem}.timer")
    timer = bus.get_object("org.freedesktop.systemd1", timer_path)
    timer_properties = dbus.Interface(
        timer, dbus_interface="org.freedesktop.DBus.Properties"
    )
    schedule["Next Start"] = timer_properties.Get(
        "org.freedesktop.systemd1.Timer", "NextElapseUSecRealtime"
    )
    # "org.freedesktop.systemd1.Timer", "LastTriggerUSec"
    missing_dt = datetime(1970, 1, 1, 0, 0, 0)

    def timestamp_to_dt(timestamp):
        try:
            dt = datetime.fromtimestamp(timestamp / 1_000_000)
            if dt == missing_dt:
                return None
            return dt
        except ValueError:
            # "year 586524 is out of range"
            return None

    schedule = {field: timestamp_to_dt(val) for field, val in schedule.items()}
    # TimersCalendar contains an array of structs that contain information about all realtime/calendar timers of this timer unit. The structs contain a string identifying the timer base, which may only be "OnCalendar" for now; the calendar specification string; the next elapsation point on the CLOCK_REALTIME clock, relative to its epoch.
    timers_cal = []
    # for timer_type in ("TimersMonotonic", "TimersCalendar"):
    for timer in timer_properties.Get(
        "org.freedesktop.systemd1.Timer", "TimersCalendar"
    ):
        base, spec, next_start = timer
        timers_cal.append(
            {
                "base": base,
                "spec": spec,
                "next_start": timestamp_to_dt(next_start),
            }
        )
    schedule["Timers Calendar"] = timers_cal
    if (not schedule["Next Start"]) and (
        next_start := [t["next_start"] for t in timers_cal if t["next_start"]]
    ):
        schedule["Next Start"] = min(next_start)
    # TimersMonotonic contains an array of structs that contain information about all monotonic timers of this timer unit. The structs contain a string identifying the timer base, which is one of "OnActiveUSec", "OnBootUSec", "OnStartupUSec", "OnUnitActiveUSec", or "OnUnitInactiveUSec" which correspond to the settings of the same names in the timer unit files; the microsecond offset from this timer base in monotonic time; the next elapsation point on the CLOCK_MONOTONIC clock, relative to its epoch.
    timers_mono = []
    for timer in timer_properties.Get(
        "org.freedesktop.systemd1.Timer", "TimersMonotonic"
    ):
        base, offset, next_start = timer
        timers_mono.append(
            {
                "base": base,
                "offset": offset,
                "next_start": timestamp_to_dt(next_start),
            }
        )
    schedule["Timers Monotonic"] = timers_mono
    return schedule


def get_unit_files(
    unit_type: Optional[Literal["service", "timer"]] = None,
    match: Optional[str] = None,
    states: Optional[str | Sequence[str]] = None,
) -> List[str]:
    """Get a list of paths of taskflow unit files."""
    file_states = get_unit_file_states(unit_type=unit_type, match=match, states=states)
    return list(file_states.keys())


def get_unit_file_states(
    unit_type: Optional[Literal["service", "timer"]] = None,
    match: Optional[str] = None,
    states: Optional[str | Sequence[str]] = None,
) -> Dict[str, str]:
    """Map taskflow unit file path to unit state."""
    states = states or []
    pattern = _make_unit_match_pattern(unit_type=unit_type, match=match)
    files = list(systemd_manager().ListUnitFilesByPatterns(states, [pattern]))
    if not files:
        logger.error("No taskflow unit files found matching: %s", pattern)
    return {str(file): str(state) for file, state in files}


def get_units(
    unit_type: Optional[Literal["service", "timer"]] = None,
    match: Optional[str] = None,
    states: Optional[str | Sequence[str]] = None,
) -> List[Dict[str, str]]:
    """Get metadata for taskflow units."""
    states = states or []
    pattern = _make_unit_match_pattern(unit_type=unit_type, match=match)
    files = list(systemd_manager().ListUnitsByPatterns(states, [pattern]))
    fields = [
        "unit_name",
        "description",
        "load_state",
        "active_state",
        "sub_state",
        "followed",
        "unit_path",
        "job_id",
        "job_type",
        "job_path",
    ]
    return [{k: str(v) for k, v in zip(fields, f)} for f in files]


def _make_unit_match_pattern(
    unit_type: Optional[Literal["service", "timer"]] = None, match: Optional[str] = None
) -> str:
    pattern = match or "*"
    if unit_type and not pattern.endswith(f".{unit_type}"):
        pattern += f".{unit_type}"
    if _SYSTEMD_FILE_PREFIX not in pattern:
        pattern = f"*{_SYSTEMD_FILE_PREFIX}{pattern}"
    return re.sub(r"\*{2,}", "*", pattern)


def _start_service(files: Sequence[str]):
    mgr = systemd_manager()
    for sf in files:
        sf = os.path.basename(sf)
        if sf.startswith("stop-"):
            continue
        logger.info("Running: %s", sf)
        mgr.StartUnit(sf, "replace")


def _stop_service(files: Sequence[str]):
    mgr = systemd_manager()
    for sf in files:
        sf = os.path.basename(sf)
        logger.info("Stopping: %s", sf)
        try:
            mgr.StopUnit(sf, "replace")
        except dbus.exceptions.DBusException as err:
            logger.warning("Could not stop %s: (%s) %s", sf, type(err), err)

        # remove any failed status caused by stopping service.
        # mgr.ResetFailedUnit(sf)


def _restart_service(files: Sequence[str]):
    units = [os.path.basename(f) for f in files]
    # don't restart "stop" units
    units = [u for u in units if u.startswith("taskflow-")]
    mgr = systemd_manager()
    for sf in units:
        logger.info("Restarting: %s", sf)
        try:
            mgr.RestartUnit(sf, "replace")
        except dbus.exceptions.DBusException as err:
            logger.warning("Could not restart %s: (%s) %s", sf, type(err), err)


def _enable_service(files: Sequence[str]):
    mgr = systemd_manager()
    logger.info("Enabling: %s", pformat(files))

    def enable_files(files, is_retry=False):
        try:
            # the first bool controls whether the unit shall be enabled for runtime only (true, /run), or persistently (false, /etc).
            # The second one controls whether symlinks pointing to other units shall be replaced if necessary.
            mgr.EnableUnitFiles(files, False, True)
        except dbus.exceptions.DBusException as err:
            logger.warning("Could not enable %s: (%s) %s", files, type(err), err)
            if not is_retry and len(files) > 1:
                for file in files:
                    enable_files([file], is_retry=True)

    enable_files(files)


def _disable_service(files: Sequence[str]):
    mgr = systemd_manager()
    files = [os.path.basename(f) for f in files]
    logger.info("Disabling: %s", pformat(files))

    def disable_files(files, is_retry=False):
        try:
            # the first bool controls whether the unit shall be enabled for runtime only (true, /run), or persistently (false, /etc).
            # The second one controls whether symlinks pointing to other units shall be replaced if necessary.
            for meta in mgr.DisableUnitFiles(files, False):
                # meta has: the type of the change (one of symlink or unlink), the file name of the symlink and the destination of the symlink.
                logger.info("%s %s %s", *meta)
        except dbus.exceptions.DBusException as err:
            logger.warning("Could not disable %s: (%s) %s", files, type(err), err)
            if not is_retry and len(files) > 1:
                for file in files:
                    disable_files([file], is_retry=True)

    disable_files(files)


def _remove_service(
    service_files: Sequence[str],
    timer_files: Sequence[str]
):
    def valid_file_paths(files):
        files = [Path(f) for f in files]
        return [f for f in files if f.is_file()]

    service_files = valid_file_paths(service_files)
    timer_files = valid_file_paths(timer_files)

    files = service_files + timer_files
    _stop_service(files)
    _disable_service(files)
    container_names = set()
    mgr = systemd_manager()
    for srv_file in service_files:
        logger.info("Cleaning cache and runtime directories: %s.", srv_file)
        try:
            # the possible values are "configuration", "state", "logs", "cache", "runtime", "fdstore", and "all".
            mgr.CleanUnit(srv_file.name, ["all"])
        except dbus.exceptions.DBusException as err:
            logger.warning("Could not clean %s: (%s) %s", srv_file, type(err), err)
        container_name = re.search(
            r"docker (?:start|stop) ([\w-]+)", srv_file.read_text()
        )
        if container_name:
            container_names.add(container_name.group(1))
    for cname in container_names:
        delete_docker_container(cname)
    for srv in service_files:
        files.extend(taskflows_data_dir.glob(f"{extract_service_name(srv)}#*.pickle"))
    for file in files:
        logger.info("Deleting %s", file)
        file.unlink()
