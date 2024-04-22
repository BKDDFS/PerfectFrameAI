from pathlib import Path

current_directory = Path.cwd()

service_name = "extractor_service"
default_extractor = "best_frames_extractor"
dockerfile_path = str(current_directory / "extractor_service")
default_port = 8100
service_default_input_directory = "/app/input_directory"
service_default_output_directory = "/app/output_directory"
default_input_directory = str(current_directory / 'input_directory')
default_output_directory = str(current_directory / 'output_directory')

