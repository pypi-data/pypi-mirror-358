"""
Kwollect monitoring manager
"""

from pathlib import Path
from typing import Hashable, Optional, TextIO

import enoslib as en

import e2clab.constants.default as default
from e2clab.constants import WORKFLOW_TASKS, Environment
from e2clab.errors import E2clabError
from e2clab.log import get_logger
from e2clab.managers.manager import Manager
from e2clab.probe import Record, TaskProbe

METRICS = "metrics"
STEP = "step"

START = "start"
END = "end"

ALL = "all"

STEP_OPTIONS = [*WORKFLOW_TASKS, "launch"]


class MonitoringKwollectManager(Manager):
    """
    Kwollect monitoring manager class
    """

    logger = get_logger(__name__, ["KWOLLECT"])

    SCHEMA = {
        "$schema": "https://json-schema.org/draft/2019-09/schema",
        "type": "object",
        "title": "Grid5000 kwollect monitoring manager",
        "properties": {
            METRICS: {
                "description": "Metrics to pull from job, '[all]' to pull all metrics",
                "type": "array",
                "items": {"type": "string"},
            },
            STEP: {
                "description": "Workflow step to monitor",
                "type": "string",
                "enum": STEP_OPTIONS,
                "default": default.KWOLLECT_STEP,
            },
            START: {
                "description": (
                    f"Workflow step to start monitor at. Mandatory if '{END}' is set"
                ),
                "type": "string",
                "enum": STEP_OPTIONS,
            },
            END: {
                "description": "Workflow step to end monitor at",
                "type": "string",
                "enum": STEP_OPTIONS,
            },
        },
        "required": [METRICS],
        "dependencies": {END: [START]},
        "allOf": [
            {
                "if": {"required": [STEP]},
                "then": {
                    "not": {
                        "anyOf": [
                            {"required": [START]},
                            {"required": [END]},
                        ]
                    }
                },
            }
        ],
    }

    CONFIG_KEY = "kwollect"
    SERVICE_ROLE = None  # Not useful
    ROLE = "k_monitor"

    def create_service(self) -> en.Kwollect:
        return en.Kwollect(nodes=self.agents)

    def _deploy(self) -> None:
        self.jobs = self.provider.get_jobs()
        for job in self.jobs:
            site = job.site
            id = job.uid
            dash_addr = self._get_viz_address(site)
            self.logger.info(
                f"Access kwollect metric dashboard for job {id}: {dash_addr}"
            )
        self.service.deploy()

    def _backup(self, output_dir: Path) -> None:
        # output dir
        kwollect_output_dir = (
            output_dir / default.MONITORING_DATA / default.MONITORING_KWOLLECT_DATA
        )
        # kwollect_output_dir.mkdir(exist_ok=True, parents=True)

        # metrics
        metrics = self._get_metrics()

        # probe
        try:
            start_time, end_time = self._get_timestamp()
        except E2clabError as e:
            self.logger.warning(f"Could not backup kwollect data : {e}")
            return

        # hacky way to set start and end time
        self.service.start_time = start_time
        self.service.stop_time = end_time

        self.logger.debug("Backing up kwollect data...")
        try:
            self.service.backup(
                backup_dir=kwollect_output_dir,
                metrics=metrics,
            )
        except Exception as e:
            self.logger.error("Failed to backup kwollect data")
            self.logger.error(e)
        self.logger.debug("Backed up kwollect data")

    def _destroy(self) -> None:
        self.service.destroy()

    def get_environment(self) -> Environment:
        """This manager only works for Grid5000"""
        return Environment.G5K

    def layers_validate_info(self, file: TextIO) -> None:
        """
        Information to dump to `layers_services_validate.yaml`
        """
        self.jobs = self.provider.get_jobs()
        info = "\n# Access kwollect metric dashboard for jobs:"
        for job in self.jobs:
            site = job.site
            id = job.uid
            dash_addr = self._get_viz_address(site)
            info += f"\n#  - {id} on site {site}: {dash_addr}"

        file.write(info)

    def _get_metrics(self) -> Optional[list[str]]:
        m_list = self.config.get(METRICS, [ALL])
        if ALL in m_list:
            # None parameter will pull all metrics
            return None
        else:
            return m_list

    def _get_timestamp(self) -> tuple[float, Optional[float]]:
        """Parsing configuration for start and end timestamp

        Returns:
            tuple[str, Optional[str]]: end timestamp may be None
        """
        # Get task probe singleton
        task_probe = TaskProbe.get_probe()

        def _get_record(rec_name: Hashable) -> Record:
            rec = task_probe.get_task_record(rec_name)
            if rec is None:
                raise E2clabError(f"Failed to get timing record for {rec_name}")
            return rec

        start = None
        end = None
        if STEP in self.config:
            step = self.config[STEP]

            rec = _get_record(step)

            start = rec.start
            end = rec.end

        elif START in self.config:
            step = self.config[START]

            rec = _get_record(step)
            start = rec.start

            if END in self.config:
                step = self.config[END]

                rec = _get_record(step)
                end = rec.end
        else:
            rec = _get_record(default.KWOLLECT_STEP)
            start = rec.start
            end = rec.end

        if start is None:
            raise E2clabError("No start time found for kwollect monitoring")
        return start, end

    def _get_viz_address(self, site: str) -> str:
        """Returns address to dashboard"""
        addr = f"https://api.grid5000.fr/stable/sites/{site}/metrics/dashboard"
        return addr
