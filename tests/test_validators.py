"""Tests for validators.py."""
import unittest
from atlas_domain_pack_sdk.validators import (
    validate_node_type_definition,
    validate_edge_type_definition,
    validate_procedure_definition,
    validate_lens_definition,
    validate_checkpoint_definition,
    validate_packet_template,
    validate_node_object,
    validate_edge_object,
)
from atlas_domain_pack_sdk.errors import RegistryValidationError, SchemaValidationError


class TestNodeTypeValidator(unittest.TestCase):

    def test_valid_definition_passes(self):
        validate_node_type_definition(
            {"type_name": "person", "description": "A person."},
            "test_pack", "node_types.json"
        )

    def test_missing_type_name_raises(self):
        with self.assertRaises(RegistryValidationError) as ctx:
            validate_node_type_definition(
                {"description": "No type_name."}, "test_pack", "node_types.json"
            )
        self.assertIn("type_name", str(ctx.exception))

    def test_missing_description_raises(self):
        with self.assertRaises(RegistryValidationError) as ctx:
            validate_node_type_definition(
                {"type_name": "person"}, "test_pack", "node_types.json"
            )
        self.assertIn("description", str(ctx.exception))

    def test_required_fields_must_be_list(self):
        with self.assertRaises(RegistryValidationError):
            validate_node_type_definition(
                {"type_name": "x", "description": "x", "required_fields": "not_a_list"},
                "p", "f"
            )


class TestEdgeTypeValidator(unittest.TestCase):

    def test_valid_edge_type(self):
        validate_edge_type_definition(
            {"type_name": "contains", "description": "Parent contains child."},
            "test_pack", "edge_types.json"
        )

    def test_missing_type_name_raises(self):
        with self.assertRaises(RegistryValidationError):
            validate_edge_type_definition({"description": "No name."}, "p", "f")

    def test_allowed_types_must_be_list(self):
        with self.assertRaises(RegistryValidationError):
            validate_edge_type_definition(
                {"type_name": "e", "description": "e",
                 "allowed_source_types": "not_a_list"},
                "p", "f"
            )


class TestProcedureValidator(unittest.TestCase):

    def test_valid_procedure(self):
        validate_procedure_definition(
            {"name": "P.v1", "version": "1.0", "procedure_type": "inference",
             "description": "A procedure.", "output_schema": "Node", "steps": ["step"]},
            "p", "f"
        )

    def test_missing_name_raises(self):
        with self.assertRaises(RegistryValidationError):
            validate_procedure_definition(
                {"version": "1.0", "procedure_type": "inference",
                 "description": "A procedure.", "output_schema": "Node", "steps": []},
                "p", "f"
            )

    def test_steps_must_be_list(self):
        with self.assertRaises(RegistryValidationError):
            validate_procedure_definition(
                {"name": "P.v1", "version": "1.0", "procedure_type": "inference",
                 "description": "desc", "output_schema": "Node", "steps": "not_a_list"},
                "p", "f"
            )


class TestLensValidator(unittest.TestCase):

    def test_valid_lens(self):
        validate_lens_definition(
            {"name": "lens.v1", "version": "1.0", "description": "A lens.",
             "activation_conditions": ["low_confidence"]},
            "p", "f"
        )

    def test_activation_conditions_must_be_list(self):
        with self.assertRaises(RegistryValidationError):
            validate_lens_definition(
                {"name": "lens.v1", "version": "1.0", "description": "A lens.",
                 "activation_conditions": "not_a_list"},
                "p", "f"
            )


class TestCheckpointValidator(unittest.TestCase):

    def test_valid_checkpoint(self):
        validate_checkpoint_definition(
            {"name": "cp.v1", "version": "1.0", "checkpoint_type": "evidence",
             "description": "A checkpoint.", "pass_conditions": ["has_evidence"],
             "failure_conditions": ["no_evidence"]},
            "p", "f"
        )

    def test_pass_conditions_must_be_list(self):
        with self.assertRaises(RegistryValidationError):
            validate_checkpoint_definition(
                {"name": "cp.v1", "version": "1.0", "checkpoint_type": "evidence",
                 "description": "desc", "pass_conditions": "not_a_list",
                 "failure_conditions": []},
                "p", "f"
            )


class TestPacketTemplateValidator(unittest.TestCase):

    def test_valid_template(self):
        validate_packet_template(
            {"template_name": "tmpl", "detected_type": "claim", "risk_tier": "high"},
            "p", "f"
        )

    def test_invalid_risk_tier(self):
        with self.assertRaises(RegistryValidationError) as ctx:
            validate_packet_template(
                {"template_name": "tmpl", "detected_type": "claim", "risk_tier": "extreme"},
                "p", "f"
            )
        self.assertIn("risk_tier", str(ctx.exception))

    def test_confidence_out_of_range(self):
        with self.assertRaises(RegistryValidationError):
            validate_packet_template(
                {"template_name": "tmpl", "detected_type": "claim", "risk_tier": "low",
                 "confidence_threshold_for_auto_commit": 1.5},
                "p", "f"
            )


class TestNodeObjectValidator(unittest.TestCase):

    def _valid_node(self):
        return {
            "id": "abc", "type": "person", "name": "Example Person",
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z",
            "confidence": 1.0,
        }

    def test_valid_node_passes(self):
        validate_node_object(self._valid_node(), {"person"})

    def test_missing_id_raises(self):
        node = self._valid_node()
        del node["id"]
        with self.assertRaises(SchemaValidationError):
            validate_node_object(node, {"person"})

    def test_confidence_out_of_range_raises(self):
        node = self._valid_node()
        node["confidence"] = 1.5
        with self.assertRaises(SchemaValidationError):
            validate_node_object(node, {"person"})

    def test_unknown_type_raises(self):
        node = self._valid_node()
        with self.assertRaises(SchemaValidationError):
            validate_node_object(node, {"memory_domain"})  # "person" not in set


class TestEdgeObjectValidator(unittest.TestCase):

    def _valid_edge(self):
        return {
            "id": "e1", "type": "contains",
            "source_node_id": "n1", "target_node_id": "n2",
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z",
        }

    def test_valid_edge_passes(self):
        validate_edge_object(self._valid_edge(), {"contains"})

    def test_missing_source_raises(self):
        edge = self._valid_edge()
        del edge["source_node_id"]
        with self.assertRaises(SchemaValidationError):
            validate_edge_object(edge, {"contains"})

    def test_unknown_edge_type_raises(self):
        edge = self._valid_edge()
        with self.assertRaises(SchemaValidationError):
            validate_edge_object(edge, {"relates_to"})  # "contains" not in set


if __name__ == "__main__":
    unittest.main()
