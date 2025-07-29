import base64
import json
import logging
import aiohttp.web
import ray.dashboard.utils as dashboard_utils
import ray.dashboard.optional_utils as dashboard_optional_utils
from ray.dashboard.datacenter import DataSource
from ray._private.test_utils import get_resource_usage
from ray.dashboard.modules.insight.analyze_prompt import PROMPT_TEMPLATE

logger = logging.getLogger(__name__)
routes = dashboard_optional_utils.DashboardHeadRouteTable


class InsightHead(dashboard_utils.DashboardHeadModule):
    def __init__(self, config: dashboard_utils.DashboardHeadModuleConfig):
        super().__init__(config)

    @routes.get("/get_insight_analyze_prompt")
    async def get_insight_analyze_prompt(
        self, req: aiohttp.web.Request
    ) -> aiohttp.web.Response:
        """Return the insight analyze prompt."""
        return dashboard_optional_utils.rest_response(
            success=True,
            message="Insight analyze prompt retrieved successfully.",
            prompt=PROMPT_TEMPLATE,
        )

    @routes.get("/get_breakpoints")
    async def get_breakpoints(self, req: aiohttp.web.Request) -> aiohttp.web.Response:
        """Return a list of breakpoints."""
        job_id = req.query.get("job_id", "default_job")
        task_id = req.query.get("task_id", "")
        address = await self.gcs_aio_client.internal_kv_get(
            "insight_monitor_address",
            namespace="flowinsight",
            timeout=5,
        )
        if not address:
            return dashboard_optional_utils.rest_response(
                success=False, message="InsightMonitor address not found in KV store"
            )
        host, port = address.decode().split(":")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"http://{host}:{port}/get_breakpoints",
                    json={"job_id": job_id, "task_id": task_id},
                ) as response:
                    if response.status != 200:
                        return dashboard_optional_utils.rest_response(
                            success=False,
                            message=f"Error from insight monitor: {await response.text()}",
                        )
                    result = await response.json()
                    return dashboard_optional_utils.rest_response(
                        success=True,
                        message="Breakpoints retrieved successfully.",
                        result=result,
                    )
        except Exception as e:
            logger.error(f"Error retrieving breakpoints: {str(e)}")
            return dashboard_optional_utils.rest_response(
                success=False, message=f"Error retrieving breakpoints: {str(e)}"
            )

    @routes.get("/set_breakpoints")
    async def set_breakpoints(self, req: aiohttp.web.Request) -> aiohttp.web.Response:
        """Set a list of breakpoints."""
        job_id = req.query.get("job_id", "default_job")
        task_id = req.query.get("task_id", "")
        breakpoints_base64 = req.query.get("breakpoints", "")
        breakpoints = json.loads(base64.b64decode(breakpoints_base64).decode("utf-8"))
        address = await self.gcs_aio_client.internal_kv_get(
            "insight_monitor_address",
            namespace="flowinsight",
            timeout=5,
        )
        if not address:
            return dashboard_optional_utils.rest_response(
                success=False, message="InsightMonitor address not found in KV store"
            )
        host, port = address.decode().split(":")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"http://{host}:{port}/set_breakpoints",
                    json={
                        "job_id": job_id,
                        "task_id": task_id,
                        "breakpoints": breakpoints,
                    },
                ) as response:
                    if response.status != 200:
                        return dashboard_optional_utils.rest_response(
                            success=False,
                            message=f"Error from insight monitor: {await response.text()}",
                        )
                    result = await response.json()
                    return dashboard_optional_utils.rest_response(
                        success=True,
                        message="Breakpoints set successfully.",
                        result=result,
                    )
        except Exception as e:
            logger.error(f"Error setting breakpoints: {str(e)}")
            return dashboard_optional_utils.rest_response(
                success=False, message=f"Error setting breakpoints: {str(e)}"
            )

    @routes.get("/get_debug_sessions")
    async def get_debug_sessions(
        self, req: aiohttp.web.Request
    ) -> aiohttp.web.Response:
        """Return a list of active debug sessions."""
        job_id = req.query.get("job_id", "default_job")
        service_name = req.query.get("service_name", None)
        instance_id = req.query.get("instance_id", None)
        func_name = req.query.get("func_name", None)
        filter_active = req.query.get("filter_active", "false")
        filter_active = True if filter_active == "true" else False
        address = await self.gcs_aio_client.internal_kv_get(
            "insight_monitor_address",
            namespace="flowinsight",
            timeout=5,
        )
        if not address:
            return dashboard_optional_utils.rest_response(
                success=False, message="InsightMonitor address not found in KV store"
            )
        host, port = address.decode().split(":")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"http://{host}:{port}/get_debug_sessions",
                    json={
                        "job_id": job_id,
                        "service_info": None
                        if service_name is None
                        else [service_name, instance_id],
                        "func_name": func_name,
                        "filter_active": filter_active,
                    },
                ) as response:
                    if response.status != 200:
                        return dashboard_optional_utils.rest_response(
                            success=False,
                            message=f"Error from insight monitor: {await response.text()}",
                        )
                    result = await response.json()
                    return dashboard_optional_utils.rest_response(
                        success=True,
                        message="Debug sessions retrieved successfully.",
                        result=result,
                    )
        except Exception as e:
            logger.error(f"Error retrieving debug sessions: {str(e)}")
            return dashboard_optional_utils.rest_response(
                success=False, message=f"Error retrieving debug sessions: {str(e)}"
            )

    @routes.get("/activate_debug_session")
    async def activate_debug_session(
        self, req: aiohttp.web.Request
    ) -> aiohttp.web.Response:
        """Activate a debug session."""
        job_id = req.query.get("job_id", "default_job")
        service_name = req.query.get("service_name", None)
        instance_id = req.query.get("instance_id", None)
        func_name = req.query.get("func_name", None)
        task_id = req.query.get("task_id", "")
        address = await self.gcs_aio_client.internal_kv_get(
            "insight_monitor_address",
            namespace="flowinsight",
            timeout=5,
        )
        if not address:
            return dashboard_optional_utils.rest_response(
                success=False, message="InsightMonitor address not found in KV store"
            )
        host, port = address.decode().split(":")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"http://{host}:{port}/activate_debug_session",
                    json={
                        "job_id": job_id,
                        "service_info": None
                        if service_name is None
                        else [service_name, instance_id],
                        "func_name": func_name,
                        "task_id": task_id,
                    },
                ) as response:
                    if response.status != 200:
                        return dashboard_optional_utils.rest_response(
                            success=False,
                            message=f"Error from insight monitor: {await response.text()}",
                        )
                    result = await response.json()
                    return dashboard_optional_utils.rest_response(
                        success=True,
                        message="Debug session activated successfully.",
                        result=result,
                    )
        except Exception as e:
            logger.error(f"Error activating debug session: {str(e)}")
            return dashboard_optional_utils.rest_response(
                success=False, message=f"Error activating debug session: {str(e)}"
            )

    @routes.get("/debug_cmd")
    async def debug_cmd(self, req: aiohttp.web.Request) -> aiohttp.web.Response:
        """Send a debug command to the insight monitor."""
        job_id = req.query.get("job_id", "default_job")
        task_id = req.query.get("task_id", "")
        command = req.query.get("command", "")
        args_base64 = req.query.get("args", "")
        args = base64.b64decode(args_base64).decode("utf-8")
        args = json.loads(args)
        address = await self.gcs_aio_client.internal_kv_get(
            "insight_monitor_address",
            namespace="flowinsight",
            timeout=5,
        )
        if not address:
            return dashboard_optional_utils.rest_response(
                success=False, message="InsightMonitor address not found in KV store"
            )
        host, port = address.decode().split(":")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"http://{host}:{port}/debug_cmd",
                    json={
                        "job_id": job_id,
                        "task_id": task_id,
                        "command": command,
                        "args": args,
                    },
                ) as response:
                    if response.status != 200:
                        return dashboard_optional_utils.rest_response(
                            success=False,
                            message=f"Error from insight monitor: {await response.text()}",
                        )
                    result = await response.json()
                    return dashboard_optional_utils.rest_response(
                        success=True,
                        message="Debug command sent successfully.",
                        result=result,
                    )
        except Exception as e:
            logger.error(f"Error sending debug command: {str(e)}")
            return dashboard_optional_utils.rest_response(
                success=False, message=f"Error sending debug command: {str(e)}"
            )

    @routes.get("/deactivate_debug_session")
    async def deactivate_debug_session(
        self, req: aiohttp.web.Request
    ) -> aiohttp.web.Response:
        """Deactivate a debug session."""
        job_id = req.query.get("job_id", "default_job")
        task_id = req.query.get("task_id", "")
        address = await self.gcs_aio_client.internal_kv_get(
            "insight_monitor_address",
            namespace="flowinsight",
            timeout=5,
        )
        if not address:
            return dashboard_optional_utils.rest_response(
                success=False, message="InsightMonitor address not found in KV store"
            )
        host, port = address.decode().split(":")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"http://{host}:{port}/deactivate_debug_session",
                    json={"job_id": job_id, "task_id": task_id},
                ) as response:
                    if response.status != 200:
                        return dashboard_optional_utils.rest_response(
                            success=False,
                            message=f"Error from insight monitor: {await response.text()}",
                        )
                    result = await response.json()
                    return dashboard_optional_utils.rest_response(
                        success=True,
                        message="Debug session deactivated successfully.",
                        result=result,
                    )
        except Exception as e:
            logger.error(f"Error deactivating debug session: {str(e)}")
            return dashboard_optional_utils.rest_response(
                success=False, message=f"Error deactivating debug session: {str(e)}"
            )

    @routes.get("/get_active_debug_sessions")
    async def get_active_debug_sessions(
        self, req: aiohttp.web.Request
    ) -> aiohttp.web.Response:
        """Get a list of active debug sessions."""
        job_id = req.query.get("job_id", "default_job")
        address = await self.gcs_aio_client.internal_kv_get(
            "insight_monitor_address",
            namespace="flowinsight",
            timeout=5,
        )
        if not address:
            return dashboard_optional_utils.rest_response(
                success=False, message="InsightMonitor address not found in KV store"
            )
        host, port = address.decode().split(":")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"http://{host}:{port}/get_active_debug_sessions?job_id={job_id}"
                ) as response:
                    if response.status != 200:
                        return dashboard_optional_utils.rest_response(
                            success=False,
                            message=f"Error from insight monitor: {await response.text()}",
                        )
                    result = await response.json()
                    return dashboard_optional_utils.rest_response(
                        success=True,
                        message="Active debug sessions retrieved successfully.",
                        result=result,
                    )
        except Exception as e:
            logger.error(f"Error retrieving active debug sessions: {str(e)}")
            return dashboard_optional_utils.rest_response(
                success=False,
                message=f"Error retrieving active debug sessions: {str(e)}",
            )

    @routes.get("/physical_view")
    async def get_physical_view(self, req: aiohttp.web.Request) -> aiohttp.web.Response:
        """Return a physical view of resource usage and actor placement across nodes.

        Query Parameters:
            job_id: Filter actors by job ID

        Returns:
            JSON with node-based view of resources and actors
        """
        try:
            job_id = req.query.get("job_id", "default_job")

            # Get resource usage data from GCS
            resources_data = get_resource_usage(self.gcs_address)

            # Get insight monitor address from KV store
            address = await self.gcs_aio_client.internal_kv_get(
                "insight_monitor_address",
                namespace="flowinsight",
                timeout=5,
            )

            if not address:
                logger.warning("InsightMonitor address not found in KV store")
                context_info = {}
                resource_usage = {}
            else:
                host, port = address.decode().split(":")
                # Fetch context info from insight monitor
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"http://{host}:{port}/get_context_info",
                        params={"job_id": job_id},
                    ) as response:
                        if response.status != 200:
                            logger.warning(
                                f"Error fetching context info: {await response.text()}"
                            )
                            context_info = {}
                        else:
                            context_info = await response.json()

                    async with session.get(
                        f"http://{host}:{port}/get_resource_usage",
                        params={"job_id": job_id},
                    ) as response:
                        if response.status != 200:
                            logger.warning(
                                f"Error fetching resource usage: {await response.text()}"
                            )
                            resource_usage = {}
                        else:
                            resource_usage = await response.json()

            # Build node-based view
            physical_view = {}

            # Process each node's resource usage
            for node_data in resources_data.batch:
                node_id = node_data.node_id.hex()
                if node_id not in physical_view:
                    physical_view[node_id] = {
                        "resources": {},
                        "services": {},
                        "gpus": [],
                    }

                for resource_name, total in node_data.resources_total.items():
                    available = node_data.resources_available.get(resource_name, 0.0)
                    physical_view[node_id]["resources"][resource_name] = {
                        "total": total,
                        "available": available,
                    }

                # Add GPU information from node physical stats
                node_physical_stats = DataSource.node_physical_stats.get(node_id, {})
                if "gpus" in node_physical_stats:
                    physical_view[node_id]["gpus"] = node_physical_stats["gpus"]

            # Add actor information
            for actor_id, actor_info in DataSource.actors.items():
                if actor_info.get("jobId") == job_id:
                    # Skip the internal insight monitor actor
                    if actor_info.get("name", "") != "":
                        actor_name = actor_info.get("name")
                    else:
                        actor_name = actor_info.get("className", "Unknown")

                    if actor_name == "_ray_internal_insight_monitor":
                        continue

                    node_id = actor_info["address"]["rayletId"]
                    if node_id in physical_view:
                        actor_pid = actor_info.get("pid")
                        actor_view = {
                            "instanceId": actor_id,
                            "name": actor_name,
                            "state": actor_info.get("state", "UNKNOWN"),
                            "pid": actor_pid,
                            "nodeId": node_id,  # Add node ID to actor information
                            "requiredResources": actor_info.get(
                                "requiredResources", {}
                            ),
                            "gpuDevices": [],  # Add GPU devices used by this actor
                        }

                        # Add placement group info if available
                        pg_id = actor_info.get("placementGroupId")
                        if pg_id:
                            actor_view["placementGroup"] = {
                                "id": pg_id,
                            }

                        # Initialize process stats with default values
                        actor_view["processStats"] = {
                            "cpuPercent": 0,
                            "memoryInfo": {"rss": 0},
                        }

                        # Get CPU and memory information from node_physical_stats by matching PID
                        node_physical_stats = DataSource.node_physical_stats.get(
                            node_id, {}
                        )
                        if actor_pid and "workers" in node_physical_stats:
                            for worker in node_physical_stats["workers"]:
                                if worker.get("pid") == actor_pid:
                                    # Update process stats with data from node_physical_stats
                                    actor_view["processStats"] = {
                                        "cpuPercent": worker.get("cpuPercent", 0),
                                        "memoryInfo": worker.get(
                                            "memoryInfo", {"rss": 0}
                                        ),
                                    }

                        actor_view["nodeCpuPercent"] = node_physical_stats.get("cpu", 0)

                        # Add node memory info from the dictionary if available
                        actor_view["nodeMem"] = node_physical_stats.get("mem", 0)

                        # Add GPU information for this actor based on its PID
                        if actor_pid:
                            node_gpus = physical_view[node_id].get("gpus", [])
                            for gpu in node_gpus:
                                for process in gpu.get("processesPids", []):
                                    if process["pid"] == actor_pid:
                                        actor_view["gpuDevices"].append(
                                            {
                                                "index": gpu["index"],
                                                "name": gpu["name"],
                                                "uuid": gpu["uuid"],
                                                "memoryUsed": process["gpuMemoryUsage"],
                                                "memoryTotal": gpu["memoryTotal"],
                                                "utilization": gpu.get(
                                                    "utilizationGpu", 0
                                                ),
                                            }
                                        )

                        # If actor has no GPU devices but the node has GPUs, add node GPU info
                        if not actor_view["gpuDevices"]:
                            for gpu in node_physical_stats["gpus"]:
                                actor_view["gpuDevices"].append(
                                    {
                                        "index": gpu["index"],
                                        "name": gpu["name"],
                                        "uuid": gpu["uuid"],
                                        "memoryTotal": gpu["memoryTotal"],
                                        "memoryUsed": 0,  # No specific usage for this actor
                                        "utilization": gpu.get("utilizationGpu", 0),
                                        "nodeGpuOnly": True,
                                    }
                                )

                        actor_view["contextInfo"] = context_info.get(actor_id, {})
                        actor_view["resourceUsage"] = resource_usage.get(actor_id, {})

                        physical_view[node_id]["services"][actor_id] = actor_view

            return dashboard_optional_utils.rest_response(
                success=True,
                message="Physical view data retrieved successfully.",
                physical_view=physical_view,
            )

        except Exception as e:
            logger.error(f"Error retrieving physical view data: {str(e)}")
            return dashboard_optional_utils.rest_response(
                success=False, message=f"Error retrieving physical view data: {str(e)}"
            )

    @routes.get("/call_graph")
    async def get_call_graph(self, req: aiohttp.web.Request) -> aiohttp.web.Response:
        """Return the call graph data by reading from the InsightMonitor HTTP endpoint."""
        try:
            job_id = req.query.get("job_id", "default_job")
            stack_mode = req.query.get("stack_mode", "0")

            # Get insight monitor address from KV store using gcs_aio_client
            address = await self.gcs_aio_client.internal_kv_get(
                "insight_monitor_address",
                namespace="flowinsight",
                timeout=5,
            )

            if not address:
                return dashboard_optional_utils.rest_response(
                    success=False,
                    message="InsightMonitor address not found in KV store",
                )

            host, port = address.decode().split(":")

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"http://{host}:{port}/get_call_graph_data",
                    params={"job_id": job_id, "stack_mode": stack_mode},
                ) as response:
                    if response.status != 200:
                        return dashboard_optional_utils.rest_response(
                            success=False,
                            message=f"Error from insight monitor: {await response.text()}",
                        )

                    graph_data = await response.json()

                    # Add GPU information and actor names to each node in the graph data
                    for node in graph_data.get("services", []):
                        actor_id = node.get("id")
                        # Check if we have this actor in DataSource.actors
                        if actor_id in DataSource.actors:
                            actor_info = DataSource.actors[actor_id]
                            # Use actor name if available, otherwise keep original name
                            if "name" in actor_info and actor_info["name"] != "":
                                node["name"] = actor_info["name"]

                        # Add GPU information for this actor
                        if actor_id in DataSource.actors:
                            actor_info = DataSource.actors[actor_id]
                            node_id = actor_info["address"]["rayletId"]
                            actor_pid = actor_info.get("pid")

                            # Add node ID to actor information
                            node["nodeId"] = node_id

                            # Initialize GPU info for this actor
                            node["gpuDevices"] = []

                            node_physical_stats = DataSource.node_physical_stats.get(
                                node_id, {}
                            )

                            # Add node CPU info from the dictionary if available
                            node["nodeCpuPercent"] = node_physical_stats.get("cpu")

                            # Add node memory info from the dictionary if available
                            node["nodeMem"] = node_physical_stats.get("mem", [])

                            if actor_pid:
                                for gpu in node_physical_stats.get("gpus", []):
                                    for process in gpu.get("processesPids", []):
                                        if process["pid"] == actor_pid:
                                            node["gpuDevices"].append(
                                                {
                                                    "index": gpu["index"],
                                                    "name": gpu["name"],
                                                    "uuid": gpu["uuid"],
                                                    "memoryUsed": process[
                                                        "gpuMemoryUsage"
                                                    ],
                                                    "memoryTotal": gpu["memoryTotal"],
                                                    "utilization": gpu.get(
                                                        "utilizationGpu", 0
                                                    ),
                                                }
                                            )

                            # If actor has no GPU devices but the node has GPUs, add node GPU info
                            if not node["gpuDevices"]:
                                # Add node-level GPU information without usage details
                                for gpu in node_physical_stats.get("gpus", []):
                                    node["gpuDevices"].append(
                                        {
                                            "index": gpu["index"],
                                            "name": gpu["name"],
                                            "uuid": gpu["uuid"],
                                            "memoryTotal": gpu["memoryTotal"],
                                            "memoryUsed": 0,  # No specific usage for this actor
                                            "utilization": gpu.get("utilizationGpu", 0),
                                            "nodeGpuOnly": True,  # Flag to indicate this is node-level info only
                                        }
                                    )

                    return dashboard_optional_utils.rest_response(
                        success=True,
                        message="Call graph data retrieved successfully.",
                        graph_data=graph_data,
                        job_id=job_id,
                    )

        except Exception as e:
            logger.error(f"Error retrieving call graph data: {str(e)}")
            return dashboard_optional_utils.rest_response(
                success=False, message=f"Error retrieving call graph data: {str(e)}"
            )

    @routes.get("/flame_graph")
    async def get_flame_graph(self, req: aiohttp.web.Request) -> aiohttp.web.Response:
        """Return the flame graph data by reading from the InsightMonitor HTTP endpoint."""
        try:
            job_id = req.query.get("job_id", "default_job")

            # Get insight monitor address from KV store using gcs_aio_client
            address = await self.gcs_aio_client.internal_kv_get(
                "insight_monitor_address",
                namespace="flowinsight",
                timeout=5,
            )

            if not address:
                return dashboard_optional_utils.rest_response(
                    success=False,
                    message="InsightMonitor address not found in KV store",
                )

            host, port = address.decode().split(":")

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"http://{host}:{port}/get_flame_graph_data",
                    params={"job_id": job_id},
                ) as response:
                    if response.status != 200:
                        return dashboard_optional_utils.rest_response(
                            success=False,
                            message=f"Error from insight monitor: {await response.text()}",
                        )

                    flame_data = await response.json()

                    return dashboard_optional_utils.rest_response(
                        success=True,
                        message="Flame graph data retrieved successfully.",
                        flame_data=flame_data,
                        job_id=job_id,
                    )

        except Exception as e:
            logger.error(f"Error retrieving flame graph data: {str(e)}")
            return dashboard_optional_utils.rest_response(
                success=False, message=f"Error retrieving flame graph data: {str(e)}"
            )

    async def run(self, server):
        pass

    @staticmethod
    def is_minimal_module():
        return False
