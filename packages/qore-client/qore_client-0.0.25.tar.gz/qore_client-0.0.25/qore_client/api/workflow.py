from typing import Any, Dict, List, Literal


class WorkflowAPI:
    """Workflow operation utilities for QoreClient"""

    def __init__(self, request_method):
        """
        Initialize with the request method from the parent client

        :param request_method: The _request method from QoreClient
        """
        self._request = request_method

    def get_published_workflow_detail(self, workflow_id: str) -> dict:
        """Published 워크플로우 상세 정보를 가져옵니다."""
        response = self._request("GET", f"/api/workflow/{workflow_id}")
        return response

    def get_draft_workflow_detail(self, workflow_id: str) -> dict:
        """Draft 워크플로우 상세 정보를 가져옵니다."""
        response = self._request("GET", f"/api/workflow/{workflow_id}/draft")
        return response

    def get_version_workflow_detail(self, workflow_id: str, version: str) -> dict:
        """Version 워크플로우 상세 정보를 가져옵니다."""
        response = self._request("GET", f"/api/workflow/{workflow_id}/{version}")
        return response

    def create_workflow(self, workspace_id: str, workflow_name: str, description: str = "") -> dict:
        """워크플로우를 생성합니다."""
        response = self._request(
            "POST",
            "/api/workflow/create",
            data={"workspace_id": workspace_id, "name": workflow_name, "description": description},
        )
        return response

    def save_workflow(self, workflow_id: str, workflow_json: dict) -> dict:
        """워크플로우를 저장합니다."""
        response = self._request(
            "PUT", f"/api/workflow/{workflow_id}/draft/save", json=workflow_json
        )
        if response:
            return {"status": "success"}
        else:
            return {"status": "failed"}

    def execute_workflow(self, workflow_id: str, workflow_json: dict) -> dict:
        """워크플로우를 실행합니다."""
        response = self._request(
            "POST", f"/api/workflow/{workflow_id}/draft/execute", json=workflow_json
        )
        return format_execution_result(response)

    def execute_published_workflow(
        self,
        workflow_id: str,
        format: Literal["raw", "logs"] = "logs",
        version: Literal["latest"] | int = "latest",
        **kwargs,
    ) -> List[str] | Dict[str, Any]:
        """Published 워크플로우를 실행합니다."""
        response_data = self._request(
            "POST", f"/api/workflow/{workflow_id}/{version}/execute", json=kwargs
        )

        if response_data is None:
            raise ValueError("Failed to execute workflow, received None response.")

        if format == "logs":
            return format_execution_result(response_data)
        elif format == "raw":
            return response_data
        else:
            raise ValueError(f"Invalid format: {format}")


def format_execution_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Formats the workflow execution result into a dictionary.
    Sorts nodes by start time and includes duration, status, and logs for each.

    :param result: The raw execution result from the API.
    :return: A dictionary with formatted execution details for each node, sorted by start time.
    """
    import datetime

    if not isinstance(result, dict):
        return {"error": "Invalid result format: not a dictionary."}

    node_executions = []
    for node_id, data in result.items():
        if isinstance(data, dict) and "start_time" in data and "end_time" in data:
            node_executions.append((node_id, data))

    try:
        # Sort by start_time
        node_executions.sort(key=lambda x: x[1]["start_time"])
    except (KeyError, TypeError):
        # Fallback to original order if sorting fails
        pass

    output_data = {}
    for node_id, data in node_executions:
        start_time_str = data.get("start_time")
        end_time_str = data.get("end_time")

        duration_seconds = None
        if start_time_str and end_time_str:
            try:
                start_time = datetime.datetime.fromisoformat(start_time_str.replace("Z", "+00:00"))
                end_time = datetime.datetime.fromisoformat(end_time_str.replace("Z", "+00:00"))
                duration = end_time - start_time
                duration_seconds = duration.total_seconds()
            except (ValueError, TypeError):
                pass

        status = data.get("status", "N/A")

        execute_result = data.get("execute_result", {})
        logs = execute_result.get("logs") or ""

        output_data[node_id] = {
            "duration_seconds": duration_seconds,
            "status": status,
            "logs": logs,
        }

    if not output_data:
        return result

    return output_data
