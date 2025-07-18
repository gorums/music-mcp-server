#!/usr/bin/env python3
"""
Music Collection MCP Server - Migrate Band Structure Tool

This module contains the migrate_band_structure tool implementation for migrating 
band folder organization patterns between different structure types.
"""

from typing import Any, Dict, List, Optional

from ..mcp_instance import mcp
from ..base_handlers import BaseToolHandler

# Import migration functionality
from src.models.migration import (
    BandStructureMigrator,
    MigrationType,
    MigrationStatus,
    MigrationResult
)
from src.models.migration_analytics import migration_analytics

import logging
logger = logging.getLogger(__name__)

class MigrateBandStructureHandler(BaseToolHandler):
    """Handler for the migrate_band_structure tool."""
    
    def __init__(self):
        super().__init__("migrate_band_structure", "1.0.0")
    
    def _execute_tool(self, **kwargs) -> Dict[str, Any]:
        """Execute the migrate band structure tool logic."""
        # Extract and validate parameters
        band_name = kwargs.get('band_name', '').strip()
        migration_type = kwargs.get('migration_type', '').strip()
        dry_run = kwargs.get('dry_run', False)
        album_type_overrides = kwargs.get('album_type_overrides', {})
        backup_original = kwargs.get('backup_original', True)
        force = kwargs.get('force', False)
        exclude_albums = kwargs.get('exclude_albums', [])
        
        # Validate required parameters
        validation_error = self._validate_required_params(kwargs, ['band_name', 'migration_type'])
        if validation_error:
            return validation_error.to_dict()
        
        if not band_name:
            raise ValueError("Band name cannot be empty")
        
        # Validate migration type
        try:
            migration_type_enum = MigrationType(migration_type)
        except ValueError:
            valid_types = [t.value for t in MigrationType]
            raise ValueError(f"Invalid migration type '{migration_type}'. Valid types: {valid_types}")
        
        # Create migrator instance
        migrator = BandStructureMigrator()
        
        # Set up progress tracking
        progress_messages = []
        def progress_callback(message: str, percentage: float):
            progress_messages.append({
                'message': message,
                'percentage': percentage
            })
            logger.info(f"Migration progress: {percentage:.1f}% - {message}")
        
        migrator.set_progress_callback(progress_callback)
        
        # Execute migration
        try:
            result = migrator.migrate_band_structure(
                band_name=band_name,
                migration_type=migration_type_enum,
                dry_run=dry_run,
                album_type_overrides=album_type_overrides,
                backup_original=backup_original,
                force=force,
                exclude_albums=exclude_albums
            )
            
            from pathlib import Path
            from src.di import get_config
            config = get_config()
            band_folder_path = Path(config.MUSIC_ROOT_PATH) / band_name
            
            migration_report = migration_analytics.generate_migration_report(result, band_folder_path)
            
            # Build response with analytics
            response = {
                'status': 'success',
                'migration_result': {
                    'status': result.status.value,
                    'band_name': result.band_name,
                    'migration_type': result.migration_type.value,
                    'albums_migrated': result.albums_migrated,
                    'albums_failed': result.albums_failed,
                    'migration_time_seconds': result.migration_time_seconds,
                    'dry_run': result.dry_run,
                    'error_messages': result.error_messages
                },
                'operations': [
                    {
                        'album_name': op.album_name,
                        'source_path': op.source_path,
                        'target_path': op.target_path,
                        'album_type': op.album_type.value,
                        'operation_type': op.operation_type,
                        'completed': op.completed,
                        'error_message': op.error_message
                    }
                    for op in result.operations
                ],
                'progress_tracking': progress_messages,
                'backup_info': None,
                
                # Enhanced analytics and reporting
                'migration_analytics': {
                    'report_id': migration_report.report_id,
                    'structure_comparison': {
                        'before_structure': migration_report.structure_comparison.before_structure.value,
                        'after_structure': migration_report.structure_comparison.after_structure.value,
                        'albums_reorganized': migration_report.structure_comparison.albums_reorganized,
                        'new_type_folders_created': migration_report.structure_comparison.new_type_folders_created,
                        'compliance_improvement': migration_report.structure_comparison.compliance_improvement
                    },
                    'success_metrics': {
                        'total_operations': migration_report.success_metrics.total_operations,
                        'successful_operations': migration_report.success_metrics.successful_operations,
                        'failed_operations': migration_report.success_metrics.failed_operations,
                        'success_rate': migration_report.success_metrics.success_rate,
                        'error_breakdown': migration_report.success_metrics.error_breakdown
                    },
                    'type_distribution': [
                        {
                            'album_type': dist.album_type.value,
                            'before_count': dist.before_count,
                            'after_count': dist.after_count,
                            'change': dist.change
                        }
                        for dist in migration_report.type_distribution_analysis
                        if dist.before_count > 0 or dist.after_count > 0
                    ],
                    'organization_improvements': [
                        {
                            'metric_name': imp.metric_name,
                            'improvement_percentage': imp.improvement_percentage,
                            'description': imp.improvement_description
                        }
                        for imp in migration_report.organization_improvements
                    ],
                    'performance_metrics': [
                        {
                            'name': metric.name,
                            'value': metric.value,
                            'unit': metric.unit,
                            'description': metric.description
                        }
                        for metric in migration_report.performance_metrics
                    ],
                    'unmigrated_recommendations': [
                        {
                            'album_name': rec.album_name,
                            'current_path': rec.current_path,
                            'recommended_path': rec.recommended_path,
                            'recommended_type': rec.recommended_type.value,
                            'reason': rec.reason
                        }
                        for rec in migration_report.unmigrated_recommendations
                    ]
                },
                
                # Migration history summary
                'migration_history': {
                    'previous_migrations': len(migration_analytics.get_migration_history(band_name)),
                    'overall_statistics': migration_analytics.get_migration_statistics()
                },
                
                # Markdown report for easy reading
                'markdown_report': migration_analytics.generate_markdown_report(migration_report)
            }
            
            # Add backup information if available
            if result.backup_info:
                response['backup_info'] = {
                    'timestamp': result.backup_info.timestamp,
                    'backup_folder_path': result.backup_info.backup_folder_path,
                    'original_structure_type': result.backup_info.original_structure_type.value,
                    'metadata_backup_path': result.backup_info.metadata_backup_path
                }
            
            # Add tool-specific metadata
            response['tool_info'] = self._create_tool_info(
                migration_type=migration_type,
                dry_run=dry_run,
                albums_processed=len(result.operations),
                success_rate=f"{(result.albums_migrated / max(1, len(result.operations))) * 100:.1f}%"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Migration failed for band '{band_name}': {str(e)}")
            raise


# Create handler instance
_handler = MigrateBandStructureHandler()

@mcp.tool()
def migrate_band_structure(
    band_name: str,
    migration_type: str,
    dry_run: bool = False,
    album_type_overrides: Optional[Dict[str, str]] = None,
    backup_original: bool = True,
    force: bool = False,
    exclude_albums: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Migrate a band's folder structure between different organization patterns.
    
    This tool enables safe migration of band folder organization with comprehensive features:
    - Support for multiple migration types (default→enhanced, legacy→default, mixed→enhanced)
    - Dry-run mode for previewing changes without making actual modifications
    - Automatic backup creation with rollback functionality on failure
    - Progress tracking for large band migrations
    - Album type override capabilities for manual classification
    - Selective album exclusion from migration operations
    
    Migration Types:
    - default_to_enhanced: Migrate from flat structure to type-based folders (Album/, Live/, Demo/, etc.)
    - legacy_to_default: Add year prefixes to album folders (Album Name → YYYY - Album Name)
    - mixed_to_enhanced: Convert inconsistent patterns to unified enhanced structure
    - enhanced_to_default: Rollback from enhanced to flat structure
    
    Args:
        band_name: Name of the band to migrate (exact match from collection)
        migration_type: Type of migration to perform (see Migration Types above)
        dry_run: If True, preview migration operations without making actual changes
        album_type_overrides: Manual album type assignments (e.g., {"Album Name": "live"})
        backup_original: Whether to create backup before migration (recommended: True)
        force: Override safety checks and validation warnings
        exclude_albums: List of album names to skip during migration
    
    Returns:
        Dict containing migration results including:
        - status: 'success' or 'error'
        - migration_result: Detailed migration outcome with statistics
        - operations: List of all planned/executed operations per album
        - progress_tracking: Progress messages with completion percentages
        - backup_info: Backup location and rollback information
        - tool_info: Migration metadata and performance statistics
    
    Example Usage:
        # Dry run to preview migration from default to enhanced structure
        migrate_band_structure(
            band_name="Metallica",
            migration_type="default_to_enhanced",
            dry_run=True
        )
        
        # Actual migration with manual album type overrides
        migrate_band_structure(
            band_name="Iron Maiden",
            migration_type="default_to_enhanced",
            dry_run=False,
            album_type_overrides={
                "Live After Death": "live",
                "Best of the Beast": "compilation"
            },
            exclude_albums=["Work in Progress Demo"]
        )
    """
    return _handler.execute(
        band_name=band_name,
        migration_type=migration_type,
        dry_run=dry_run,
        album_type_overrides=album_type_overrides,
        backup_original=backup_original,
        force=force,
        exclude_albums=exclude_albums
    ) 