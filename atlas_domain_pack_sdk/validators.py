"""
Validation logic for registry entries and runtime objects.
All validation raises structured errors from errors.py.
Silent failures are unacceptable — every bad definition must fail loud and early.
"""

from __future__ import annotations

from .errors import RegistryValidationError, SchemaValidationError


# ---------------------------------------------------------------------------
# Required field validators for domain pack definitions
# ---------------------------------------------------------------------------

NODE_TYPE_REQUIRED_FIELDS = ["type_name", "description"]
EDGE_TYPE_REQUIRED_FIELDS = ["type_name", "description"]
PROCEDURE_REQUIRED_FIELDS = ["name", "version", "procedure_type", "description", "output_schema", "steps"]
LENS_REQUIRED_FIELDS = ["name", "version", "description", "activation_conditions"]
CHECKPOINT_REQUIRED_FIELDS = ["name", "version", "checkpoint_type", "description", "pass_conditions", "failure_conditions"]
WORKER_REQUIRED_FIELDS = ["worker_name", "worker_type", "max_risk_tier", "cost_tier"]
PACKET_TEMPLATE_REQUIRED_FIELDS = ["template_name", "detected_type", "risk_tier"]
MANIFEST_REQUIRED_FIELDS = ["pack_name", "version", "description"]


def validate_node_type_definition(defn: dict, pack_name: str, file: str) -> None:
    """Validate a node type definition dict. Raises RegistryValidationError on failure."""
    _check_required_fields(defn, NODE_TYPE_REQUIRED_FIELDS, pack_name, file, "node_type")
    _check_string_field(defn, "type_name", pack_name, file)
    _check_string_field(defn, "description", pack_name, file)
    if "required_fields" in defn and not isinstance(defn["required_fields"], list):
        raise RegistryValidationError(
            f"'required_fields' must be a list",
            pack_name=pack_name, file=file,
            object_name=defn.get("type_name"),
            field="required_fields",
            suggested_fix="Change required_fields to a JSON array, e.g. []",
        )
    if "allowed_parent_types" in defn and not isinstance(defn["allowed_parent_types"], list):
        raise RegistryValidationError(
            f"'allowed_parent_types' must be a list",
            pack_name=pack_name, file=file,
            object_name=defn.get("type_name"),
            field="allowed_parent_types",
        )


def validate_edge_type_definition(defn: dict, pack_name: str, file: str) -> None:
    """Validate an edge type definition dict."""
    _check_required_fields(defn, EDGE_TYPE_REQUIRED_FIELDS, pack_name, file, "edge_type")
    _check_string_field(defn, "type_name", pack_name, file)
    _check_string_field(defn, "description", pack_name, file)
    for list_field in ("allowed_source_types", "allowed_target_types"):
        if list_field in defn and not isinstance(defn[list_field], list):
            raise RegistryValidationError(
                f"'{list_field}' must be a list",
                pack_name=pack_name, file=file,
                object_name=defn.get("type_name"),
                field=list_field,
            )


def validate_procedure_definition(defn: dict, pack_name: str, file: str) -> None:
    """Validate a procedure definition dict."""
    _check_required_fields(defn, PROCEDURE_REQUIRED_FIELDS, pack_name, file, "procedure")
    if not isinstance(defn.get("steps"), list):
        raise RegistryValidationError(
            "'steps' must be a list",
            pack_name=pack_name, file=file,
            object_name=defn.get("name"),
            field="steps",
            suggested_fix="Change steps to a JSON array of step strings",
        )


def validate_lens_definition(defn: dict, pack_name: str, file: str) -> None:
    """Validate a lens definition dict."""
    _check_required_fields(defn, LENS_REQUIRED_FIELDS, pack_name, file, "lens")
    if not isinstance(defn.get("activation_conditions"), list):
        raise RegistryValidationError(
            "'activation_conditions' must be a list",
            pack_name=pack_name, file=file,
            object_name=defn.get("name"),
            field="activation_conditions",
        )


def validate_checkpoint_definition(defn: dict, pack_name: str, file: str) -> None:
    """Validate a verification checkpoint definition dict."""
    _check_required_fields(defn, CHECKPOINT_REQUIRED_FIELDS, pack_name, file, "checkpoint")
    for list_field in ("pass_conditions", "failure_conditions"):
        if not isinstance(defn.get(list_field), list):
            raise RegistryValidationError(
                f"'{list_field}' must be a list",
                pack_name=pack_name, file=file,
                object_name=defn.get("name"),
                field=list_field,
            )


def validate_worker_definition(defn: dict, pack_name: str, file: str) -> None:
    """Validate a worker capability definition dict."""
    _check_required_fields(defn, WORKER_REQUIRED_FIELDS, pack_name, file, "worker")
    valid_risk_tiers = {"low", "medium", "high", "critical"}
    risk = defn.get("max_risk_tier", "")
    if risk not in valid_risk_tiers:
        raise RegistryValidationError(
            f"Invalid max_risk_tier '{risk}'",
            pack_name=pack_name, file=file,
            object_name=defn.get("worker_name"),
            field="max_risk_tier",
            suggested_fix=f"Must be one of: {sorted(valid_risk_tiers)}",
        )
    valid_cost_tiers = {"free", "low", "medium", "high"}
    cost = defn.get("cost_tier", "")
    if cost not in valid_cost_tiers:
        raise RegistryValidationError(
            f"Invalid cost_tier '{cost}'",
            pack_name=pack_name, file=file,
            object_name=defn.get("worker_name"),
            field="cost_tier",
            suggested_fix=f"Must be one of: {sorted(valid_cost_tiers)}",
        )


def validate_packet_template(defn: dict, pack_name: str, file: str) -> None:
    """Validate a packet template definition dict."""
    _check_required_fields(defn, PACKET_TEMPLATE_REQUIRED_FIELDS, pack_name, file, "packet_template")
    valid_risk_tiers = {"low", "medium", "high", "critical"}
    risk = defn.get("risk_tier", "")
    if risk not in valid_risk_tiers:
        raise RegistryValidationError(
            f"Invalid risk_tier '{risk}'",
            pack_name=pack_name, file=file,
            object_name=defn.get("template_name"),
            field="risk_tier",
            suggested_fix=f"Must be one of: {sorted(valid_risk_tiers)}",
        )
    confidence = defn.get("confidence_threshold_for_auto_commit", 0.85)
    if not isinstance(confidence, (int, float)) or not (0.0 <= float(confidence) <= 1.0):
        raise RegistryValidationError(
            f"confidence_threshold_for_auto_commit must be a float between 0.0 and 1.0",
            pack_name=pack_name, file=file,
            object_name=defn.get("template_name"),
            field="confidence_threshold_for_auto_commit",
        )


def validate_manifest(manifest: dict, pack_name: str, file: str) -> None:
    """Validate a pack_manifest.json dict."""
    _check_required_fields(manifest, MANIFEST_REQUIRED_FIELDS, pack_name, file, "manifest")


# ---------------------------------------------------------------------------
# Runtime object validators
# ---------------------------------------------------------------------------

def validate_node_object(node_dict: dict, registered_types: set) -> None:
    """Validate a node dict before inserting into the atlas."""
    for field in ("id", "type", "name", "created_at", "updated_at"):
        if not node_dict.get(field):
            raise SchemaValidationError(
                f"Node missing required field '{field}'",
                object_type="node",
                object_id=node_dict.get("id"),
                field=field,
            )
    confidence = node_dict.get("confidence", 1.0)
    if not isinstance(confidence, (int, float)) or not (0.0 <= float(confidence) <= 1.0):
        raise SchemaValidationError(
            f"Node confidence must be between 0.0 and 1.0, got {confidence!r}",
            object_type="node",
            object_id=node_dict.get("id"),
            field="confidence",
            value=confidence,
        )
    node_type = node_dict.get("type", "")
    if registered_types and node_type not in registered_types:
        raise SchemaValidationError(
            f"Unknown node type '{node_type}'",
            object_type="node",
            object_id=node_dict.get("id"),
            field="type",
            value=node_type,
        )


def validate_edge_object(edge_dict: dict, registered_types: set) -> None:
    """Validate an edge dict before inserting into the atlas."""
    for field in ("id", "type", "source_node_id", "target_node_id", "created_at", "updated_at"):
        if not edge_dict.get(field):
            raise SchemaValidationError(
                f"Edge missing required field '{field}'",
                object_type="edge",
                object_id=edge_dict.get("id"),
                field=field,
            )
    edge_type = edge_dict.get("type", "")
    if registered_types and edge_type not in registered_types:
        raise SchemaValidationError(
            f"Unknown edge type '{edge_type}'",
            object_type="edge",
            object_id=edge_dict.get("id"),
            field="type",
            value=edge_type,
        )


def validate_result_candidate(candidate_dict: dict) -> None:
    """Validate a result candidate before commit evaluation."""
    for field in ("id", "task_packet_id", "result_type", "created_at"):
        if not candidate_dict.get(field):
            raise SchemaValidationError(
                f"ResultCandidate missing required field '{field}'",
                object_type="result_candidate",
                object_id=candidate_dict.get("id"),
                field=field,
            )
    confidence = candidate_dict.get("confidence", 0.0)
    if not isinstance(confidence, (int, float)) or not (0.0 <= float(confidence) <= 1.0):
        raise SchemaValidationError(
            f"ResultCandidate confidence must be between 0.0 and 1.0, got {confidence!r}",
            object_type="result_candidate",
            object_id=candidate_dict.get("id"),
            field="confidence",
            value=confidence,
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _check_required_fields(
    defn: dict,
    required: list,
    pack_name: str,
    file: str,
    object_kind: str,
) -> None:
    for f in required:
        if f not in defn or defn[f] is None or defn[f] == "":
            raise RegistryValidationError(
                f"{object_kind} missing required field '{f}'",
                pack_name=pack_name,
                file=file,
                object_name=defn.get("type_name") or defn.get("name") or defn.get("worker_name") or defn.get("template_name"),
                field=f,
                suggested_fix=f"Add a non-empty '{f}' field to this {object_kind} definition",
            )


def _check_string_field(defn: dict, field_name: str, pack_name: str, file: str) -> None:
    val = defn.get(field_name, "")
    if not isinstance(val, str):
        raise RegistryValidationError(
            f"Field '{field_name}' must be a string, got {type(val).__name__}",
            pack_name=pack_name,
            file=file,
            object_name=defn.get("type_name") or defn.get("name"),
            field=field_name,
        )
