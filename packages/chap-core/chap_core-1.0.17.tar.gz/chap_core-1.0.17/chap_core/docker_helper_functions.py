import os
from pathlib import Path
import docker
import logging

logger = logging.getLogger(__name__)


def create_docker_image(dockerfile_directory: Path | str):
    """Creates a docker image based on path to a directory that should contain a Dockerfile.
    Uses the final directory name as the name for the image (e.g. /path/to/name/ -> name)
    Returns the name.
    """
    name = Path(dockerfile_directory).stem
    logging.info(f"Creating docker image {name} from Dockerfile in {dockerfile_directory}")
    dockerfile = Path(dockerfile_directory) / "Dockerfile"
    logging.info(f"Looking for dockerfile {dockerfile}")
    fileobject = open(dockerfile, "rb")
    return docker_image_from_fo(fileobject, name)


def docker_image_from_fo(fileobject, name):
    client = docker.from_env()
    response = client.api.build(fileobj=fileobject, tag=name, decode=True)
    for line in response:
        if "stream" in line:
            print(line["stream"])  # .encode("utf-8"))
        else:
            print(line)
    return name


def run_command_through_docker_container(
    docker_image_name: str, working_directory: str, command: str, remove_after_run: bool = False
):
    client = docker.from_env()
    try:
        working_dir_full_path = os.path.abspath(working_directory)
    except FileNotFoundError:
        logging.error(f"Could not find working dir {working_directory}.")
        logging.error(f"Current directory is {os.getcwd()}")
        raise

    logger.info(
        f"Running command {command} in docker image {docker_image_name} with mount {working_dir_full_path}:/home/run/"
    )
    logger.info(
        f"Equivalent docker command: docker run -w /home/run -v {working_dir_full_path}:/home/run/ {docker_image_name} {command}"
    )
    container = client.containers.run(
        docker_image_name,
        command=command,
        volumes=[f"{working_dir_full_path}:/home/run/"],
        working_dir="/home/run",
        auto_remove=remove_after_run,
        detach=True,
    )

    output = container.attach(stdout=True, stream=False, logs=True)
    # get logs from container
    print(output)
    result = container.wait()
    exit_code = result["StatusCode"]
    log_output = container.logs().decode("utf-8")
    assert exit_code == 0, f"Command failed with exit code {exit_code}: {log_output}"
    container.remove()

    return log_output
