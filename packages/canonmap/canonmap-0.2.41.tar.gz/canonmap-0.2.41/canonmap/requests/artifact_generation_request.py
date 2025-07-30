from pathlib import Path
from typing import Optional, List, Dict, Union, Any
import pandas as pd
from pydantic import BaseModel, Field
import warnings
import types

class EntityField(BaseModel):
    """Configuration for a field to be canonicalized."""
    table_name: str
    field_name: str

class SemanticField(BaseModel):
    """Configuration for a field to be extracted as semantic text."""
    table_name: str
    field_name: str

class SemanticTextTitleField(BaseModel):
    """Configuration for specifying which field to use as the title for semantic text files."""
    table_name: str
    field_name: str

class CommaSeparatedField(BaseModel):
    """Configuration for a field that should be split on commas."""
    table_name: str
    field_name: str



class InputConfig(BaseModel):
    source_name: str = "data"
    table_name: Optional[str] = None
    recursive: bool = False
    file_pattern: Union[str, List[str]] = ["*.csv", "*.json"]
    table_name_from_file: bool = True
    num_rows: Optional[int] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "source_name": "my_data",
                "table_name": "custom_name",
                "recursive": True,
                "file_pattern": ["*.csv", "*.json"],
                "table_name_from_file": False,
                "num_rows": 1000
            }
        }

class ProcessingConfig(BaseModel):
    normalize_table_names: bool = True
    normalize_field_names: bool = True
    use_other_fields_as_metadata: bool = True

class FieldMappingConfig(BaseModel):
    entity_fields: Optional[List[EntityField]] = Field(default_factory=list)
    semantic_fields: Optional[List[SemanticField]] = Field(default_factory=list)
    semantic_text_title_fields: Optional[List[SemanticTextTitleField]] = Field(default_factory=list)
    comma_separated_fields: Optional[List[CommaSeparatedField]] = Field(default_factory=list)

class ArtifactGenerationConfig(BaseModel):
    generate_canonical_entities: bool = True
    generate_schemas: bool = True
    generate_embeddings: bool = True
    generate_semantic_texts: bool = True
    save_processed_data: bool = True
    database_type: str = "postgres"
    upload_artifacts_to_gcs: bool = False


class ArtifactGenerationRequest(BaseModel):
    """Configuration for generating canonicalization artifacts.
    
    Focuses on WHAT to generate rather than WHERE to store it.
    Storage configuration is handled by CanonMapArtifactsConfig.
    If 'upload_artifacts_to_gcs' is True, generated artifacts will be uploaded to GCS according to the sync strategy in the config.
    
    Table Naming Behavior:
        The table naming depends on the input type and configuration:
        
        1. Single File Input:
           - If table_name is provided: Uses the provided name
           - If table_name is None: Uses filename without extension
           
        2. Directory Input (Multiple Files):
           - If table_name is provided AND table_name_from_file=False:
             * Single file found: Uses the provided table_name
             * Multiple files found: Uses table_name as prefix (e.g., "custom_1", "custom_2")
           - If table_name is provided AND table_name_from_file=True:
             * Ignores table_name, uses file-based names (with warning)
           - If table_name is None AND table_name_from_file=False:
             * Single file found: Uses source_name
             * Multiple files found: Uses "source_name_table_1", "source_name_table_2", etc.
           - If table_name is None AND table_name_from_file=True (default):
             * Uses file-based names (e.g., "main", "subdir1_file1")
    
    Examples:
        # Single file pattern
        request = ArtifactGenerationRequest(
            input_path="/path/to/data",
            file_pattern="*.csv"
        )
        
        # Multiple file patterns
        request = ArtifactGenerationRequest(
            input_path="/path/to/data",
            file_pattern=["*.csv", "*.tsv", "*.xlsx"]
        )
        
        # With recursive search (handles naming conflicts automatically)
        request = ArtifactGenerationRequest(
            input_path="/path/to/data",
            file_pattern=["*.csv", "*.json"],
            recursive=True
        )
        
        # Custom table naming for directory input
        request = ArtifactGenerationRequest(
            input_path="/path/to/data",
            table_name="my_data",
            table_name_from_file=False,
            recursive=True
        )
        
        # Generic naming using source_name
        request = ArtifactGenerationRequest(
            input_path="/path/to/data",
            source_name="customer_data",
            table_name=None,
            table_name_from_file=False,
            recursive=True
        )
        # Results in: "customer_data_table_1", "customer_data_table_2", etc.
        
    Note:
        When recursive=True, table names are derived from the relative path to avoid conflicts.
        For example, "subdir/file.csv" becomes "subdir_file" as the table name.
        If conflicts still occur, incremental counters are appended (e.g., "table_1", "table_2").
        
    Deprecation Notice:
        The following parameters are deprecated and will be removed in future releases.
        Use the corresponding nested configs instead:
        - table_name → input_config.table_name
        - recursive → input_config.recursive  
        - file_pattern → input_config.file_pattern
        - table_name_from_file → input_config.table_name_from_file
        - num_rows → input_config.num_rows
        - normalize_table_names → processing_config.normalize_table_names
        - normalize_field_names → processing_config.normalize_field_names
        - use_other_fields_as_metadata → processing_config.use_other_fields_as_metadata
        - entity_fields → field_mapping_config.entity_fields
        - semantic_fields → field_mapping_config.semantic_fields
        - semantic_text_title_fields → field_mapping_config.semantic_text_title_fields
        - comma_separated_fields → field_mapping_config.comma_separated_fields
        - generate_canonical_entities → artifact_generation_config.generate_canonical_entities
        - generate_schemas → artifact_generation_config.generate_schemas
        - generate_embeddings → artifact_generation_config.generate_embeddings
        - generate_semantic_texts → artifact_generation_config.generate_semantic_texts
        - save_processed_data → artifact_generation_config.save_processed_data
        - database_type → artifact_generation_config.database_type
        - upload_artifacts_to_gcs → artifact_generation_config.upload_artifacts_to_gcs
    """
    
    input_path: str  # Restrict to str for FastAPI compatibility

    input_config: InputConfig = InputConfig()
    processing_config: ProcessingConfig = ProcessingConfig()
    field_mapping_config: FieldMappingConfig = FieldMappingConfig()
    artifact_generation_config: ArtifactGenerationConfig = ArtifactGenerationConfig()
    
    # Legacy parameters - DEPRECATED
    table_name: Optional[str] = Field(
        default=None,
        description="DEPRECATED: Use input_config.table_name instead. Will be removed in future releases."
    )
    normalize_table_names: bool = Field(
        default=True,
        description="DEPRECATED: Use processing_config.normalize_table_names instead. Will be removed in future releases."
    )
    recursive: bool = Field(
        default=False,
        description="DEPRECATED: Use input_config.recursive instead. Will be removed in future releases."
    )
    file_pattern: Union[str, List[str]] = Field(
        default=["*.csv", "*.json"],
        description="DEPRECATED: Use input_config.file_pattern instead. Will be removed in future releases."
    )
    table_name_from_file: bool = Field(
        default=True,
        description="DEPRECATED: Use input_config.table_name_from_file instead. Will be removed in future releases."
    )
    entity_fields: Optional[List[EntityField]] = Field(
        default_factory=list,
        description="DEPRECATED: Use field_mapping_config.entity_fields instead. Will be removed in future releases."
    )
    semantic_fields: Optional[List[SemanticField]] = Field(
        default_factory=list,
        description="DEPRECATED: Use field_mapping_config.semantic_fields instead. Will be removed in future releases."
    )
    semantic_text_title_fields: Optional[List[SemanticTextTitleField]] = Field(
        default_factory=list,
        description="DEPRECATED: Use field_mapping_config.semantic_text_title_fields instead. Will be removed in future releases."
    )
    comma_separated_fields: Optional[List[CommaSeparatedField]] = Field(
        default_factory=list,
        description="DEPRECATED: Use field_mapping_config.comma_separated_fields instead. Will be removed in future releases."
    )
    use_other_fields_as_metadata: bool = Field(
        default=True,
        description="DEPRECATED: Use processing_config.use_other_fields_as_metadata instead. Will be removed in future releases."
    )
    num_rows: Optional[int] = Field(
        default=None,
        description="DEPRECATED: Use input_config.num_rows instead. Will be removed in future releases."
    )
    generate_canonical_entities: bool = Field(
        default=True,
        description="DEPRECATED: Use artifact_generation_config.generate_canonical_entities instead. Will be removed in future releases."
    )
    generate_schemas: bool = Field(
        default=True,
        description="DEPRECATED: Use artifact_generation_config.generate_schemas instead. Will be removed in future releases."
    )
    generate_embeddings: bool = Field(
        default=True,
        description="DEPRECATED: Use artifact_generation_config.generate_embeddings instead. Will be removed in future releases."
    )
    generate_semantic_texts: bool = Field(
        default=True,
        description="DEPRECATED: Use artifact_generation_config.generate_semantic_texts instead. Will be removed in future releases."
    )
    save_processed_data: bool = Field(
        default=True,
        description="DEPRECATED: Use artifact_generation_config.save_processed_data instead. Will be removed in future releases."
    )
    database_type: str = Field(
        default="postgres",
        description="DEPRECATED: Use artifact_generation_config.database_type instead. Will be removed in future releases."
    )
    normalize_field_names: bool = Field(
        default=True,
        description="DEPRECATED: Use processing_config.normalize_field_names instead. Will be removed in future releases."
    )
    upload_artifacts_to_gcs: bool = Field(
        default=False,
        description="DEPRECATED: Use artifact_generation_config.upload_artifacts_to_gcs instead. Will be removed in future releases."
    )

    class Config:
        arbitrary_types_allowed = True  # Allow pandas DataFrame and Path objects

    def __init__(self, **data):
        super().__init__(**data)
        self._warn_deprecated_params()

    def _warn_deprecated_params(self):
        """Warn about deprecated parameters that are being used."""
        deprecated_params = [
            'table_name', 'normalize_table_names', 'recursive', 'file_pattern',
            'table_name_from_file', 'entity_fields', 'semantic_fields',
            'semantic_text_title_fields', 'comma_separated_fields',
            'use_other_fields_as_metadata', 'num_rows', 'generate_canonical_entities',
            'generate_schemas', 'generate_embeddings', 'generate_semantic_texts',
            'save_processed_data', 'database_type', 'normalize_field_names',
            'upload_artifacts_to_gcs'
        ]
        
        used_deprecated = []
        for param in deprecated_params:
            # Use the actual field value, not the property
            value = self.__dict__.get(param, None)
            if value is None and param in self.model_fields:
                value = self.model_fields[param].default
            if self._is_param_used(param, value):
                used_deprecated.append(param)
        
        if used_deprecated:
            warnings.warn(
                f"Deprecated parameters detected: {', '.join(used_deprecated)}. "
                "These will be removed in future releases. Use the corresponding nested configs instead. "
                "See the class docstring for migration guide.",
                DeprecationWarning,
                stacklevel=2
            )

    def _is_param_used(self, param: str, value: Any) -> bool:
        """Check if a deprecated parameter is actually being used."""
        # If value is a property or method object, treat as default (not used)
        if isinstance(value, property) or isinstance(value, types.MethodType):
            return False
        default_values = {
            'table_name': None, 'normalize_table_names': True, 'recursive': False,
            'file_pattern': ["*.csv", "*.json"], 'table_name_from_file': True,
            'entity_fields': [], 'semantic_fields': [], 'semantic_text_title_fields': [],
            'comma_separated_fields': [], 'use_other_fields_as_metadata': True,
            'num_rows': None, 'generate_canonical_entities': True, 'generate_schemas': True,
            'generate_embeddings': True, 'generate_semantic_texts': True,
            'save_processed_data': True, 'database_type': "postgres",
            'normalize_field_names': True, 'upload_artifacts_to_gcs': False
        }
        default = default_values.get(param)
        if param in ['table_name', 'num_rows']:
            return value is not None
        elif param in ['entity_fields', 'semantic_fields', 'semantic_text_title_fields', 'comma_separated_fields']:
            return isinstance(value, list) and len(value) > 0
        else:
            return value != default

    def to_dict(self) -> Dict[str, Any]:
        """Convert the request to a dictionary for serialization."""
        return {
            'input_path': str(self.input_path) if isinstance(self.input_path, Path) else self.input_path,
            'source_name': self.source_name,
            'table_name': self.table_name,
            'normalize_table_names': self.normalize_table_names,
            'recursive': self.recursive,
            'file_pattern': self.file_pattern,  # Can be string or list
            'table_name_from_file': self.table_name_from_file,
            'entity_fields': [{'table_name': ef.table_name, 'field_name': ef.field_name} for ef in self.entity_fields],
            'semantic_fields': [{'table_name': sf.table_name, 'field_name': sf.field_name} for sf in self.semantic_fields],
            'semantic_text_title_fields': [{'table_name': stf.table_name, 'field_name': stf.field_name} for stf in self.semantic_text_title_fields],
            'comma_separated_fields': [{'table_name': csf.table_name, 'field_name': csf.field_name} for csf in self.comma_separated_fields],
            'use_other_fields_as_metadata': self.use_other_fields_as_metadata,
            'num_rows': self.num_rows,
            'generate_canonical_entities': self.generate_canonical_entities,
            'generate_schemas': self.generate_schemas,
            'generate_embeddings': self.generate_embeddings,
            'generate_semantic_texts': self.generate_semantic_texts,
            'save_processed_data': self.save_processed_data,
            'database_type': self.database_type,
            'normalize_field_names': self.normalize_field_names,
            'upload_artifacts_to_gcs': self.upload_artifacts_to_gcs,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ArtifactGenerationRequest':
        """Create a request from a dictionary."""
        # Convert nested field objects
        entity_fields = [EntityField(**ef) for ef in data.get('entity_fields', [])]
        semantic_fields = [SemanticField(**sf) for sf in data.get('semantic_fields', [])]
        semantic_text_title_fields = [SemanticTextTitleField(**stf) for stf in data.get('semantic_text_title_fields', [])]
        comma_separated_fields = [CommaSeparatedField(**csf) for csf in data.get('comma_separated_fields', [])]
        
        return cls(
            input_path=data['input_path'],
            source_name=data.get('source_name', 'data'),
            table_name=data.get('table_name'),
            normalize_table_names=data.get('normalize_table_names', True),
            recursive=data.get('recursive', False),
            file_pattern=data.get('file_pattern', '*.csv'),  # Can be string or list
            table_name_from_file=data.get('table_name_from_file', True),
            entity_fields=entity_fields,
            semantic_fields=semantic_fields,
            semantic_text_title_fields=semantic_text_title_fields,
            comma_separated_fields=comma_separated_fields,
            use_other_fields_as_metadata=data.get('use_other_fields_as_metadata', True),
            num_rows=data.get('num_rows'),
            generate_canonical_entities=data.get('generate_canonical_entities', True),
            generate_schemas=data.get('generate_schemas', True),
            generate_embeddings=data.get('generate_embeddings', True),
            generate_semantic_texts=data.get('generate_semantic_texts', True),
            save_processed_data=data.get('save_processed_data', True),
            database_type=data.get('database_type', 'postgres'),
            normalize_field_names=data.get('normalize_field_names', True),
            upload_artifacts_to_gcs=data.get('upload_artifacts_to_gcs', False),
        )

    @classmethod
    def from_legacy_params(cls, **kwargs) -> 'ArtifactGenerationRequest':
        """
        Create a request from legacy parameters, automatically migrating to new config structure.
        
        This method helps migrate from the old flat parameter structure to the new nested configs.
        It will automatically map legacy parameters to their new locations and show deprecation warnings.
        
        Example:
            # Old way
            request = ArtifactGenerationRequest(
                input_path="/path/to/data",
                table_name="my_table",
                recursive=True,
                generate_canonical_entities=True
            )
            
            # New way (recommended)
            request = ArtifactGenerationRequest(
                input_path="/path/to/data",
                input_config=InputConfig(
                    table_name="my_table",
                    recursive=True
                ),
                artifact_generation_config=ArtifactGenerationConfig(
                    generate_canonical_entities=True
                )
            )
            
            # Migration helper
            request = ArtifactGenerationRequest.from_legacy_params(
                input_path="/path/to/data",
                table_name="my_table",
                recursive=True,
                generate_canonical_entities=True
            )
        """
        # Extract input_path (required)
        input_path = kwargs.pop('input_path', None)
        if input_path is None:
            raise ValueError("input_path is required")
        
        # Map legacy parameters to new configs
        input_config_kwargs = {}
        processing_config_kwargs = {}
        field_mapping_config_kwargs = {}
        artifact_generation_config_kwargs = {}
        
        # Input config mappings
        input_mappings = {
            'table_name': 'table_name',
            'recursive': 'recursive',
            'file_pattern': 'file_pattern',
            'table_name_from_file': 'table_name_from_file',
            'num_rows': 'num_rows'
        }
        
        # Processing config mappings
        processing_mappings = {
            'normalize_table_names': 'normalize_table_names',
            'normalize_field_names': 'normalize_field_names',
            'use_other_fields_as_metadata': 'use_other_fields_as_metadata'
        }
        
        # Field mapping config mappings
        field_mapping_mappings = {
            'entity_fields': 'entity_fields',
            'semantic_fields': 'semantic_fields',
            'semantic_text_title_fields': 'semantic_text_title_fields',
            'comma_separated_fields': 'comma_separated_fields'
        }
        
        # Artifact generation config mappings
        artifact_generation_mappings = {
            'generate_canonical_entities': 'generate_canonical_entities',
            'generate_schemas': 'generate_schemas',
            'generate_embeddings': 'generate_embeddings',
            'generate_semantic_texts': 'generate_semantic_texts',
            'save_processed_data': 'save_processed_data',
            'database_type': 'database_type',
            'upload_artifacts_to_gcs': 'upload_artifacts_to_gcs'
        }
        
        # Process mappings
        for old_param, new_param in input_mappings.items():
            if old_param in kwargs:
                input_config_kwargs[new_param] = kwargs.pop(old_param)
        
        for old_param, new_param in processing_mappings.items():
            if old_param in kwargs:
                processing_config_kwargs[new_param] = kwargs.pop(old_param)
        
        for old_param, new_param in field_mapping_mappings.items():
            if old_param in kwargs:
                field_mapping_config_kwargs[new_param] = kwargs.pop(old_param)
        
        for old_param, new_param in artifact_generation_mappings.items():
            if old_param in kwargs:
                artifact_generation_config_kwargs[new_param] = kwargs.pop(old_param)
        
        # Create configs
        input_config = InputConfig(**input_config_kwargs) if input_config_kwargs else InputConfig()
        processing_config = ProcessingConfig(**processing_config_kwargs) if processing_config_kwargs else ProcessingConfig()
        field_mapping_config = FieldMappingConfig(**field_mapping_config_kwargs) if field_mapping_config_kwargs else FieldMappingConfig()
        artifact_generation_config = ArtifactGenerationConfig(**artifact_generation_config_kwargs) if artifact_generation_config_kwargs else ArtifactGenerationConfig()
        
        # Warn about any remaining legacy parameters
        if kwargs:
            warnings.warn(
                f"Unknown parameters detected: {', '.join(kwargs.keys())}. "
                "These will be ignored.",
                UserWarning,
                stacklevel=2
            )
        
        # Create the request with new structure
        return cls(
            input_path=input_path,
            input_config=input_config,
            processing_config=processing_config,
            field_mapping_config=field_mapping_config,
            artifact_generation_config=artifact_generation_config,
            **kwargs  # Any remaining parameters (like source_name)
        )

    # Property methods for config-based access (config trumps legacy)
    @property
    def source_name(self) -> str:
        """Get source_name from input_config, fallback to legacy parameter."""
        config_value = self.input_config.source_name
        model_data = self.model_dump()
        legacy_value = model_data.get('source_name', "data")
        return config_value if config_value != "data" else legacy_value
    
    @property
    def table_name(self) -> Optional[str]:
        """Get table_name from input_config, fallback to legacy parameter."""
        config_value = self.input_config.table_name
        model_data = self.model_dump()
        legacy_value = model_data.get('table_name', None)
        return config_value if config_value is not None else legacy_value
    
    @property
    def recursive(self) -> bool:
        """Get recursive from input_config, fallback to legacy parameter."""
        config_value = self.input_config.recursive
        model_data = self.model_dump()
        legacy_value = model_data.get('recursive', False)
        return config_value if config_value != False else legacy_value
    
    @property
    def file_pattern(self) -> Union[str, List[str]]:
        """Get file_pattern from input_config, fallback to legacy parameter."""
        config_value = self.input_config.file_pattern
        model_data = self.model_dump()
        legacy_value = model_data.get('file_pattern', ["*.csv", "*.json"])
        return config_value if config_value != ["*.csv", "*.json"] else legacy_value
    
    @property
    def table_name_from_file(self) -> bool:
        """Get table_name_from_file from input_config, fallback to legacy parameter."""
        config_value = self.input_config.table_name_from_file
        model_data = self.model_dump()
        legacy_value = model_data.get('table_name_from_file', True)
        return config_value if config_value != True else legacy_value
    
    @property
    def num_rows(self) -> Optional[int]:
        """Get num_rows from input_config, fallback to legacy parameter."""
        config_value = self.input_config.num_rows
        model_data = self.model_dump()
        legacy_value = model_data.get('num_rows', None)
        return config_value if config_value is not None else legacy_value
    
    @property
    def normalize_table_names(self) -> bool:
        """Get normalize_table_names from processing_config, fallback to legacy parameter."""
        config_value = self.processing_config.normalize_table_names
        model_data = self.model_dump()
        legacy_value = model_data.get('normalize_table_names', True)
        return config_value if config_value != True else legacy_value
    
    @property
    def normalize_field_names(self) -> bool:
        """Get normalize_field_names from processing_config, fallback to legacy parameter."""
        config_value = self.processing_config.normalize_field_names
        model_data = self.model_dump()
        legacy_value = model_data.get('normalize_field_names', True)
        return config_value if config_value != True else legacy_value
    
    @property
    def use_other_fields_as_metadata(self) -> bool:
        """Get use_other_fields_as_metadata from processing_config, fallback to legacy parameter."""
        config_value = self.processing_config.use_other_fields_as_metadata
        model_data = self.model_dump()
        legacy_value = model_data.get('use_other_fields_as_metadata', True)
        return config_value if config_value != True else legacy_value
    
    @property
    def entity_fields(self) -> List[EntityField]:
        """Get entity_fields from field_mapping_config, fallback to legacy parameter."""
        config_value = self.field_mapping_config.entity_fields
        model_data = self.model_dump()
        legacy_value = model_data.get('entity_fields', [])
        return config_value if config_value else legacy_value
    
    @property
    def semantic_fields(self) -> List[SemanticField]:
        """Get semantic_fields from field_mapping_config, fallback to legacy parameter."""
        config_value = self.field_mapping_config.semantic_fields
        model_data = self.model_dump()
        legacy_value = model_data.get('semantic_fields', [])
        return config_value if config_value else legacy_value
    
    @property
    def semantic_text_title_fields(self) -> List[SemanticTextTitleField]:
        """Get semantic_text_title_fields from field_mapping_config, fallback to legacy parameter."""
        config_value = self.field_mapping_config.semantic_text_title_fields
        model_data = self.model_dump()
        legacy_value = model_data.get('semantic_text_title_fields', [])
        return config_value if config_value else legacy_value
    
    @property
    def comma_separated_fields(self) -> List[CommaSeparatedField]:
        """Get comma_separated_fields from field_mapping_config, fallback to legacy parameter."""
        config_value = self.field_mapping_config.comma_separated_fields
        model_data = self.model_dump()
        legacy_value = model_data.get('comma_separated_fields', [])
        return config_value if config_value else legacy_value
    
    @property
    def generate_canonical_entities(self) -> bool:
        """Get generate_canonical_entities from artifact_generation_config, fallback to legacy parameter."""
        config_value = self.artifact_generation_config.generate_canonical_entities
        model_data = self.model_dump()
        legacy_value = model_data.get('generate_canonical_entities', True)
        return config_value if config_value != True else legacy_value
    
    @property
    def generate_schemas(self) -> bool:
        """Get generate_schemas from artifact_generation_config, fallback to legacy parameter."""
        config_value = self.artifact_generation_config.generate_schemas
        model_data = self.model_dump()
        legacy_value = model_data.get('generate_schemas', True)
        return config_value if config_value != True else legacy_value
    
    @property
    def generate_embeddings(self) -> bool:
        """Get generate_embeddings from artifact_generation_config, fallback to legacy parameter."""
        config_value = self.artifact_generation_config.generate_embeddings
        model_data = self.model_dump()
        legacy_value = model_data.get('generate_embeddings', True)
        return config_value if config_value != True else legacy_value
    
    @property
    def generate_semantic_texts(self) -> bool:
        """Get generate_semantic_texts from artifact_generation_config, fallback to legacy parameter."""
        config_value = self.artifact_generation_config.generate_semantic_texts
        model_data = self.model_dump()
        legacy_value = model_data.get('generate_semantic_texts', True)
        return config_value if config_value != True else legacy_value
    
    @property
    def save_processed_data(self) -> bool:
        """Get save_processed_data from artifact_generation_config, fallback to legacy parameter."""
        config_value = self.artifact_generation_config.save_processed_data
        model_data = self.model_dump()
        legacy_value = model_data.get('save_processed_data', True)
        return config_value if config_value != True else legacy_value
    
    @property
    def database_type(self) -> str:
        """Get database_type from artifact_generation_config, fallback to legacy parameter."""
        config_value = self.artifact_generation_config.database_type
        model_data = self.model_dump()
        legacy_value = model_data.get('database_type', "postgres")
        return config_value if config_value != "postgres" else legacy_value
    
    @property
    def upload_artifacts_to_gcs(self) -> bool:
        """Get upload_artifacts_to_gcs from artifact_generation_config, fallback to legacy parameter."""
        config_value = self.artifact_generation_config.upload_artifacts_to_gcs
        model_data = self.model_dump()
        legacy_value = model_data.get('upload_artifacts_to_gcs', False)
        return config_value if config_value != False else legacy_value