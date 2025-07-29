"""Command-line interface for Person From Vid.

This module provides the main CLI entry point with argument parsing,
configuration management, and progress display setup.
"""

import signal
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from .data.config import Config, LogLevel, load_config
from .utils.exceptions import PersonFromVidError, format_exception_message
from .utils.logging import get_logger, setup_logging
from .utils.validation import validate_system_requirements, validate_video_file

# Global console for rich output
console = Console()


def signal_handler(signum: int, frame) -> None:
    """Handle interrupt signals gracefully."""
    console.print("\n[yellow]Processing interrupted by user.[/yellow]")
    console.print("[green]Temporary files preserved for potential resume.[/green]")
    sys.exit(1)


def get_version():
    """Get the current version for CLI help."""
    from . import __version__

    return __version__


@click.command()
@click.version_option(version=get_version(), prog_name="Person From Vid")
@click.argument(
    "video_path", type=click.Path(exists=True, path_type=Path), required=False
)
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Path to configuration file (YAML or JSON)",
)
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(path_type=Path),
    help="Output directory (default: same as video file)",
)
@click.option(
    "--log-level",
    "-l",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
    default="INFO",
    help="Logging level",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--quiet", "-q", is_flag=True, help="Suppress non-essential output")
@click.option(
    "--device",
    type=click.Choice(["cpu", "gpu", "auto"], case_sensitive=False),
    default="auto",
    help="Computation device preference",
)
@click.option(
    "--batch-size", type=click.IntRange(1, 64), help="Batch size for AI model inference"
)
@click.option(
    "--confidence",
    type=click.FloatRange(0.0, 1.0),
    help="Confidence threshold for detections",
)
@click.option(
    "--max-frames", type=click.IntRange(1), help="Maximum frames to extract per video"
)
@click.option(
    "--quality-threshold",
    type=click.FloatRange(0.0),
    help="Quality threshold for frame selection",
)
@click.option(
    "--output-format",
    type=click.Choice(["png", "jpeg"], case_sensitive=False),
    help="Output image format",
)
@click.option(
    "--output-jpeg-quality",
    type=click.IntRange(70, 100),
    help="JPEG quality for output images",
)
@click.option(
    "--output-face-crop-enabled/--no-output-face-crop-enabled",
    default=None,
    help="Enable/disable generation of cropped face images",
)
@click.option(
    "--output-face-crop-padding",
    type=click.FloatRange(0.0, 1.0),
    help="Padding around face bounding box for crops",
)
@click.option(
    "--face-restoration/--no-face-restoration",
    "face_restoration_enabled",
    default=None,
            help="Enable/disable GFPGAN face restoration for enhanced quality",
)
@click.option(
    "--face-restoration-strength",
    type=click.FloatRange(0.0, 1.0),
    help="Face restoration strength: 0.0=no effect, 1.0=full restoration, 0.8=recommended balance",
)
@click.option(
    "--crop-padding",
    type=click.FloatRange(0.0, 1.0),
    help="Padding around pose bounding box for crops, in percentage of the crop size (default: 0.2)",
)
@click.option(
    "--crop-ratio",
    type=str,
    help="Aspect ratio for crops: fixed ratios (e.g., '1:1', '16:9', '4:3') or 'any' for variable aspect ratios. Automatically enables cropping.",
)
@click.option(
    "--full-frames",
    is_flag=True,
    help="Output full frames in addition to crops when cropping is enabled",
)
@click.option(
    "--output-png-optimize/--no-output-png-optimize",
    default=None,
    help="Enable/disable PNG optimization",
)
@click.option(
    "--resize",
    type=click.IntRange(256, 4096),
    help="Maximum dimension for proportional image resizing (256-4096 pixels)",
)
@click.option(
    "--min-frames-per-category",
    type=click.IntRange(1, 10),
    help="Minimum frames to output per pose/angle category",
)
@click.option(
    "--max-frames-per-category",
    type=click.IntRange(1, 100),
    help="Maximum frames to output per pose/angle category",
)
@click.option(
    "--keep-temp",
    is_flag=True,
    help="Keep temporary files after processing (overrides default cleanup)",
)
@click.option(
    "--force",
    is_flag=True,
    help="Force restart analysis by deleting existing state (preserves extracted frames)",
)
@click.option(
    "--no-structured-output",
    is_flag=True,
    help="Disable structured output format (use basic logging instead)",
)
def main(
    video_path: Optional[Path],
    config: Optional[Path],
    output_dir: Optional[Path],
    log_level: str,
    verbose: bool,
    quiet: bool,
    device: str,
    batch_size: Optional[int],
    confidence: Optional[float],
    max_frames: Optional[int],
    quality_threshold: Optional[float],
    output_format: Optional[str],
    output_jpeg_quality: Optional[int],
    output_face_crop_enabled: Optional[bool],
    output_face_crop_padding: Optional[float],
    face_restoration_enabled: Optional[bool],
    face_restoration_strength: Optional[float],
    crop_padding: Optional[float],
    crop_ratio: Optional[str],
    full_frames: bool,
    output_png_optimize: Optional[bool],
    resize: Optional[int],
    min_frames_per_category: Optional[int],
    max_frames_per_category: Optional[int],
    keep_temp: bool,
    force: bool,
    no_structured_output: bool,
) -> None:
    """Extract and categorize high-quality frames containing people from video files.

    Person From Vid analyzes video files to identify and extract frames showing people
    in specific poses (standing, sitting, squatting) and head orientations (front,
    profile, looking directions). The tool uses AI models for face detection, pose
    estimation, and head pose analysis to automatically categorize and select the
    best quality frames.

    VIDEO_PATH: Path to the input video file to process.

    Examples:

        # Basic usage
        personfromvid video.mp4

        # With custom output directory
        personfromvid video.mp4 --output-dir ./extracted_frames

        # High quality with verbose output
        personfromvid video.mp4 --jpeg-quality 98 --verbose

        # Use GPU acceleration with custom batch size
        personfromvid video.mp4 --device gpu --batch-size 16

        # Resize output images to max 1024px dimension
        personfromvid video.mp4 --resize 1024

        # Generate square crops with fixed 1:1 aspect ratio
        personfromvid video.mp4 --crop-ratio 1:1

        # Generate widescreen crops with 16:9 aspect ratio
        personfromvid video.mp4 --crop-ratio 16:9 --output-dir ./widescreen_crops

        # Generate portrait crops with custom padding
        personfromvid video.mp4 --crop-ratio 4:3 --crop-padding 0.3

        # Generate variable aspect ratio crops (preserve natural proportions)
        personfromvid video.mp4 --crop-ratio any --crop-padding 0.2

        # Combine fixed aspect ratio with face restoration and resizing
        personfromvid video.mp4 --crop-ratio 1:1 --face-restoration --resize 512

    """
    # Check for required video path
    if not video_path:
        console.print(
            "[red]Error:[/red] VIDEO_PATH is required when not using --version"
        )
        console.print("Try 'personfromvid --help' for help.")
        sys.exit(1)

    # Set up signal handling
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Initialize variables for error handling
    app_config = None
    processing_context = None

    try:
        # 1. Load configuration and apply overrides
        app_config = load_config(config)
        apply_cli_overrides(app_config, locals())

        # 2. Set up logging and formatting
        will_use_consolidated_formatter, logger = setup_logging_and_formatting(
            app_config, no_structured_output, quiet
        )

        # 3. Validate inputs
        video_validation = validate_inputs(
            video_path, app_config, quiet, no_structured_output
        )

        # 4. Set up output directory and create directories
        if output_dir is None:
            output_dir = video_path.parent
        app_config.create_directories()

        # 5. Show processing plan (unless using consolidated formatter)
        if not will_use_consolidated_formatter:
            show_processing_plan(video_path, output_dir, app_config)

        # 6. Run pipeline
        result, processing_context = create_and_run_pipeline(
            video_path,
            output_dir,
            app_config,
            video_validation,
            will_use_consolidated_formatter,
            logger,
            verbose,
        )

        # 7. Handle pipeline failure (success cleanup is handled by pipeline itself)
        if not result.success:
            handle_cleanup(processing_context, app_config, success=False)
            console.print(
                f"[red]Error:[/red] Processing failed: {result.error_message}"
            )
            sys.exit(1)

    except (PersonFromVidError, KeyboardInterrupt, Exception) as e:
        handle_cli_error(e, processing_context, app_config, verbose)
        sys.exit(1)


def create_and_run_pipeline(
    video_path: Path,
    output_dir: Path,
    config: Config,
    video_validation: dict,
    will_use_consolidated_formatter: bool,
    logger,
    verbose: bool,
):
    """Create processing context and run pipeline.

    Returns:
        tuple: (ProcessingResult, ProcessingContext) - Pipeline execution result and context
    """
    # Initialize and run pipeline
    from .core.pipeline import ProcessingPipeline
    from .data.context import ProcessingContext

    # Create processing context with required components
    if not will_use_consolidated_formatter:
        logger.info("Initializing processing context...")

    # Create ProcessingContext
    processing_context = ProcessingContext(
        video_path=video_path,
        video_base_name=video_path.stem,
        config=config,
        output_directory=output_dir,
    )

    # Create consolidated formatter if structured output is enabled
    consolidated_formatter = None
    if will_use_consolidated_formatter:
        from .utils.output_formatter import create_consolidated_formatter

        consolidated_formatter = create_consolidated_formatter(
            console=console, enable_debug=verbose or config.logging.verbose
        )

        # Start processing with consolidated output
        config_info = {
            "gpu_available": config.models.device == "gpu",
            "video_metadata": (
                video_validation["metadata"]
                if "error" not in video_validation["metadata"]
                else None
            ),
            "file_size_mb": video_path.stat().st_size / (1024 * 1024),
        }
        consolidated_formatter.start_processing(str(video_path), config_info)
    else:
        logger.info("Initializing processing pipeline...")

    try:
        pipeline = ProcessingPipeline(
            context=processing_context, formatter=consolidated_formatter
        )

        # Process with resume by default
        # Check if resumable state exists
        status = pipeline.get_status()
        if status.can_resume:
            logger.info("Resuming from previous processing state...")
            result = pipeline.resume()
        else:
            logger.info("No resumable state found, starting new processing...")
            result = pipeline.process()

        # Show results
        if result.success:
            # Pipeline's consolidated formatter already handled success output
            if not consolidated_formatter:
                logger.info("Processing completed successfully")
        else:
            error_msg = f"Processing failed: {result.error_message}"
            if consolidated_formatter:
                consolidated_formatter.print_error(error_msg)
            else:
                logger.error(f"❌ {error_msg}")
            # Don't call sys.exit here - let main function handle cleanup
            return result, processing_context

        return result, processing_context

    except Exception as e:
        logger.error(f"Pipeline processing failed: {e}")
        if verbose:
            console.print_exception()

        # Re-raise the exception to let CLI handle cleanup
        raise


def handle_cli_error(
    error: Exception,
    processing_context: Optional[object] = None,
    app_config: Optional[object] = None,
    verbose: bool = False,
) -> None:
    """Handle CLI-level errors with appropriate cleanup and messaging.

    Args:
        error: The exception that occurred
        processing_context: The processing context (if created)
        app_config: Application configuration (if loaded)
        verbose: Whether to show detailed error information
    """
    if isinstance(error, PersonFromVidError):
        error_msg = format_exception_message(error)
        console.print(f"[red]Error:[/red] {error_msg}")
    elif isinstance(error, KeyboardInterrupt):
        console.print("\n[yellow]Processing interrupted by user.[/yellow]")
        console.print("[green]Temporary files preserved for potential resume.[/green]")
    else:
        console.print(f"[red]Unexpected error:[/red] {str(error)}")
        if verbose:
            console.print_exception()

    # Cleanup if processing context was created
    if processing_context and app_config:
        handle_cleanup(processing_context, app_config, success=False, error=error)


def handle_cleanup(
    processing_context: Optional[object] = None,
    config: Optional[object] = None,
    success: bool = False,
    error: Optional[Exception] = None,
    interrupted: bool = False,
) -> None:
    """Handle cleanup operations for CLI-level failures only.

    Note: Pipeline handles its own success and internal failure cleanup.
    This function only handles cleanup for CLI-level errors that occur
    before or after pipeline execution.

    Args:
        processing_context: The processing context with temp manager (if available)
        config: Application configuration (if available)
        success: Whether processing completed successfully (unused - pipeline handles success)
        error: Exception that caused failure (if any)
        interrupted: Whether processing was interrupted by user (unused - interrupts preserve files)
    """
    # Only perform cleanup if we have both context and config
    if not processing_context or not config:
        return

    try:
        temp_manager = getattr(processing_context, "temp_manager", None)
        if not temp_manager:
            return

        # Only cleanup on CLI-level errors, and only if configured to do so
        if not success and not interrupted and config.storage.cleanup_temp_on_failure:
            temp_manager.cleanup_temp_files()

    except Exception:
        # Don't fail cleanup on error - just silently continue
        pass


def setup_logging_and_formatting(
    config: Config, no_structured_output: bool, quiet: bool
) -> tuple:
    """Set up logging and determine formatter.

    Returns:
        tuple: (will_use_consolidated_formatter, consolidated_formatter)
    """
    # Determine if we'll use consolidated formatter
    will_use_consolidated_formatter = (
        config.logging.enable_structured_output and not no_structured_output
    )

    # Completely disable structured logging if using consolidated formatter
    if will_use_consolidated_formatter:
        config.logging.enable_rich_console = False
        config.logging.enable_structured_output = False
        # Set logging to ERROR level to suppress all INFO/DEBUG messages
        config.logging.level = LogLevel.ERROR

    # Set up logging
    setup_logging(config.logging)
    logger = get_logger("cli")

    # Show banner unless quiet or using consolidated formatter
    if not quiet and not will_use_consolidated_formatter:
        show_banner()

    return will_use_consolidated_formatter, logger


def validate_inputs(
    video_path: Path, config: Config, quiet: bool, no_structured_output: bool = False
) -> dict:
    """Handle all system and video validation.

    Returns:
        dict: Video validation metadata

    Raises:
        SystemExit: If validation fails
    """
    logger = get_logger("cli")

    # Determine if we'll use consolidated formatter for conditional output
    # Note: This must match the logic from main function
    will_use_consolidated_formatter = (
        config.logging.enable_structured_output and not no_structured_output
    )

    # Validate system requirements (suppress detailed output if using consolidated formatter)
    if not will_use_consolidated_formatter:
        logger.info("Validating system requirements...")

    system_issues = validate_system_requirements()

    if system_issues:
        if will_use_consolidated_formatter:
            # Just check for fatal issues, don't log details
            fatal_issues = [
                issue
                for issue in system_issues
                if "Missing required dependency" in issue
            ]
            if fatal_issues:
                console.print("[red]Error:[/red] Missing required dependencies")
                for issue in fatal_issues:
                    console.print(f"  • {issue}")
                sys.exit(1)
        else:
            # Original detailed logging
            logger.warning("System validation issues found:")
            for issue in system_issues:
                logger.warning(f"  • {issue}")

            # Fatal issues (missing dependencies)
            fatal_issues = [
                issue
                for issue in system_issues
                if "Missing required dependency" in issue
            ]
            if fatal_issues:
                logger.error("Cannot proceed due to missing dependencies.")
                sys.exit(1)

    # Validate video file
    if not will_use_consolidated_formatter:
        logger.info(f"Validating video file: {video_path}")

    video_validation = validate_video_file(video_path)

    if "error" not in video_validation["metadata"]:
        metadata = video_validation["metadata"]
        if not will_use_consolidated_formatter:
            duration_str = f"{metadata['duration']:.1f}s"
            resolution_str = f"{metadata['width']}x{metadata['height']}"
            fps_str = f"{metadata['fps']:.1f} FPS"
            logger.info(
                f"Video: {duration_str}, {resolution_str}, {fps_str}, {metadata['codec']}"
            )
    else:
        error_msg = f"Video validation failed: {video_validation['metadata']['error']}"
        if will_use_consolidated_formatter:
            console.print(f"[red]Error:[/red] {error_msg}")
        else:
            logger.error(error_msg)
        sys.exit(1)

    return video_validation


def show_banner() -> None:
    """Show application banner."""
    banner_text = Text("Person From Vid", style="bold blue")
    subtitle_text = Text(
        "AI-powered video frame extraction and pose categorization", style="dim"
    )

    panel = Panel(
        f"{banner_text}\n{subtitle_text}", border_style="blue", padding=(1, 2)
    )
    console.print(panel)


def _apply_logging_overrides(config: Config, cli_args: dict) -> None:
    """Apply logging-specific overrides."""
    # Logging overrides
    if cli_args["verbose"]:
        config.logging.verbose = True
        config.logging.level = LogLevel.DEBUG
    elif cli_args["quiet"]:
        config.logging.level = LogLevel.WARNING
    else:
        config.logging.level = LogLevel(cli_args["log_level"])

    # Structured output override
    if cli_args["no_structured_output"]:
        config.logging.enable_structured_output = False


def _apply_model_overrides(config: Config, cli_args: dict) -> None:
    """Apply model-specific overrides."""
    # Model overrides
    if cli_args["device"]:
        config.models.device = cli_args["device"]

    if cli_args["batch_size"]:
        config.models.batch_size = cli_args["batch_size"]

    if cli_args["confidence"]:
        config.models.confidence_threshold = cli_args["confidence"]


def _apply_extraction_overrides(config: Config, cli_args: dict) -> None:
    """Apply frame extraction overrides."""
    # Frame extraction overrides
    if cli_args["max_frames"]:
        config.frame_extraction.max_frames_per_video = cli_args["max_frames"]

    # Quality overrides
    if cli_args["quality_threshold"]:
        config.frame_selection.min_quality_threshold = cli_args["quality_threshold"]


def _apply_output_overrides(config: Config, cli_args: dict) -> None:
    """Apply output-specific overrides."""
    # Output overrides
    if cli_args["output_format"]:
        config.output.image.format = cli_args["output_format"]

    if cli_args["output_jpeg_quality"]:
        config.output.image.jpeg.quality = cli_args["output_jpeg_quality"]

    if cli_args["output_face_crop_enabled"] is not None:
        config.output.image.face_crop_enabled = cli_args["output_face_crop_enabled"]

    if cli_args["output_face_crop_padding"]:
        config.output.image.face_crop_padding = cli_args["output_face_crop_padding"]

    if cli_args["face_restoration_enabled"] is not None:
        config.output.image.face_restoration_enabled = cli_args["face_restoration_enabled"]

    if cli_args["face_restoration_strength"]:
        config.output.image.face_restoration_strength = cli_args["face_restoration_strength"]

    if cli_args["crop_padding"]:
        config.output.image.pose_crop_padding = cli_args["crop_padding"]

    if cli_args["crop_ratio"]:
        config.output.image.crop_ratio = cli_args["crop_ratio"]
        # Automatically enable cropping when crop ratio is specified
        config.output.image.enable_pose_cropping = True

    if cli_args["full_frames"]:
        config.output.image.full_frames = True

    if cli_args["output_png_optimize"] is not None:
        config.output.image.png.optimize = cli_args["output_png_optimize"]

    if cli_args["resize"]:
        config.output.image.resize = cli_args["resize"]

    if cli_args["min_frames_per_category"]:
        config.output.min_frames_per_category = cli_args["min_frames_per_category"]

    if cli_args["max_frames_per_category"]:
        config.output.max_frames_per_category = cli_args["max_frames_per_category"]


def _apply_processing_overrides(config: Config, cli_args: dict) -> None:
    """Apply processing overrides."""
    # Processing overrides
    if cli_args["force"]:
        config.processing.force_restart = True

    # Storage overrides
    if cli_args["keep_temp"]:
        config.storage.keep_temp = True


def apply_cli_overrides(config: Config, cli_args: dict) -> None:
    """Apply CLI argument overrides to configuration."""
    _apply_logging_overrides(config, cli_args)
    _apply_model_overrides(config, cli_args)
    _apply_extraction_overrides(config, cli_args)
    _apply_output_overrides(config, cli_args)
    _apply_processing_overrides(config, cli_args)


def show_processing_plan(video_path: Path, output_dir: Path, config: Config) -> None:
    """Show the processing plan to the user."""
    get_logger("cli")

    plan_text = Text("Processing Plan", style="bold green")

    details = [
        f"Input video: {video_path}",
        f"Output directory: {output_dir}",
        f"Device: {config.models.device}",
        f"Batch size: {config.models.batch_size}",
        f"Confidence threshold: {config.models.confidence_threshold}",
        "Resume enabled: always (use --force to restart)",
        f"Output format: {config.output.image.format.upper()}",
        f"Output quality: {config.output.image.jpeg.quality if config.output.image.format.lower() in ['jpg', 'jpeg'] else 'PNG optimized' if config.output.image.png.optimize else 'PNG standard'}",
        f"Face crops: {'enabled' if config.output.image.face_crop_enabled else 'disabled'}",
    ]

    if config.frame_extraction.max_frames_per_video:
        details.append(f"Max frames: {config.frame_extraction.max_frames_per_video}")

    if config.output.image.resize:
        details.append(f"Image resize: {config.output.image.resize}px max dimension")

    # Temp directory handling
    if config.storage.keep_temp:
        details.append("Temp files: kept after processing")
    else:
        details.append("Temp files: cleaned up after processing")

    if config.processing.force_restart:
        details.append("Force restart: existing state will be deleted to start fresh")

    plan_content = "\n".join(details)

    panel = Panel(plan_content, title=plan_text, border_style="green", padding=(1, 2))
    console.print(panel)


if __name__ == "__main__":
    main()
