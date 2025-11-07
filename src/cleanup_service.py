"""
Cleanup service for managing signal TTL and backups.
Automatically removes expired signals and creates backups.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from loguru import logger

from src.config import settings
from src.models import AnalysisResult, BackupData, BackupMetadata


class CleanupService:
    """Manages signal expiry and backup operations."""

    def __init__(self):
        """Initialize cleanup service."""
        self.active_file = settings.active_dir / "current_signals.json"
        self.backup_dir = settings.backup_dir

    def save_active_signals(self, result: AnalysisResult) -> None:
        """
        Save analysis result to active signals file.

        Args:
            result: AnalysisResult to save
        """
        try:
            # Convert to dict for JSON serialization
            data = result.model_dump(mode='json')

            # Save to active file
            self.active_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.active_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)

            logger.info(f"Saved active signals to {self.active_file}")

        except Exception as e:
            logger.error(f"Error saving active signals: {e}")

    def load_active_signals(self) -> Optional[AnalysisResult]:
        """
        Load active signals from file.

        Returns:
            AnalysisResult if available, None otherwise
        """
        try:
            if not self.active_file.exists():
                logger.info("No active signals file found")
                return None

            with open(self.active_file, 'r') as f:
                data = json.load(f)

            result = AnalysisResult(**data)
            logger.info(f"Loaded active signals from {self.active_file}")
            return result

        except Exception as e:
            logger.error(f"Error loading active signals: {e}")
            return None

    def is_expired(self, result: AnalysisResult) -> bool:
        """
        Check if analysis result has expired.

        Args:
            result: AnalysisResult to check

        Returns:
            True if expired, False otherwise
        """
        now = datetime.utcnow()
        expires_at = result.analysis_metadata.expires_at

        # Handle timezone-aware datetime
        if expires_at.tzinfo is not None:
            expires_at = expires_at.replace(tzinfo=None)

        return now >= expires_at

    def get_time_remaining(self, result: AnalysisResult) -> int:
        """
        Get time remaining in minutes before expiry.

        Args:
            result: AnalysisResult to check

        Returns:
            Minutes remaining (negative if expired)
        """
        now = datetime.utcnow()
        expires_at = result.analysis_metadata.expires_at

        # Handle timezone-aware datetime
        if expires_at.tzinfo is not None:
            expires_at = expires_at.replace(tzinfo=None)

        delta = expires_at - now
        return int(delta.total_seconds() / 60)

    def backup_signals(self, result: AnalysisResult) -> str:
        """
        Create backup of analysis result before removal.

        Args:
            result: AnalysisResult to backup

        Returns:
            Path to backup file
        """
        try:
            now = datetime.utcnow()

            # Create date-based directory
            date_dir = self.backup_dir / now.strftime('%Y-%m-%d')
            date_dir.mkdir(parents=True, exist_ok=True)

            # Create backup filename
            analysis_id = result.analysis_metadata.analysis_id
            backup_file = date_dir / f"analysis-{analysis_id}.json"

            # Create backup metadata
            backup_metadata = BackupMetadata(
                original_analysis_id=analysis_id,
                archived_at=now,
                original_timestamp=result.analysis_metadata.timestamp,
                reason="ttl_expired",
                ttl_minutes=result.analysis_metadata.ttl_minutes
            )

            # Create backup data
            backup_data = BackupData(
                backup_metadata=backup_metadata,
                original_data=result
            )

            # Save backup
            with open(backup_file, 'w') as f:
                json.dump(backup_data.model_dump(mode='json'), f, indent=2, default=str)

            logger.info(f"Created backup at {backup_file}")
            return str(backup_file)

        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return ""

    def remove_active_signals(self) -> None:
        """Remove active signals file."""
        try:
            if self.active_file.exists():
                self.active_file.unlink()
                logger.info(f"Removed active signals file: {self.active_file}")
            else:
                logger.info("No active signals file to remove")

        except Exception as e:
            logger.error(f"Error removing active signals: {e}")

    def cleanup_expired_signals(self) -> bool:
        """
        Check for expired signals, backup and remove them.

        Returns:
            True if cleanup was performed, False otherwise
        """
        try:
            # Load active signals
            result = self.load_active_signals()

            if result is None:
                logger.debug("No active signals to cleanup")
                return False

            # Check if expired
            if self.is_expired(result):
                logger.info(f"Signals expired, performing cleanup for analysis {result.analysis_metadata.analysis_id}")

                # Create backup
                backup_path = self.backup_signals(result)

                if backup_path:
                    # Remove active signals
                    self.remove_active_signals()
                    logger.info(f"Cleanup complete. Backed up to {backup_path}")
                    return True
                else:
                    logger.error("Backup failed, keeping active signals")
                    return False
            else:
                time_remaining = self.get_time_remaining(result)
                logger.debug(f"Signals not expired yet. {time_remaining} minutes remaining")
                return False

        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            return False

    def get_backup_files(self, date: Optional[str] = None) -> List[Path]:
        """
        Get list of backup files.

        Args:
            date: Optional date string in YYYY-MM-DD format

        Returns:
            List of backup file paths
        """
        try:
            if date:
                date_dir = self.backup_dir / date
                if date_dir.exists():
                    return sorted(date_dir.glob("analysis-*.json"))
                else:
                    return []
            else:
                # Get all backup files across all dates
                backup_files = []
                for date_dir in sorted(self.backup_dir.glob("*"), reverse=True):
                    if date_dir.is_dir():
                        backup_files.extend(sorted(date_dir.glob("analysis-*.json"), reverse=True))
                return backup_files

        except Exception as e:
            logger.error(f"Error getting backup files: {e}")
            return []

    def load_backup(self, backup_path: Path) -> Optional[BackupData]:
        """
        Load backup data from file.

        Args:
            backup_path: Path to backup file

        Returns:
            BackupData if successful, None otherwise
        """
        try:
            with open(backup_path, 'r') as f:
                data = json.load(f)

            backup = BackupData(**data)
            logger.info(f"Loaded backup from {backup_path}")
            return backup

        except Exception as e:
            logger.error(f"Error loading backup: {e}")
            return None

    def get_active_signals_with_ttl(self) -> Optional[dict]:
        """
        Get active signals with updated TTL information.

        Returns:
            Dict with active signals and TTL info, None if no active signals
        """
        try:
            result = self.load_active_signals()

            if result is None:
                return None

            # Check if expired
            if self.is_expired(result):
                logger.info("Active signals have expired")
                return None

            # Calculate time remaining
            time_remaining = self.get_time_remaining(result)

            # Convert to dict
            data = result.model_dump(mode='json')

            # Update time remaining in metadata
            data['analysis_metadata']['time_remaining_minutes'] = time_remaining

            # Update time remaining for each article
            for article in data['news_articles']:
                article['time_remaining_minutes'] = time_remaining

                # Update time remaining for each signal
                for signal in article['trading_signals']:
                    signal['time_remaining_minutes'] = time_remaining
                    signal['is_expired'] = False

            return data

        except Exception as e:
            logger.error(f"Error getting active signals with TTL: {e}")
            return None

    def cleanup_old_backups(self, days_to_keep: int = 30) -> int:
        """
        Remove backup files older than specified days.

        Args:
            days_to_keep: Number of days to keep backups

        Returns:
            Number of files deleted
        """
        try:
            now = datetime.utcnow()
            deleted_count = 0

            for date_dir in self.backup_dir.glob("*"):
                if date_dir.is_dir():
                    try:
                        # Parse date from directory name
                        dir_date = datetime.strptime(date_dir.name, '%Y-%m-%d')
                        days_old = (now - dir_date).days

                        if days_old > days_to_keep:
                            # Delete all files in this directory
                            for backup_file in date_dir.glob("*.json"):
                                backup_file.unlink()
                                deleted_count += 1

                            # Remove empty directory
                            if not any(date_dir.iterdir()):
                                date_dir.rmdir()
                                logger.info(f"Removed old backup directory: {date_dir}")

                    except ValueError:
                        # Skip directories that don't match date format
                        continue

            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old backup files")

            return deleted_count

        except Exception as e:
            logger.error(f"Error cleaning up old backups: {e}")
            return 0


# Global instance
cleanup_service = CleanupService()
