import typer

from picsellia_cli.commands.processing.deployer import deploy_processing
from picsellia_cli.commands.processing.initializer import init_processing
from picsellia_cli.commands.processing.smoke_tester import smoke_test_processing
from picsellia_cli.commands.processing.syncer import sync_processing_params
from picsellia_cli.commands.processing.tester import test_processing
from picsellia_cli.commands.training.deployer import deploy_training
from picsellia_cli.commands.training.initializer import init_training
from picsellia_cli.commands.training.smoke_tester import smoke_test_training
from picsellia_cli.commands.training.tester import test_training
from picsellia_cli.utils.pipeline_config import PipelineConfig

app = typer.Typer()

VALID_PIPELINE_TYPES = ["training", "processing"]
PROCESSING_TEMPLATES = ["dataset_version_creation", "pre_annotation"]
TRAINING_TEMPLATES = ["ultralytics"]


@app.command(name="init")
def init(
    pipeline_name: str,
    type: str = typer.Option(
        None, help="Type of pipeline ('training' or 'processing')"
    ),
    template: str = typer.Option(None, help="Template to use"),
    output_dir: str = typer.Option(".", help="Where to create the pipeline"),
    use_pyproject: bool = typer.Option(True, help="Use pyproject.toml"),
):
    if type is None:
        typer.secho(
            f"❌ Missing required option: --type. Choose from {VALID_PIPELINE_TYPES}.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)

    available_templates = (
        PROCESSING_TEMPLATES if type == "processing" else TRAINING_TEMPLATES
    )

    if template is None:
        typer.secho(
            f"❌ Missing required option: --template. Choose from: {', '.join(available_templates)}",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)

    if type not in VALID_PIPELINE_TYPES:
        typer.secho(
            f"❌ Invalid type: '{type}'. Choose from {VALID_PIPELINE_TYPES}.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)

    if template not in available_templates:
        typer.echo(
            f"❌ Invalid template '{template}' for type '{type}'.\n"
            f"👉 Available: {', '.join(available_templates)}"
        )
        raise typer.Exit(code=1)

    if type == "training":
        init_training(
            pipeline_name=pipeline_name,
            template=template,
            output_dir=output_dir,
            use_pyproject=use_pyproject,
        )
    elif type == "processing":
        init_processing(
            pipeline_name=pipeline_name,
            template=template,
            output_dir=output_dir,
            use_pyproject=use_pyproject,
        )
    else:
        typer.echo(
            f"❌ Invalid pipeline type '{type}'. Must be 'training' or 'processing'."
        )
        raise typer.Exit()


def get_pipeline_type(pipeline_name: str) -> str:
    try:
        config = PipelineConfig(pipeline_name)
        pipeline_type = config.get("metadata", "type")
        if not pipeline_type:
            raise ValueError
        return pipeline_type
    except Exception:
        typer.echo(f"❌ Could not determine type for pipeline '{pipeline_name}'.")
        raise typer.Exit()


@app.command(name="test")
def test(
    pipeline_name: str,
    reuse_dir: bool = typer.Option(
        False, help="Reuse previous run directory if available"
    ),
):
    pipeline_type = get_pipeline_type(pipeline_name)
    if pipeline_type == "TRAINING":
        test_training(pipeline_name=pipeline_name, reuse_dir=reuse_dir)
    elif pipeline_type in {"DATASET_VERSION_CREATION", "PRE_ANNOTATION"}:
        test_processing(pipeline_name=pipeline_name, reuse_dir=reuse_dir)
    else:
        typer.echo(f"❌ Unknown pipeline type for '{pipeline_name}'.")
        raise typer.Exit()


@app.command(name="smoke-test")
def smoke_test(pipeline_name: str):
    pipeline_type = get_pipeline_type(pipeline_name)
    if pipeline_type == "TRAINING":
        smoke_test_training(pipeline_name=pipeline_name)
    elif (
        pipeline_type == "DATASET_VERSION_CREATION" or pipeline_type == "PRE_ANNOTATION"
    ):
        smoke_test_processing(pipeline_name=pipeline_name)
    else:
        typer.echo(f"❌ Unknown pipeline type for '{pipeline_name}'.")
        raise typer.Exit()


@app.command(name="deploy")
def deploy(pipeline_name: str):
    pipeline_type = get_pipeline_type(pipeline_name)
    if pipeline_type == "TRAINING":
        deploy_training(pipeline_name=pipeline_name)
    elif (
        pipeline_type == "DATASET_VERSION_CREATION" or pipeline_type == "PRE_ANNOTATION"
    ):
        deploy_processing(pipeline_name=pipeline_name)
    else:
        typer.echo(f"❌ Unknown pipeline type for '{pipeline_name}'.")
        raise typer.Exit()


@app.command(name="sync")
def sync(pipeline_name: str):
    pipeline_type = get_pipeline_type(pipeline_name)

    if pipeline_type == "DATASET_VERSION_CREATION":
        sync_processing_params(pipeline_name=pipeline_name)
    elif pipeline_type == "TRAINING":
        typer.echo("⚠️ Syncing training parameters is not implemented yet.")
        # sync_training_params(pipeline_name=pipeline_name)
    else:
        typer.echo(f"❌ Unknown pipeline type for '{pipeline_name}'.")
        raise typer.Exit()


if __name__ == "__main__":
    app()
