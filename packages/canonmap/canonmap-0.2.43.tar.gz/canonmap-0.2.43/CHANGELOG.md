# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] - 2024-12-19

### Added
- **Enhanced Configuration System**: New configuration classes for better organization and flexibility
  - `CanonMapGCPConfig`: Base GCP configuration with service account and troubleshooting
  - `CanonMapCustomGCSConfig`: Bucket-specific configuration with sync strategies
  - `CanonMapArtifactsConfig`: Configuration for artifact storage and management
  - `CanonMapEmbeddingConfig`: Configuration for embedding model management
- **Comprehensive Response Models**: Enhanced response objects with detailed metadata
  - `ArtifactGenerationResponse`: Detailed artifact generation results with statistics
  - `EntityMappingResponse`: Comprehensive entity mapping results with performance metrics
  - Processing statistics, error handling, and warning information
  - GCP upload details and convenience paths
- **API Mode Support**: New `api_mode` parameter for API-specific optimizations
- **Advanced GCP Integration**: 
  - Flexible sync strategies ("none", "missing", "overwrite", "refresh")
  - Automatic bucket and prefix creation
  - Separate configurations for artifacts and embeddings
- **Enhanced Error Handling**: Detailed error and warning information in responses

### Changed
- **Breaking Changes**:
  - `CanonMap()` constructor now requires explicit configuration objects
  - `generate()` method renamed to `generate_artifacts()`
  - Removed `output_path` parameter from `ArtifactGenerationRequest`
  - Removed `artifacts_path` parameter from `CanonMap` constructor
- **Method Signatures**:
  - `CanonMap.__init__()` now requires `artifacts_config` and `embedding_config`
  - `generate_artifacts()` returns `ArtifactGenerationResponse` instead of dict
  - `map_entities()` returns `EntityMappingResponse` with enhanced metadata

### Improved
- **Documentation**: Updated README with new configuration examples and response model documentation
- **Logging**: Enhanced logging with configurable verbosity and troubleshooting modes
- **Performance**: Better error handling and resource management
- **Flexibility**: More granular control over GCP integration and sync strategies

### Migration Guide
To upgrade from version 0.1.x to 0.2.0:

1. **Update CanonMap initialization**:
   ```python
   # Old way
   canonmap = CanonMap()
   
   # New way
   artifacts_config = CanonMapArtifactsConfig(...)
   embedding_config = CanonMapEmbeddingConfig(...)
   canonmap = CanonMap(artifacts_config, embedding_config)
   ```

2. **Update method calls**:
   ```python
   # Old way
   results = canonmap.generate(request)
   
   # New way
   response = canonmap.generate_artifacts(request)
   ```

3. **Update response handling**:
   ```python
   # Old way
   print(f"Generated {len(results['artifacts'])} artifacts")
   
   # New way
   print(f"Generated {len(response.generated_artifacts)} artifacts")
   print(f"Status: {response.status}")
   print(f"Processing time: {response.processing_stats.processing_time_seconds:.2f}s")
   ```

## [0.1.200] - Previous versions

- Initial release with basic artifact generation and entity mapping
- Support for multiple database types
- GCP integration
- Embedding generation capabilities 