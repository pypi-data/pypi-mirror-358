from pathlib import Path
from typing import Optional, List, Dict, Union, Any
import pandas as pd
from pydantic import BaseModel, Field

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

class ArtifactGenerationRequest(BaseModel):
    """Configuration for generating canonicalization artifacts.
    
    Focuses on WHAT to generate rather than WHERE to store it.
    Storage configuration is handled by CanonMapArtifactsConfig.
    If 'upload_to_gcp' is True, generated artifacts will be uploaded to GCS according to the sync strategy in the config.
    """
    
    input_path: str  # Restrict to str for FastAPI compatibility
    source_name: str = "data"
    table_name: Optional[str] = None
    normalize_table_names: bool = True
    recursive: bool = False
    file_pattern: str = "*.csv"
    table_name_from_file: bool = True
    entity_fields: Optional[List[EntityField]] = Field(default_factory=list)
    semantic_fields: Optional[List[SemanticField]] = Field(default_factory=list)
    semantic_text_title_fields: Optional[List[SemanticTextTitleField]] = Field(default_factory=list)
    comma_separated_fields: Optional[List[CommaSeparatedField]] = Field(default_factory=list)
    use_other_fields_as_metadata: bool = False
    num_rows: Optional[int] = None
    generate_canonical_entities: bool = True
    generate_schema: bool = False
    generate_embeddings: bool = False
    generate_semantic_texts: bool = False
    save_processed_data: bool = False
    schema_database_type: str = "mariadb"
    clean_field_names: bool = True
    upload_to_gcp: bool = False

    class Config:
        arbitrary_types_allowed = True  # Allow pandas DataFrame and Path objects

    def to_dict(self) -> Dict[str, Any]:
        """Convert the request to a dictionary for serialization."""
        return {
            'input_path': str(self.input_path) if isinstance(self.input_path, Path) else self.input_path,
            'source_name': self.source_name,
            'table_name': self.table_name,
            'normalize_table_names': self.normalize_table_names,
            'recursive': self.recursive,
            'file_pattern': self.file_pattern,
            'table_name_from_file': self.table_name_from_file,
            'entity_fields': [{'table_name': ef.table_name, 'field_name': ef.field_name} for ef in self.entity_fields],
            'semantic_fields': [{'table_name': sf.table_name, 'field_name': sf.field_name} for sf in self.semantic_fields],
            'semantic_text_title_fields': [{'table_name': stf.table_name, 'field_name': stf.field_name} for stf in self.semantic_text_title_fields],
            'comma_separated_fields': [{'table_name': csf.table_name, 'field_name': csf.field_name} for csf in self.comma_separated_fields],
            'use_other_fields_as_metadata': self.use_other_fields_as_metadata,
            'num_rows': self.num_rows,
            'generate_canonical_entities': self.generate_canonical_entities,
            'generate_schema': self.generate_schema,
            'generate_embeddings': self.generate_embeddings,
            'generate_semantic_texts': self.generate_semantic_texts,
            'save_processed_data': self.save_processed_data,
            'schema_database_type': self.schema_database_type,
            'clean_field_names': self.clean_field_names,
            'upload_to_gcp': self.upload_to_gcp,
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
            file_pattern=data.get('file_pattern', '*.csv'),
            table_name_from_file=data.get('table_name_from_file', True),
            entity_fields=entity_fields,
            semantic_fields=semantic_fields,
            semantic_text_title_fields=semantic_text_title_fields,
            comma_separated_fields=comma_separated_fields,
            use_other_fields_as_metadata=data.get('use_other_fields_as_metadata', False),
            num_rows=data.get('num_rows'),
            generate_canonical_entities=data.get('generate_canonical_entities', True),
            generate_schema=data.get('generate_schema', False),
            generate_embeddings=data.get('generate_embeddings', False),
            generate_semantic_texts=data.get('generate_semantic_texts', False),
            save_processed_data=data.get('save_processed_data', False),
            schema_database_type=data.get('schema_database_type', 'mariadb'),
            clean_field_names=data.get('clean_field_names', True),
            upload_to_gcp=data.get('upload_to_gcp', False),
        )