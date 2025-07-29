"""Configuration management for Person From Vid.

This module defines configuration classes and default settings for the video processing
pipeline, with support for environment variable overrides and validation.
"""

import re
from enum import Enum
from pathlib import Path
from typing import List, Optional

import yaml
from platformdirs import user_cache_dir
from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator, model_validator

# Configuration constants
DEFAULT_CONFIDENCE_THRESHOLD = 0.3
DEFAULT_BATCH_SIZE = 1
DEFAULT_JPEG_QUALITY = 95


class ModelType(str, Enum):
    """Supported AI model types."""

    FACE_DETECTION = "face_detection"
    POSE_ESTIMATION = "pose_estimation"
    HEAD_POSE_ESTIMATION = "head_pose_estimation"


class LogLevel(str, Enum):
    """Logging levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class DeviceType(str, Enum):
    """Supported computation devices."""

    CPU = "cpu"
    GPU = "gpu"
    AUTO = "auto"


class ModelConfig(BaseModel):
    """Configuration for AI models."""

    face_detection_model: str = Field(
        default="yolov8s-face", description="Face detection model name"
    )
    pose_estimation_model: str = Field(
        default="yolov8s-pose", description="Pose estimation model name"
    )
    head_pose_model: str = Field(
        default="sixdrepnet", description="Head pose estimation model name"
    )
    device: DeviceType = Field(
        default=DeviceType.AUTO, description="Computation device preference"
    )
    batch_size: int = Field(
        default=DEFAULT_BATCH_SIZE,
        ge=1,
        le=64,
        description="Batch size for model inference",
    )
    confidence_threshold: float = Field(
        default=DEFAULT_CONFIDENCE_THRESHOLD,
        ge=0.0,
        le=1.0,
        description="Minimum confidence threshold for detections",
    )
    
    # Face completeness validation settings
    require_complete_faces: bool = Field(
        default=True,
        description="Reject face detections that appear cut off at frame edges (particularly missing chins)"
    )
    face_edge_threshold: int = Field(
        default=10,
        ge=0,
        le=50,
        description="Minimum pixels from frame edge for complete face detection"
    )
    chin_margin_pixels: int = Field(
        default=15,
        ge=5,
        le=50,
        description="Required margin below estimated chin position for complete face validation"
    )

    @field_serializer("device")
    def serialize_device(self, value) -> str:
        """Serialize DeviceType enum to string for JSON."""
        if isinstance(value, DeviceType):
            return value.value
        return str(value)


class FrameExtractionConfig(BaseModel):
    """Configuration for frame extraction."""

    temporal_sampling_interval: float = Field(
        default=0.25,
        ge=0.1,
        le=2.0,
        description="Interval in seconds for temporal frame sampling",
    )
    enable_keyframe_detection: bool = Field(
        default=True, description="Enable I-frame keyframe detection"
    )
    enable_temporal_sampling: bool = Field(
        default=True, description="Enable temporal frame sampling"
    )
    max_frames_per_video: Optional[int] = Field(
        default=None,
        ge=1,
        description="Maximum frames to extract per video (None for unlimited)",
    )


class QualityConfig(BaseModel):
    """Configuration for image quality assessment."""

    blur_threshold: float = Field(
        default=100.0,
        ge=10.0,
        description="Minimum blur threshold (Laplacian variance)",
    )
    brightness_min: float = Field(
        default=30.0, ge=0.0, le=255.0, description="Minimum acceptable brightness"
    )
    brightness_max: float = Field(
        default=225.0, ge=0.0, le=255.0, description="Maximum acceptable brightness"
    )
    contrast_min: float = Field(
        default=20.0, ge=0.0, description="Minimum acceptable contrast"
    )
    enable_multiple_metrics: bool = Field(
        default=True, description="Use multiple quality metrics"
    )


class PoseClassificationConfig(BaseModel):
    """Configuration for pose classification."""

    standing_hip_knee_angle_min: float = Field(
        default=160.0,
        ge=120.0,
        le=180.0,
        description="Minimum hip-knee angle for standing classification",
    )
    sitting_hip_knee_angle_min: float = Field(
        default=80.0,
        ge=45.0,
        le=120.0,
        description="Minimum hip-knee angle for sitting classification",
    )
    sitting_hip_knee_angle_max: float = Field(
        default=120.0,
        ge=80.0,
        le=160.0,
        description="Maximum hip-knee angle for sitting classification",
    )
    squatting_hip_knee_angle_max: float = Field(
        default=90.0,
        ge=45.0,
        le=120.0,
        description="Maximum hip-knee angle for squatting classification",
    )
    closeup_face_area_threshold: float = Field(
        default=0.15,
        ge=0.05,
        le=0.5,
        description="Minimum face area ratio for closeup detection",
    )


class HeadAngleConfig(BaseModel):
    """Configuration for head angle classification."""

    yaw_threshold_degrees: float = Field(
        default=22.5,
        ge=10.0,
        le=45.0,
        description="Yaw angle threshold for direction classification",
    )
    pitch_threshold_degrees: float = Field(
        default=22.5,
        ge=10.0,
        le=45.0,
        description="Pitch angle threshold for direction classification",
    )
    max_roll_degrees: float = Field(
        default=30.0, ge=15.0, le=60.0, description="Maximum acceptable roll angle"
    )
    profile_yaw_threshold: float = Field(
        default=67.5,
        ge=45.0,
        le=90.0,
        description="Yaw threshold for profile classification",
    )


class CloseupDetectionConfig(BaseModel):
    """Configuration for closeup detection."""

    extreme_closeup_threshold: float = Field(
        default=0.25,
        ge=0.15,
        le=0.5,
        description="Face area ratio threshold for extreme closeup classification",
    )
    closeup_threshold: float = Field(
        default=0.15,
        ge=0.08,
        le=0.3,
        description="Face area ratio threshold for closeup classification",
    )
    medium_closeup_threshold: float = Field(
        default=0.08,
        ge=0.04,
        le=0.15,
        description="Face area ratio threshold for medium closeup classification",
    )
    medium_shot_threshold: float = Field(
        default=0.03,
        ge=0.01,
        le=0.08,
        description="Face area ratio threshold for medium shot classification",
    )
    shoulder_width_threshold: float = Field(
        default=0.35,
        ge=0.2,
        le=0.6,
        description="Shoulder width ratio threshold for closeup detection",
    )
    enable_distance_estimation: bool = Field(
        default=True,
        description="Enable distance estimation using inter-ocular distance",
    )


class FrameSelectionConfig(BaseModel):
    """Configuration for frame selection."""

    min_quality_threshold: float = Field(
        default=0.2,
        ge=0.0,
        le=1.0,
        description="Minimum quality threshold for frame selection",
    )
    face_size_weight: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Weight for face size in selection scoring (0-1)",
    )
    quality_weight: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Weight for quality metrics in selection scoring (0-1)",
    )
    diversity_threshold: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Minimum diversity score to avoid selecting similar frames",
    )
    temporal_diversity_threshold: float = Field(
        default=3.0,
        ge=0.0,
        le=30.0,
        description="Minimum seconds between selected frames to ensure temporal diversity",
    )

    @field_validator("face_size_weight", "quality_weight")
    @classmethod
    def validate_weights_sum(cls, v, info):
        """Ensure face_size_weight and quality_weight don't exceed 1.0 when combined."""
        if info.field_name == "quality_weight":
            # Get face_size_weight from values if it exists
            face_size_weight = info.data.get("face_size_weight", 0.3)
            if v + face_size_weight > 1.0:
                raise ValueError(
                    f"face_size_weight ({face_size_weight}) + quality_weight ({v}) must not exceed 1.0"
                )
        return v


class PersonSelectionCriteria(BaseModel):
    """Configuration for person-based selection."""

    # Enable person-based selection (defaults to True for enhanced multi-person support)
    enabled: bool = Field(
        default=True,
        description="Enable person-based selection instead of frame-based selection",
    )

    # Core per-person parameters (scale naturally with detected person count)
    min_instances_per_person: int = Field(
        default=3,
        ge=1,
        le=20,
        description="Minimum instances to select per person_id",
    )
    max_instances_per_person: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum instances to select per person_id",
    )
    min_quality_threshold: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Minimum person.quality.overall_quality for selection",
    )

    # Category-based selection within person groups
    enable_pose_categories: bool = Field(
        default=True,
        description="Enable pose category diversity within person groups",
    )
    enable_head_angle_categories: bool = Field(
        default=True,
        description="Enable head angle category diversity within person groups",
    )
    min_poses_per_person: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Minimum different poses per person (if available)",
    )
    min_head_angles_per_person: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Minimum different head angles per person (if available)",
    )

    # Temporal diversity (now applied to ALL selections for better diversity)
    temporal_diversity_threshold: float = Field(
        default=2.0,
        ge=0.0,
        le=30.0,
        description="Minimum seconds between selected instances of same person_id (applied to ALL selections for temporal diversity)",
    )

    # Global resource limit (no global minimum - scales naturally with person count)
    max_total_selections: int = Field(
        default=100,
        ge=10,
        le=1000,
        description="Overall limit on total selections across all persons",
    )

    @field_validator("max_instances_per_person")
    @classmethod
    def validate_max_greater_than_min(cls, v, info):
        """Ensure max_instances_per_person >= min_instances_per_person."""
        min_instances = info.data.get("min_instances_per_person", 3)
        if v < min_instances:
            raise ValueError(
                f"max_instances_per_person ({v}) must be >= min_instances_per_person ({min_instances})"
            )
        return v


class PngConfig(BaseModel):
    """Configuration for PNG output."""

    optimize: bool = Field(
        False, description="Enable PNG optimization for smaller file sizes."
    )


class JpegConfig(BaseModel):
    """Configuration for JPEG output."""

    quality: int = Field(
        95, ge=70, le=100, description="Quality for JPEG images (1-100)."
    )


class OutputImageConfig(BaseModel):
    """Configuration for output generation."""

    format: str = Field(
        "png",
        description="The output image format ('png' or 'jpeg'). 'jpg' is used as the extension for 'jpeg'.",
    )
    face_crop_enabled: bool = Field(
        default=True,
        description="Enable or disable the generation of cropped face images.",
    )
    face_crop_padding: float = Field(
        default=0.2,
        description="Padding around the face bounding box for crops (as a percentage).",
    )
    face_restoration_enabled: bool = Field(
        default=False,
        description="Enable GFPGAN face restoration for enhanced quality",
    )
    face_restoration_strength: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Face restoration strength (0.0=no effect, 1.0=full restoration)",
    )
    enable_pose_cropping: bool = Field(
        False, description="Enable generation of cropped pose images."
    )
    full_frames: bool = Field(
        False, description="Output full frames in addition to crops when pose cropping is enabled."
    )
    pose_crop_padding: float = Field(
        0.1, ge=0.0, le=1.0, description="Padding around pose bounding box."
    )
    resize: Optional[int] = Field(
        default=None,
        ge=256,
        le=4096,
        description="Maximum dimension for proportional image resizing (None for no resizing)",
    )
    crop_ratio: Optional[str] = Field(
        default=None,
        description="Fixed aspect ratio for crops (e.g., '1:1', '16:9', '4:3')",
    )
    default_crop_size: int = Field(
        default=640,
        ge=256,
        le=4096,
        description="Default crop size in pixels when crop_ratio is specified",
    )

    png: PngConfig = Field(default_factory=PngConfig)
    jpeg: JpegConfig = Field(default_factory=JpegConfig)

    @field_validator('crop_ratio', mode='before')
    @classmethod
    def validate_crop_ratio_format(cls, v):
        """Validate crop ratio format and range."""
        if v is None:
            return v
        
        if not isinstance(v, str):
            raise ValueError("crop_ratio must be a string in format 'W:H' (e.g., '16:9', '4:3', '1:1') or 'any'")
        
        # Handle "any" case (case-insensitive)
        if v.lower() == "any":
            return "any"  # Normalize to lowercase
        
        # Use regex to match exact W:H format with positive integers
        pattern = r'^(\d+):(\d+)$'
        match = re.match(pattern, v)
        
        if not match:
            raise ValueError(
                f"Invalid crop_ratio format '{v}'. Must be in format 'W:H' where W and H are positive integers "
                "(e.g., '16:9', '4:3', '1:1') or 'any'. Invalid formats like '16:', ':9', '16/9', or '1.5:1' are not allowed."
            )
        
        # Extract width and height as integers
        width, height = int(match.group(1)), int(match.group(2))
        
        # Validate that both width and height are positive
        if width <= 0 or height <= 0:
            raise ValueError(f"Invalid crop_ratio '{v}': both width and height must be positive integers")
        
        # Calculate ratio and validate range (0.1 to 100.0)
        ratio = width / height
        if not (0.1 <= ratio <= 100.0):
            raise ValueError(
                f"Invalid crop_ratio '{v}': calculated ratio {ratio:.2f} is outside valid range (0.1-100.0). "
                "Use ratios like '1:10' (0.1) to '100:1' (100.0)."
            )
        
        return v

    @model_validator(mode='after')
    @classmethod
    def validate_crop_ratio_dependency(cls, values):
        """Ensure crop_ratio is only specified when enable_pose_cropping is True."""
        if hasattr(values, 'crop_ratio') and hasattr(values, 'enable_pose_cropping'):
            if values.crop_ratio is not None and not values.enable_pose_cropping:
                raise ValueError("crop_ratio can only be specified when enable_pose_cropping is True")
        return values


class OutputConfig(BaseModel):
    """Configuration for output generation."""

    min_frames_per_category: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Minimum frames to output per pose/angle category",
    )

    max_frames_per_category: int = Field(
        default=5,
        ge=1,
        le=100,
        description="Maximum frames to output per pose/angle category",
    )

    preserve_metadata: bool = Field(
        default=True, description="Preserve metadata in output images"
    )
    # Image output configuration
    image: OutputImageConfig = Field(default_factory=OutputImageConfig)


class StorageConfig(BaseModel):
    """Configuration for storage and caching."""

    cache_directory: Path = Field(
        default_factory=lambda: Path(user_cache_dir("personfromvid", "codeprimate")),
        description="Directory for model and data caching",
    )
    temp_directory: Optional[Path] = Field(
        default=None, description="Temporary directory (None for auto-generated)"
    )
    cleanup_temp_on_success: bool = Field(
        default=True, description="Clean up temporary files on successful completion"
    )
    cleanup_temp_on_failure: bool = Field(
        default=False, description="Clean up temporary files on failure"
    )
    keep_temp: bool = Field(
        default=False,
        description="Keep temporary files after processing (overrides cleanup settings)",
    )
    force_temp_cleanup: bool = Field(
        default=False,
        description="Force cleanup of existing temp directory before processing",
    )
    max_cache_size_gb: float = Field(
        default=5.0, ge=0.5, le=50.0, description="Maximum cache size in GB"
    )

    @field_validator("cache_directory", "temp_directory", mode="before")
    @classmethod
    def convert_path(cls, v):
        """Convert string paths to Path objects."""
        if v is None:
            return v
        return Path(v) if not isinstance(v, Path) else v

    @field_serializer("cache_directory", "temp_directory")
    def serialize_path(self, value: Optional[Path]) -> Optional[str]:
        """Serialize Path objects to strings for JSON."""
        return str(value) if value is not None else None


class ProcessingConfig(BaseModel):
    """Configuration for processing behavior."""

    force_restart: bool = Field(
        default=False,
        description="Force restart processing by deleting existing state (preserves extracted frames)",
    )
    save_intermediate_results: bool = Field(
        default=True, description="Save intermediate processing results"
    )
    max_processing_time_minutes: Optional[int] = Field(
        default=None,
        ge=1,
        description="Maximum processing time in minutes (None for unlimited)",
    )
    parallel_workers: int = Field(
        default=1, ge=1, le=16, description="Number of parallel workers for processing"
    )


class LoggingConfig(BaseModel):
    """Configuration for logging."""

    level: LogLevel = Field(default=LogLevel.INFO, description="Logging level")
    enable_file_logging: bool = Field(
        default=False, description="Enable logging to file"
    )
    log_file: Optional[Path] = Field(
        default=None, description="Log file path (None for auto-generated)"
    )
    enable_rich_console: bool = Field(
        default=True, description="Enable rich console formatting"
    )
    enable_structured_output: bool = Field(
        default=True,
        description="Enable structured output format with emojis and progress bars",
    )
    verbose: bool = Field(default=False, description="Enable verbose logging")

    @field_serializer("level")
    def serialize_level(self, value) -> str:
        """Serialize LogLevel enum to string for JSON."""
        if isinstance(value, LogLevel):
            return value.value
        return str(value)

    @field_validator("log_file", mode="before")
    @classmethod
    def convert_log_path(cls, v):
        """Convert string paths to Path objects."""
        if v is None:
            return v
        return Path(v) if not isinstance(v, Path) else v

    @field_serializer("log_file")
    def serialize_log_path(self, value: Optional[Path]) -> Optional[str]:
        """Serialize Path objects to strings for JSON."""
        return str(value) if value is not None else None


class Config(BaseModel):
    """Main configuration class combining all settings."""

    # Sub-configurations
    models: ModelConfig = Field(default_factory=ModelConfig)
    frame_extraction: FrameExtractionConfig = Field(
        default_factory=FrameExtractionConfig
    )
    quality: QualityConfig = Field(default_factory=QualityConfig)
    pose_classification: PoseClassificationConfig = Field(
        default_factory=PoseClassificationConfig
    )
    head_angle: HeadAngleConfig = Field(default_factory=HeadAngleConfig)
    closeup_detection: CloseupDetectionConfig = Field(
        default_factory=CloseupDetectionConfig
    )
    frame_selection: FrameSelectionConfig = Field(default_factory=FrameSelectionConfig)
    person_selection: PersonSelectionCriteria = Field(
        default_factory=PersonSelectionCriteria
    )
    output: OutputConfig = Field(default_factory=OutputConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    processing: ProcessingConfig = Field(default_factory=ProcessingConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)

    model_config = ConfigDict(
        env_prefix="PERSONFROMVID_",
        env_nested_delimiter="__",
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    @classmethod
    def from_file(cls, config_path: Path) -> "Config":
        """Load configuration from YAML or JSON file."""
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            if config_path.suffix.lower() in [".yaml", ".yml"]:
                data = yaml.safe_load(f)
            elif config_path.suffix.lower() == ".json":
                import json

                data = json.load(f)
            else:
                raise ValueError(
                    f"Unsupported config file format: {config_path.suffix}"
                )

        return cls(**data)

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration with environment variable overrides."""
        return cls()

    def to_file(self, config_path: Path) -> None:
        """Save configuration to YAML or JSON file."""
        config_path.parent.mkdir(parents=True, exist_ok=True)

        data = self.dict()

        with open(config_path, "w", encoding="utf-8") as f:
            if config_path.suffix.lower() in [".yaml", ".yml"]:
                yaml.safe_dump(data, f, default_flow_style=False)
            elif config_path.suffix.lower() == ".json":
                import json

                json.dump(data, f, indent=2, default=str)
            else:
                raise ValueError(
                    f"Unsupported config file format: {config_path.suffix}"
                )

    def create_directories(self) -> None:
        """Create necessary directories based on configuration."""
        self.storage.cache_directory.mkdir(parents=True, exist_ok=True)

        if self.storage.temp_directory:
            self.storage.temp_directory.mkdir(parents=True, exist_ok=True)

        if self.logging.log_file:
            self.logging.log_file.parent.mkdir(parents=True, exist_ok=True)

    def validate_system_requirements(self) -> List[str]:
        """Validate system requirements and return list of issues."""
        issues = []

        # Check available disk space
        import shutil

        try:
            cache_space = shutil.disk_usage(self.storage.cache_directory.parent)
            available_gb = cache_space.free / (1024**3)
            if available_gb < self.storage.max_cache_size_gb:
                issues.append(
                    f"Insufficient disk space. Available: {available_gb:.1f}GB, "
                    f"Required: {self.storage.max_cache_size_gb}GB"
                )
        except Exception as e:
            issues.append(f"Could not check disk space: {e}")

        # Check if required directories are writable
        try:
            self.storage.cache_directory.mkdir(parents=True, exist_ok=True)
            test_file = self.storage.cache_directory / ".write_test"
            test_file.touch()
            test_file.unlink()
        except Exception as e:
            issues.append(f"Cache directory not writable: {e}")

        return issues


def get_default_config() -> Config:
    """Get default configuration with environment variable overrides."""
    return Config.from_env()


def load_config(config_path: Optional[Path] = None) -> Config:
    """Load configuration from file or use defaults with env overrides."""
    if config_path and config_path.exists():
        return Config.from_file(config_path)
    return get_default_config()
