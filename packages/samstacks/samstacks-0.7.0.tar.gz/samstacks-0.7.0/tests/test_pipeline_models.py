import pytest
from pydantic import ValidationError
from pathlib import Path

from samstacks.pipeline_models import (
    PipelineManifestModel,
    PipelineSettingsModel,
    StackModel,
    PipelineInputItem,
    SamConfigContentType,
)


# Tests for PipelineInputItem model
class TestPipelineInputItem:
    def test_valid_input_types(self):
        valid_types = ["string", "number", "boolean"]
        for type_val in valid_types:
            item = PipelineInputItem(type=type_val)
            assert item.type == type_val

    def test_invalid_input_type(self):
        with pytest.raises(ValidationError) as excinfo:
            PipelineInputItem(type="invalid_type")
        assert "Input type must be one of" in str(excinfo.value)
        # Example of checking specific error details in Pydantic V2
        # errors = excinfo.value.errors()
        # assert errors[0]["type"] == "value_error"
        # assert "Input type must be one of" in errors[0]["msg"]

    def test_input_item_with_defaults_and_description(self):
        item = PipelineInputItem(
            type="string", description="A test input", default="hello"
        )
        assert item.type == "string"
        assert item.description == "A test input"
        assert item.default == "hello"


# Tests for StackModel
class TestStackModel:
    def test_stack_model_basic(self):
        stack = StackModel(id="test-stack", dir=Path("./some/dir"))
        assert stack.id == "test-stack"
        assert stack.dir == Path("./some/dir")
        assert stack.params == {}
        assert stack.sam_config_overrides is None

    def test_stack_model_with_all_fields(self):
        sam_config: SamConfigContentType = {
            "default": {"deploy": {"parameters": {"Foo": "Bar"}}}
        }
        stack_data = {
            "id": "s1",
            "dir": "stack_dir",
            "name": "My Stack",
            "description": "A test stack",
            "params": {"Param1": "Value1"},
            "stack_name_suffix": "-dev",
            "region": "us-west-2",
            "profile": "myprofile",
            "if": "${{ env.DEPLOY_IT }}",
            "run": "echo hello",
            "sam_config_overrides": sam_config,
        }
        stack = StackModel(**stack_data)
        assert stack.id == "s1"
        assert stack.dir == Path("stack_dir")
        assert stack.name == "My Stack"
        assert stack.params == {"Param1": "Value1"}
        assert stack.sam_config_overrides == sam_config
        assert stack.if_condition == "${{ env.DEPLOY_IT }}"

    def test_stack_model_aliases(self):
        # Test that 'if' and 'run' aliases work
        stack_data = {
            "id": "s2",
            "dir": Path("./another/dir"),
            "if": "${{ inputs.cond }}",
            "run": "./do_stuff.sh",
        }
        stack = StackModel(**stack_data)  # Uses populate_by_name due to model_config
        assert stack.if_condition == "${{ inputs.cond }}"
        assert stack.run_script == "./do_stuff.sh"


# Tests for PipelineSettingsModel
class TestPipelineSettingsModel:
    def test_pipeline_settings_defaults(self):
        settings = PipelineSettingsModel()
        assert settings.stack_name_prefix is None
        assert settings.default_sam_config is None
        assert settings.inputs == {}

    def test_pipeline_settings_with_values(self):
        """Test pipeline settings with all values provided."""
        data = {
            "stack_name_prefix": "prod-",
            "stack_name_suffix": "-v1",
            "default_region": "us-east-1",
            "default_profile": "production",
            "inputs": {
                "environment": {
                    "type": "string",
                    "description": "Deployment environment",
                    "default": "prod",
                }
            },
            "default_sam_config": {
                "version": 0.1,
                "default": {
                    "deploy": {"parameters": {"capabilities": "CAPABILITY_IAM"}}
                },
            },
        }

        settings = PipelineSettingsModel.model_validate(data)
        assert settings.stack_name_prefix == "prod-"
        assert settings.stack_name_suffix == "-v1"
        assert settings.default_region == "us-east-1"
        assert settings.default_profile == "production"
        assert settings.inputs is not None
        assert "environment" in settings.inputs
        assert settings.inputs["environment"].type == "string"
        assert settings.default_sam_config is not None

    def test_output_masking_defaults(self):
        """Test that output_masking defaults properly."""
        data = {"default_region": "us-west-2"}

        settings = PipelineSettingsModel.model_validate(data)
        assert settings.output_masking.enabled is False
        assert settings.output_masking.categories.account_ids is False


# Tests for PipelineManifestModel
class TestPipelineManifestModel:
    def test_minimal_valid_manifest(self):
        manifest = PipelineManifestModel(
            pipeline_name="TestPipeline",
            stacks=[
                StackModel(id="s1", dir=Path("s1dir")),
                StackModel(id="s2", dir=Path("s2dir")),
            ],
        )
        assert manifest.pipeline_name == "TestPipeline"
        assert len(manifest.stacks) == 2
        assert manifest.stacks[0].id == "s1"

    def test_duplicate_stack_ids(self):
        with pytest.raises(ValidationError) as excinfo:
            PipelineManifestModel(
                pipeline_name="DupPipeline",
                stacks=[
                    StackModel(id="s1", dir=Path("s1dir")),
                    StackModel(id="s1", dir=Path("s2dir")),
                ],
            )
        # Pydantic V2 includes error details in a structured way
        # We check if the message from the validator is in the exception string for simplicity
        assert "Duplicate stack ID found: s1" in str(excinfo.value)
        # errors = excinfo.value.errors()
        # assert errors[0]["type"] == "value_error"
        # assert "Duplicate stack ID found: s1" in errors[0]["msg"]

    def test_empty_stacks_list(self):
        # Pydantic allows empty list if default_factory is used
        manifest = PipelineManifestModel(pipeline_name="EmptyStacks")
        assert manifest.stacks == []

    def test_full_manifest_structure(self):
        manifest_data = {
            "pipeline_name": "FullApp",
            "pipeline_description": "A full application pipeline",
            "pipeline_settings": {
                "stack_name_prefix": "full-app-",
                "default_region": "us-east-1",
                "inputs": {
                    "environment": {"type": "string", "default": "staging"},
                    "log_level": {"type": "string", "description": "Logging level"},
                },
                "default_sam_config": {
                    "version": 0.1,
                    "default": {"deploy": {"parameters": {"ResolveS3": True}}},
                },
            },
            "stacks": [
                {
                    "id": "backend",
                    "dir": "./services/backend",
                    "params": {"TableName": "MyTable"},
                    "sam_config_overrides": {
                        "default": {"deploy": {"parameters": {"MemorySize": 512}}}
                    },
                },
                {
                    "id": "frontend",
                    "dir": "./services/frontend",
                    "if": "${{ inputs.environment == 'prod' }}",
                },
            ],
        }
        pipeline = PipelineManifestModel.model_validate(manifest_data)
        assert pipeline.pipeline_name == "FullApp"
        assert pipeline.pipeline_settings.default_region == "us-east-1"
        assert pipeline.pipeline_settings.inputs is not None
        assert pipeline.pipeline_settings.inputs["environment"].default == "staging"
        assert pipeline.pipeline_settings.default_sam_config is not None
        assert pipeline.stacks[0].id == "backend"
        assert pipeline.stacks[0].sam_config_overrides is not None
        assert pipeline.stacks[1].if_condition == "${{ inputs.environment == 'prod' }}"

    def test_extra_fields_forbidden(self):
        invalid_manifest_data = {
            "pipeline_name": "TestExtra",
            "stacks": [],
            "unknown_top_level_field": "some_value",
        }
        with pytest.raises(ValidationError) as excinfo:
            PipelineManifestModel.model_validate(invalid_manifest_data)
        assert "Extra inputs are not permitted" in str(
            excinfo.value
        )  # Pydantic V2 message for extra fields

        invalid_stack_data = {
            "id": "s1",
            "dir": "./s1dir",
            "unknown_stack_field": "value",
        }
        with pytest.raises(ValidationError) as excinfo:
            StackModel.model_validate(invalid_stack_data)
        assert "Extra inputs are not permitted" in str(excinfo.value)

        invalid_settings_data = {
            "default_region": "us-west-1",
            "unknown_settings_field": "value",
        }
        with pytest.raises(ValidationError) as excinfo:
            PipelineSettingsModel.model_validate(invalid_settings_data)
        assert "Extra inputs are not permitted" in str(excinfo.value)

        invalid_input_item_data = {"type": "string", "unknown_input_field": "value"}
        with pytest.raises(ValidationError) as excinfo:
            PipelineInputItem.model_validate(invalid_input_item_data)
        assert "Extra inputs are not permitted" in str(excinfo.value)

    def test_summary_field_validation(self):
        """Test that the summary field is properly validated."""
        # Test with valid summary
        manifest_data = {
            "pipeline_name": "TestSummary",
            "summary": "# Deployment Complete!\n\nAll stacks deployed successfully.",
            "stacks": [{"id": "test-stack", "dir": "./test"}],
        }
        pipeline = PipelineManifestModel.model_validate(manifest_data)
        assert (
            pipeline.summary
            == "# Deployment Complete!\n\nAll stacks deployed successfully."
        )

        # Test with None summary (should be allowed)
        manifest_data_no_summary = {
            "pipeline_name": "TestNoSummary",
            "stacks": [{"id": "test-stack", "dir": "./test"}],
        }
        pipeline_no_summary = PipelineManifestModel.model_validate(
            manifest_data_no_summary
        )
        assert pipeline_no_summary.summary is None

        # Test with empty string summary (should be allowed)
        manifest_data_empty = {
            "pipeline_name": "TestEmptySummary",
            "summary": "",
            "stacks": [{"id": "test-stack", "dir": "./test"}],
        }
        pipeline_empty = PipelineManifestModel.model_validate(manifest_data_empty)
        assert pipeline_empty.summary == ""

        # Test with multiline summary with template expressions
        manifest_data_templated = {
            "pipeline_name": "TestTemplatedSummary",
            "summary": """# Deployment Complete!
            
Your **${{ inputs.environment }}** environment is ready.

## Infrastructure:
- Stack: ${{ stacks.backend.outputs.StackName }}
- Region: ${{ pipeline.settings.default_region }}
            """,
            "stacks": [{"id": "backend", "dir": "./backend"}],
        }
        pipeline_templated = PipelineManifestModel.model_validate(
            manifest_data_templated
        )
        assert pipeline_templated.summary is not None
        assert "${{ inputs.environment }}" in pipeline_templated.summary
        assert "${{ stacks.backend.outputs.StackName }}" in pipeline_templated.summary
