import subprocess
from pathlib import Path


def main():
    def run_command(command, capture_output=False):
        """Pomocnicza funkcja do uruchamiania poleceń z odpowiednim przechwytywaniem wyjścia."""
        result = subprocess.run(command, capture_output=capture_output, text=True)
        if capture_output:
            print(result.stdout)
            print(result.stderr)
        return result


    # Pobierz aktualny katalog roboczy jako obiekt Path
    current_directory = Path.cwd()

    # Zdefiniuj ścieżki do lokalnych katalogów
    input_directory = current_directory / 'input_directory'
    output_directory = current_directory / 'output_directory'

    # Upewnij się, że katalogi istnieją
    input_directory.mkdir(parents=True, exist_ok=True)
    output_directory.mkdir(parents=True, exist_ok=True)

    # Zdefiniuj komendę budowania obrazu Docker
    build_command = [
        'docker', 'build', '-t', 'extractor_service', str(current_directory / 'extractor_service')
    ]
    run_command(build_command, capture_output=True)

    # Usuń istniejący kontener, jeśli istnieje
    remove_command = [
        'docker', 'rm', '-f', 'extractor_service'
    ]
    run_command(remove_command, capture_output=True)

    # Zdefiniuj komendę uruchomienia kontenera Docker
    run_command = [
        'docker', 'run', '--name', 'extractor_service', '--gpus', 'all',
        '-p', '8100:8100',
        '-v', f'{input_directory}:/app/input_directory',
        '-v', f'{output_directory}:/app/output_directory',
        '-i', 'extractor_service'
    ]

    # Uruchom komendę i przechwytuj wyjście
    process = subprocess.Popen(run_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Odczytaj i wydrukuj wyjście
    try:
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
        stderr = process.stderr.read()
        if stderr:
            print('STDERR:', stderr.strip())
    finally:
        process.terminate()


if __name__ == "__main__":
    main()
