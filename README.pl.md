# Image Extractor AI  
English version: [EN](README.md)  
#### Video Demo: <>  

## Opis:
#### Kontekst:
Image Extractor AI jest jednym z serwisów mojego głównego projektu. W porównianiu do pozostałych serwisów jest dostępny publicznie. Dodatkowo napisałem skrypt dla ułatwienia prezentacji i korzystania z serwisu.

#### Działanie w uproszeczeniu (best_frames_extractor):
1. Service bierze jako input video.
2. Dzieli je na pojedyńcze klatki. 
3. Ocenia każdą z klatek za pomocą wybranego modelu AI.
4. Wybiera najlepsze klatki.
5. Zapisuje najlepsze klatki w wybranej lokalizacji.

## Wymagania systemowe:  
- Musisz mieć zainstalowanego dockera. Docker wszystko za ciebie zainstaluje i uruchomi service. Docker desktop:  
<https://www.docker.com/products/docker-desktop/>  
- Dla skorzystania z łatwiejszych i szybszych sposobów instalacji (sposób 1 i 2) musisz mieć zainstalowanego pythona.
- Przetwarzanie obrazów/filmów to wymagające obliczeniowo zadania. Zalecam korzystanie z projektu tylko na PC z GPU ze rdzeniami CUDA (Nvidia).
- Musisz przygotować video (.mp4) i/lub obrazy (.jpg) jako input. Możesz je umieścić w domyślnym folderze 'input_directory' dla ułatwienia, ale nie musisz.  
  
## Jak używać:  
Upewnij się, że spełniasz wymagania opisane wyżej.  [Wymagania]
  
#### Sposób 1:  
Najszybszy sposób to skorzystanie z setup.py, które zrobi wszystko za nas. \ 
Jeśli korzystasz z Windows możesz po prostu skorzystać z pliku .bat.
Natomiast jeśli korzystasz z innego systemu lub chcesz uruchomić setup.py z terminala, to zrobisz to w następujący sposób: 
**Przykład:** \  
`python setup.py best_frames_extractor` \  
albo \  
`python setup.py top_images_extractor` \  
#### Domyślne ustawinia: \
- **extractor:** best_frames_extractor \  
- **input_directory:** ./input_directory \  
- **output_directory:** ./output_directory \  
- **port:** 8100  
#### Możemy skonfigurować także najważniejsze parametry używają flag: 
**--port, -p** -> do zmiany portu na którym będzie działał extractor service (domyślnie 8100) \  
**--input, -i** -> do zmiany lokalizacji, w której jest input (video/obrazy do ekstrakcji z nich najelpszych obrazów) (domyślnie jest input_directory) \  
**--output, -o** -> do zmiany lokalizacji, w której będzie output (najlepsze obrazy) (domyślnie jest output_directory) \  
**Przykład:** \  
`python setup.py best_frames_extractor -p <your_port_here> -i <your_input_dir_here> -o <your_output_dir_here>` \  
Note: Inne domyślne parametry możesz edytować w config.py, ale upewnij się że wiesz co robisz.  

### Sposób 2:  
Ten sposób polega na zrobieniu ręcznie tego co robi setup.py, dzięki czemu nie wymaga zainstalowanego Pythona. \
**Ułatwienie:** \  
Jeśli chcesz pominąć kroki 1 i 2 skorzystaj z docker-compose: \
`docker-compose up --build -d` \
Możesz ewentualnie edytować docker-compose.yaml, jeśli nie chcesz korzystać z ustawień domyślnych. \
**Krok 1:** \  
Stwóz obraz z Dockerfile. Dockerfile znajduje się wewnątrz /extractor_service. \  
`docker build -t extractor_service_image ./extractor_service` \  
**Krok 2:** \  
Utwórz kontener z obrazu z wybranymi voluminami i portem, dając mu dostęp do GPU. Zmień domyślne wartości dla hosta wedle uznania. \
Uwaga! Zniechęcam do zmieniania domyślnych wartości dla kontenera. Patrz krok 3. \  
`docker run --name extractor_service --gpus all -p 8100:8100 -v ./input_directory:/app/input_directory -v ./output_directory:/app/output_directory -d extractor_service_image`  \     
**Krok 3:** \  
Wyślij zapytanie do serwisu. Jeśli nie zmieniłeś wartości domyślnych dla kontenera to nie musisz wysyłać nic w body do servisu. Service skorzysta z ustawień domyślnych zdefiniowanych w modelach pydantic w schemas.py. Wyślij jedynie zapytanie do wybranego przez siebie serwisu. Endpoint wygląda w następujący sposób: \
**POST/ http://localhost:<your_port_here>/extractors/<choosed_extractor_here>** \
**Przykłady:** \
`curl -X POST http://localhost:<your_port_here>/extractors/<choosed_extractor_here>` \
`curl -X POST http://localhost:8100/extractors/best_frames_extractor`
`