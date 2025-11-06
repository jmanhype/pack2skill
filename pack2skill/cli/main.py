"""Main CLI entry point for pack2skill."""

import click
import logging
import json
from pathlib import Path
from typing import Optional

from pack2skill import __version__
from pack2skill.core.recorder import WorkflowRecorder
from pack2skill.core.analyzer import FrameAnalyzer
from pack2skill.core.generator import SkillGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s',
)
logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version=__version__)
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def cli(verbose):
    """Pack2Skill: Transform workflows into Claude Skills automatically."""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)


@cli.command()
@click.option(
    '--output-dir', '-o',
    type=click.Path(),
    default='./recordings',
    help='Directory to save recordings'
)
@click.option(
    '--name', '-n',
    type=str,
    help='Name for the recording session'
)
@click.option(
    '--description', '-d',
    type=str,
    help='Description of what you are recording'
)
@click.option(
    '--framerate', '-f',
    type=int,
    default=12,
    help='Video framerate (default: 12 FPS)'
)
@click.option(
    '--resolution', '-r',
    type=str,
    help='Video resolution (e.g., "1440x900")'
)
@click.option(
    '--no-events',
    is_flag=True,
    help='Disable event recording (keyboard/mouse)'
)
def record(output_dir, name, description, framerate, resolution, no_events):
    """Start recording a workflow.

    Press Ctrl+C to stop recording.
    """
    output_dir = Path(output_dir)

    recorder = WorkflowRecorder(
        output_dir=output_dir,
        framerate=framerate,
        resolution=resolution,
        record_events=not no_events,
    )

    click.echo("Starting workflow recording...")
    click.echo("Press Ctrl+C to stop.\n")

    try:
        session = recorder.start_recording(name=name, description=description)
        click.echo(f"✓ Recording started: {session['name']}")

        if session.get('video_path'):
            click.echo(f"  Video: {session['video_path']}")
        if session.get('events_path'):
            click.echo(f"  Events: {session['events_path']}")

        click.echo("\nRecording in progress... Press Ctrl+C when done.")

        # Wait for user interrupt
        import signal
        signal.pause()

    except KeyboardInterrupt:
        click.echo("\n\nStopping recording...")

        # Get summary from user
        summary = click.prompt(
            '\nBriefly describe what you recorded',
            type=str,
            default='',
        )

        result = recorder.stop_recording(summary=summary)

        if result:
            click.echo(f"\n✓ Recording saved: {result.get('session_file')}")
            click.echo(f"\nNext step: analyze the recording")
            click.echo(f"  pack2skill analyze {result.get('session_file')}")
        else:
            click.echo("\n✗ Failed to save recording", err=True)

    except Exception as e:
        logger.error(f"Recording failed: {e}")
        recorder.stop_recording()
        raise click.ClickException(str(e))


@cli.command()
@click.argument('session_file', type=click.Path(exists=True))
@click.option(
    '--output-dir', '-o',
    type=click.Path(),
    help='Directory for analysis output (default: same as session file)'
)
@click.option(
    '--method',
    type=click.Choice(['scene_change', 'interval', 'hybrid']),
    default='scene_change',
    help='Frame extraction method'
)
@click.option(
    '--model',
    type=str,
    default='Salesforce/blip-image-captioning-large',
    help='Caption model to use'
)
@click.option(
    '--no-ocr',
    is_flag=True,
    help='Disable OCR text extraction'
)
def analyze(session_file, output_dir, method, model, no_ocr):
    """Analyze a recorded workflow to generate steps.

    SESSION_FILE: Path to the session JSON file from recording.
    """
    session_file = Path(session_file)

    # Load session data
    with open(session_file, 'r') as f:
        session = json.load(f)

    video_path = Path(session.get('video_path'))
    events_path = session.get('events_path')

    if not video_path.exists():
        raise click.ClickException(f"Video file not found: {video_path}")

    # Load events if available
    events = None
    if events_path and Path(events_path).exists():
        with open(events_path, 'r') as f:
            events = json.load(f)

    # Determine output directory
    if output_dir is None:
        output_dir = session_file.parent / f"{session_file.stem}_analysis"
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    click.echo(f"Analyzing video: {video_path}")
    click.echo(f"Output directory: {output_dir}")
    click.echo(f"Method: {method}")

    # Create analyzer
    analyzer = FrameAnalyzer(
        caption_model=model,
        use_ocr=not no_ocr,
    )

    # Analyze
    try:
        steps = analyzer.analyze_video(
            video_path=video_path,
            output_dir=output_dir,
            events=events,
            method=method,
        )

        # Update session file with analysis results
        session['steps'] = steps
        session['analysis_dir'] = str(output_dir)

        updated_session_file = output_dir / 'session.json'
        with open(updated_session_file, 'w') as f:
            json.dump(session, f, indent=2)

        click.echo(f"\n✓ Analysis complete: {len(steps)} steps generated")
        click.echo(f"  Results: {output_dir / 'analysis.json'}")
        click.echo(f"  Updated session: {updated_session_file}")

        click.echo(f"\nNext step: generate the skill")
        click.echo(f"  pack2skill generate {updated_session_file}")

    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        raise click.ClickException(str(e))


@cli.command()
@click.argument('session_file', type=click.Path(exists=True))
@click.option(
    '--output-dir', '-o',
    type=click.Path(),
    default='./skills',
    help='Directory to create skill in'
)
@click.option(
    '--name', '-n',
    type=str,
    help='Custom skill name'
)
@click.option(
    '--description', '-d',
    type=str,
    help='Custom skill description'
)
@click.option(
    '--version',
    type=str,
    default='0.1.0',
    help='Skill version (default: 0.1.0)'
)
def generate(session_file, output_dir, name, description, version):
    """Generate a Claude Skill from analyzed session data.

    SESSION_FILE: Path to the analyzed session JSON file.
    """
    session_file = Path(session_file)
    output_dir = Path(output_dir)

    click.echo(f"Generating skill from: {session_file}")

    generator = SkillGenerator()

    try:
        skill_dir = generator.generate_from_session_file(
            session_file=session_file,
            output_dir=output_dir,
            skill_name=name,
            description=description,
            version=version,
        )

        click.echo(f"\n✓ Skill generated: {skill_dir}")
        click.echo(f"\nSkill structure:")
        click.echo(f"  {skill_dir}/")
        click.echo(f"  ├── SKILL.md")
        click.echo(f"  ├── REFERENCE.md")
        click.echo(f"  └── scripts/")
        click.echo(f"      └── helper.py")

        click.echo(f"\nNext step: install the skill")
        click.echo(f"  pack2skill install {skill_dir}")

    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise click.ClickException(str(e))


@cli.command()
@click.argument('skill_dir', type=click.Path(exists=True))
@click.option(
    '--global', 'install_global',
    is_flag=True,
    help='Install globally (~/.claude/skills) instead of current project'
)
def install(skill_dir, install_global):
    """Install a generated skill for use with Claude.

    SKILL_DIR: Path to the skill directory.
    """
    import shutil

    skill_dir = Path(skill_dir)

    if not (skill_dir / 'SKILL.md').exists():
        raise click.ClickException(f"Not a valid skill directory: {skill_dir}")

    # Determine installation directory
    if install_global:
        install_base = Path.home() / '.claude' / 'skills'
    else:
        # Find project root (look for .claude directory)
        project_root = Path.cwd()
        while project_root != project_root.parent:
            if (project_root / '.claude').exists():
                break
            project_root = project_root.parent

        if (project_root / '.claude').exists():
            install_base = project_root / '.claude' / 'skills'
        else:
            raise click.ClickException(
                "No .claude directory found. Use --global for global installation "
                "or run from a Claude project directory."
            )

    install_base.mkdir(parents=True, exist_ok=True)
    target_dir = install_base / skill_dir.name

    # Copy skill
    if target_dir.exists():
        if click.confirm(f"Skill '{skill_dir.name}' already exists. Overwrite?"):
            shutil.rmtree(target_dir)
        else:
            click.echo("Installation cancelled.")
            return

    shutil.copytree(skill_dir, target_dir)

    click.echo(f"✓ Skill installed: {target_dir}")
    click.echo(f"\nThe skill is now available in Claude!")


@cli.command()
@click.option(
    '--global', 'list_global',
    is_flag=True,
    help='List global skills instead of project skills'
)
def list(list_global):
    """List installed skills."""
    if list_global:
        skills_dir = Path.home() / '.claude' / 'skills'
    else:
        # Find project root
        project_root = Path.cwd()
        while project_root != project_root.parent:
            if (project_root / '.claude').exists():
                break
            project_root = project_root.parent

        if (project_root / '.claude').exists():
            skills_dir = project_root / '.claude' / 'skills'
        else:
            raise click.ClickException("No .claude directory found in project")

    if not skills_dir.exists():
        click.echo("No skills installed.")
        return

    skills = [d for d in skills_dir.iterdir() if d.is_dir() and (d / 'SKILL.md').exists()]

    if not skills:
        click.echo("No skills found.")
        return

    click.echo(f"Skills in {skills_dir}:\n")

    for skill in sorted(skills):
        # Read SKILL.md to extract metadata
        skill_md = skill / 'SKILL.md'
        content = skill_md.read_text()

        # Extract description
        import re
        desc_match = re.search(r'description:\s*([^\n]+)', content)
        description = desc_match.group(1).strip() if desc_match else "No description"

        click.echo(f"  • {skill.name}")
        click.echo(f"    {description}\n")


if __name__ == '__main__':
    cli()
