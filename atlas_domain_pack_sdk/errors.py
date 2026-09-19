"""
Structured error classes for the Atlas Kernel.
All errors include location, file, object id/name, field, problem, and suggested fix where possible.
"""

from __future__ import annotations


class AtlasError(Exception):
    """Base class for all Atlas Kernel errors."""

    def __init__(self, message: str, **context):
        super().__init__(message)
        self.context = context

    def __str__(self):
        base = super().__str__()
        if self.context:
            parts = [f"{k}={v!r}" for k, v in self.context.items() if v is not None]
            return f"{base} ({', '.join(parts)})"
        return base


class DomainPackLoadError(AtlasError):
    """
    Raised when a domain pack cannot be loaded.
    Covers missing files, malformed manifests, and failed registration.
    """
    def __init__(
        self,
        message: str,
        pack_name: str | None = None,
        file: str | None = None,
        suggested_fix: str | None = None,
    ):
        super().__init__(message, pack_name=pack_name, file=file, suggested_fix=suggested_fix)
        self.pack_name = pack_name
        self.file = file
        self.suggested_fix = suggested_fix


class RegistryValidationError(AtlasError):
    """
    Raised when a type definition fails registry validation.
    """
    def __init__(
        self,
        message: str,
        pack_name: str | None = None,
        file: str | None = None,
        object_name: str | None = None,
        field: str | None = None,
        suggested_fix: str | None = None,
    ):
        super().__init__(
            message,
            pack_name=pack_name,
            file=file,
            object_name=object_name,
            field=field,
            suggested_fix=suggested_fix,
        )
        self.pack_name = pack_name
        self.file = file
        self.object_name = object_name
        self.field = field
        self.suggested_fix = suggested_fix


class UnknownTypeReferenceError(AtlasError):
    """
    Raised when a definition references a type that is not registered.
    """
    def __init__(
        self,
        message: str,
        reference: str | None = None,
        referencing_object: str | None = None,
        file: str | None = None,
        did_you_mean: str | None = None,
    ):
        super().__init__(
            message,
            reference=reference,
            referencing_object=referencing_object,
            file=file,
            did_you_mean=did_you_mean,
        )
        self.reference = reference
        self.referencing_object = referencing_object
        self.file = file
        self.did_you_mean = did_you_mean


class DuplicateDefinitionError(AtlasError):
    """
    Raised when a definition with the same name/key already exists in the registry.
    """
    def __init__(
        self,
        message: str,
        type_name: str | None = None,
        existing_pack: str | None = None,
        new_pack: str | None = None,
    ):
        super().__init__(
            message,
            type_name=type_name,
            existing_pack=existing_pack,
            new_pack=new_pack,
        )
        self.type_name = type_name
        self.existing_pack = existing_pack
        self.new_pack = new_pack


class SchemaValidationError(AtlasError):
    """
    Raised when a runtime object (node, edge, packet, candidate) fails schema validation.
    """
    def __init__(
        self,
        message: str,
        object_type: str | None = None,
        object_id: str | None = None,
        field: str | None = None,
        value=None,
    ):
        super().__init__(
            message,
            object_type=object_type,
            object_id=object_id,
            field=field,
            value=value,
        )
        self.object_type = object_type
        self.object_id = object_id
        self.field = field
        self.value = value


class PacketGenerationError(AtlasError):
    """
    Raised when a task packet cannot be generated, e.g. unknown detected_type or missing template.
    """
    def __init__(
        self,
        message: str,
        detected_type: str | None = None,
        domain_pack: str | None = None,
        suggested_fix: str | None = None,
    ):
        super().__init__(
            message,
            detected_type=detected_type,
            domain_pack=domain_pack,
            suggested_fix=suggested_fix,
        )
        self.detected_type = detected_type
        self.domain_pack = domain_pack
        self.suggested_fix = suggested_fix


class CheckpointEvaluationError(AtlasError):
    """
    Raised when a verification checkpoint cannot be evaluated (distinct from a checkpoint *failing*).
    """
    def __init__(
        self,
        message: str,
        checkpoint_name: str | None = None,
        candidate_id: str | None = None,
    ):
        super().__init__(
            message,
            checkpoint_name=checkpoint_name,
            candidate_id=candidate_id,
        )
        self.checkpoint_name = checkpoint_name
        self.candidate_id = candidate_id


class CommitValidationError(AtlasError):
    """
    Raised when a result candidate fails commit validation (checkpoint failure, not system error).
    """
    def __init__(
        self,
        message: str,
        candidate_id: str | None = None,
        checkpoint_name: str | None = None,
        failure_reason: str | None = None,
    ):
        super().__init__(
            message,
            candidate_id=candidate_id,
            checkpoint_name=checkpoint_name,
            failure_reason=failure_reason,
        )
        self.candidate_id = candidate_id
        self.checkpoint_name = checkpoint_name
        self.failure_reason = failure_reason
