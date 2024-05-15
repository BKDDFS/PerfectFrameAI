<div id="logo">
    <img src="../static/banner.png">
</div>
<div id="badges">
    <p align="center">
        <img alt="GitHub Downloads (all assets, all releases)" src="https://img.shields.io/github/downloads/BKDDFS/PerfectFrameAI/total?style=flat&color=blue">
        <img alt="GitHub License" src="https://img.shields.io/github/license/BKDDFS/PerfectFrameAI">
        <img alt="GitHub Release" src="https://img.shields.io/github/v/release/BKDDFS/PerfectFrameAI">
        <img alt="GitHub Repo stars" src="https://img.shields.io/github/stars/BKDDFS/PerfectFrameAI">
    </p>
</div>
<div id="navigation">
    <p align="center">
        <a href="#about">O projekcie</a> &nbsp;&bull;&nbsp;
        <a href="#key-features">Kluczowe Funkcje</a> &nbsp;&bull;&nbsp;
        <a href="#installation">Instalacja</a> &nbsp;&bull;&nbsp;
        <a href="#usage">Jak używać</a> &nbsp;&bull;&nbsp;
        <a href="#contributions">Contribute</a> &nbsp;&bull;&nbsp;
        <a href="#feedback">Feedback</a> &nbsp;&bull;&nbsp;
        <a href="#licence">Licencja</a>
    </p>
</div>
<div id="languages">
    <p align="center">
        <a href="/README.md">English</a> &nbsp;&bull;&nbsp;
        <a href="/README.pl.md">Polski</a>
    </p>
</div>
<div id="description">
    W świecie przesyconym treściami wideo, każda sekunda ma potencjał, by stać się niezapomnianym ujęciem.
    <code>PerfectFrameAI</code> to narzędzie wykorzystujące sztuczną inteligencję do analizowania materiałów wideo
    i automatycznego zapisywania najładniejszych klatek.
</div>
<div id="demo">
    <h2>🔎 Demo</h2>
    <img src="../static/demo.gif" width="1000">
    <p>Full demo: <a href="https://youtu.be/FX1modlxeWA">https://youtu.be/FX1modlxeWA</a></p>
    <img src="../static/presentation.png" width="1000">
</div>
<div id="key-features">
    <h2>🔑 Kluczowe funkcje:</h2>
    <details>
        <summary>
            <strong>Best Frames Extraction 🎞️➜🖼️</strong>
            <blockquote>Wybieranie najlepszych klatek z plików video.</blockquote>
        </summary>
        <img src="../static/start_frames.png" width="350">
        <ol>
            <p>Input: Folder z plikami video <code>.mp4</code>.</p>
            <li>Bierze pierwsze video ze wskazanej lokalizacji.</li>
            <li>
                Dzieli wideo na klatki.
                Klatki są brane co 1 sekundę wideo.
                Klatki są przetwarzane w batchach(seriach).
            </li>
            <li>Ocenia wszystkie klatki w batchu za pomocą modelu AI i nadaje im ocenę liczbową.</li>
            <li>Dzieli batch klatek na mniejsze grupy.</li>
            <li>Wybiera klatkę z najwyższą oceną liczbową z każdej grupy.</li>
            <li>Zapisuje klatki z najlepszymi ocenami w wybranej lokalizacji. </li>
            <p>Output: Klatki zapisane jako <code>.jpg</code>.</p>
        </ol>
    </details>
    <br>
    <details>
        <summary>
            <strong>Top Images Extraction 🖼️➜🖼️</strong>
            <blockquote>Wybieranie najlepszych obrazów z folderu z obrazami.</blockquote>
        </summary>
        <img src="../static/start_images.png" width="350">
        <ol>
            <p>Input: Folder z obrazami <code>.jpg</code>.</p>
            <li>Wczytuje obrazy. Obrazy są przetwarzane batchach(seriach).</li>
            <li>Ocenia wszystkie obrazy w batchu za pomocą modelu AI i nadaje im ocenę liczbową.</li>
            <li>
                Oblicza, jaki wynik musi mieć obraz, żeby znaleźć się w top 90% obrazów.
                W <code>schemas.py</code> można zmienić tę wartość - <code>top_images_percent</code>.
            </li>
            <li>Zapisuje obrazy o  w wybranej lokalizacji. </li>
            <p>Output: Obrazy zapisane jako <code>.jpg</code>.</p>
        </ol>
    </details>
</div>
<div id="installation">
    <h2>💿 Instalacja</h2>
    <blockquote>
        <h3 >Wymagania systemowe:</h3>
        <ul>
            <li>Docker</li>
            <li>Python ^3.10 (tylko sposób 1)</li>
            <li>Nvidia GPU (zalecane)</li>
            <li>10 GB wolnego miejsca na dysku</li>
        </ul> 
    </blockquote>
    <details>
        <summary>Zainstaluj Dokcer:</summary>
        Docker Desktop: <a href="https://www.docker.com/products/docker-desktop/">https://www.docker.com/products/docker-desktop/</a>
    </details>
    <details>
        <summary>Zainstaluj Python v3.10+:</summary>
        MS Store: <a href="https://apps.microsoft.com/detail/9ncvdn91xzqp?hl=en-US&gl=US">https://apps.microsoft.com/detail/9ncvdn91xzqp?hl=en-US&gl=US</a><br>
        Python.org: <a href="https://www.python.org/downloads/">https://www.python.org/downloads/</a>
    </details>
    <details>
        <summary>Pobierz <code>PerfectFrameAI</code></summary>
        <blockquote>
            Aby pobrać kod z repozytorium na GitHubie, kliknij przycisk <code>Code</code>,
            a następnie wybierz <code>Download ZIP</code>
            lub skopiuj adres URL i użyj polecenia <code>git clone</code> w terminalu.
        </blockquote>
        <img src="../static/install.png" width="300">
    </details>
</div>
<div id="usage">
    <h2>⚡ Jak używać:</h2>
    <details id="method1">
        <summary>
            <strong style="font-size: 20px;"> 🚀 Sposób 1 - CLI </strong>
            <blockquote><p><i>Wymaga Pythona. Jest prosty i wygodny.</i></p></blockquote>
        </summary>
        <p>Uruchom <code>start.py</code> z terminala.</p>
        <p><strong>Przykład dla Best Frames Extraction:</strong></p>
        <code>python start.py best_frames_extractor</code>
        <table id="flags">
            <caption><strong>Dostępne flagi</strong></caption>
            <thead>
                <tr>
                    <th>Flaga</th>
                    <th>Krótka</th>
                    <th>Opis</th>
                    <th>Typ</th>
                    <th>Domyślna wartość</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>--input_dir</td>
                    <td>-i</td>
                    <td>Zmiana inputu</td>
                    <td>str</td>
                    <td>./input_directory</td>
                </tr>
                <tr>
                    <td>--output_dir</td>
                    <td>-o</td>
                    <td>Zmiana outputu</td>
                    <td>str</td>
                    <td>./output_directory</td>
                </tr>
                <tr>
                    <td>--port</td>
                    <td>-p</td>
                    <td>Zmiana portu na którym będzie działał <code>extractor_service</code></td>
                    <td>int</td>
                    <td>8100</td>
                </tr>
                <tr>
                    <td>--build</td>
                    <td>-b</td>
                    <td>
                        Buduje nowy Docker image z nowymi podanymi ustawieniami.
                        Używaj zawsze z flagą --build, jeśli nie rozumiesz.
                    </td>
                    <td>bool</td>
                    <td>False</td>
                </tr>
            </tbody>
        </table>
        <p><strong>Przykład dla Best Frames Extraction:</strong></p> 
        <img src="../static/start_example.png">
        <p>Inne domyślne parametry możesz edytować w config.py.</p>
        <blockquote>
            <p><strong style="color: lightblue;">Ułatwienie dla użytkowników Windows:</strong><br>
            Jeśli korzystasz z Windows, możesz skorzystać z dołączonego pliku <code>quick_demo.bat</code>,
            który włączy best_frames_extractor na [wartościach domyślnych] zapisanych w config.py.
            Możesz zmienić config.py, żeby dopasować aplikację do swoich potrzeb.</p>
        </blockquote>
    </details>
    <details id="method2">
        <summary>
            <strong style="font-size: 20px;">🐳 Sposób 2 - docker-compose.yaml:</strong>
            <blockquote><p><i>Nie wymaga Pythona. Uruchom używając Docker Compose.</i></p></blockquote>
        </summary>
        <p>Docker Compose Docs: <a href="https://docs.docker.com/compose/">https://docs.docker.com/compose/</a></p>
        <ol>
            <li>Uruchom serwis: <br><code>docker-compose up --build -d</code></li>
            <li>Wyślij zapytanie pod wybrany endpoint.
            <p><strong>Przykładowe zapytania:</strong></p>
                <ul>
                    <li>Best Frames Extraction:<br><code>POST http://localhost:8100/extractors/best_frames_extractor</code></li>
                    <li>Top Frames Extraction:<br><code>POST http://localhost:8100/extractors/top_images_extractor</code></li>
                    <li>Obecnie pracujący extractor:<br><code>GET http://localhost:8100/</code></li>
                </ul>
            </li>
            Możesz ewentualnie edytować docker-compose.yaml, jeśli nie chcesz korzystać z ustawień domyślnych.
        </ol>
    </details>
</div>
<div id="about">
    <h2>💡O projekcie:</h2>
    <div id="contents">
        <h3>Spis treści:</h3>
        <a href="#how-it-works">Jak to działa</a><br>
        &nbsp&nbsp&nbsp&nbsp<a href="#input">Input modelu</a><br>
        &nbsp&nbsp&nbsp&nbsp<a href="#output">Wyniki oceniania obrazów</a><br>
        &nbsp&nbsp&nbsp&nbsp<a href="#classes">Klasy estetyczne</a><br>
        &nbsp&nbsp&nbsp&nbsp<a href="#calculating-mean">Obliczanie ostatecznej oceny obrazu</a><br>
        <a href="#implementation">Jak to jest zaimplementowane w skrócie</a><br>
        &nbsp&nbsp&nbsp&nbsp<a href="#model-architecture">Architektura modelu</a><br>
        &nbsp&nbsp&nbsp&nbsp<a href="#weights">Wagi modelu</a><br>
        &nbsp&nbsp&nbsp&nbsp<a href="#normalization">Normalizacja obrazów</a><br>
        &nbsp&nbsp&nbsp&nbsp<a href="#predictions">Przewidywanie przynależności do klas</a><br>
        &nbsp&nbsp&nbsp&nbsp<a href="#mean-calculation">Obliczanie średniej ważonej</a><br>
        <a href="#1vs2">v1.0 vs v2.0</a><br>
        <a href="#build-with">Użyte technologie</a><br>
        <a href="#tests">Testy</a><br>
        &nbsp&nbsp&nbsp&nbsp<a href="#unit">jednostkowe</a><br>
        &nbsp&nbsp&nbsp&nbsp<a href="#integration">integracyjne</a><br>
        &nbsp&nbsp&nbsp&nbsp<a href="#e2e">e2e</a><br>
    </div>
    <div id="how-it-works">
    <h2>📐 Jak to działa</h2>
    <p>
        Narzędzie używa modelu zbudowanego zgodnie z zasadami dla modeli
        Neural Image Assessment (NIMA) do określania estetyki obrazów.
    </p>
    <img src="../static/evaluation.png" width="700" style="border-radius: 10px;">
    <details id="input">
       <summary style="font-size: 20px;"><strong>Input modelu</strong></summary>
       <p>Model przyjmuje odpowiednio znormalizowane obrazy w batchu Tensor.</p>
    </details>
    <h3 id="output">Wyniki oceniania obrazów</h3>
    <p>
    Model NIMA, po przetworzeniu obrazów, zwraca wektory prawdopodobieństw, 
    gdzie każda z wartość w wektorze odpowiada prawdopodobieństwu, 
    że obraz przynależy do jednej z klas estetycznych.
    </p>
    <details id="classes">
        <summary style="font-size: 20px;"><strong>Klasy estetyczne</strong></summary>
        <p>
            Jest 10 klas estetycznych. W modelu NIMA każda z 10 klas odpowiada
            określonemu poziomowi estetyki, gdzie:
        </p>
        <ul>
            <li>Klasa 1: Bardzo niska jakość estetyczna.</li>
            <li>Klasa 2: Niska jakość estetyczna.</li>
            <li>Klasa 3: Poniżej średniej jakości estetycznej.</li>
             ...
            <li>Klasa 10: Wyjątkowo wysoka jakość estetyczna.</li>
        </ul>
    </details>
    <h3 id="calculating-mean">Obliczanie ostatecznej oceny obrazu</h3>
    <p>
        Ostateczna ocena obrazu jest obliczana za pomocą średniej
        ważonej z wyników dla każdej z klas, gdzie wagi są 
        wartościami klas od 1 do 10.
    </p>
    <h4>Przykład:</h4>
    <p>
       Załóżmy, że model zwraca następujący wektor 
       prawdopodobieństw dla jednego obrazu:
    </p>
    <pre>[0.1, 0.05, 0.05, 0.1, 0.2, 0.15, 0.1, 0.1, 0.1, 0.05]</pre>
    Oznacza to, że obraz ma:
    <ul>
        <li>10% prawdopodobieństwa przynależności do klasy 1</li>
        <li>5% prawdopodobieństwa przynależności do klasy 2</li>
        <li>5% prawdopodobieństwa przynależności do klasy 3</li>
        <li>i tak dalej...</li>
    </ul>
    <p>
       Obliczając średnią ważoną z tych prawdopodobieństw,
       gdzie wagi to wartości klas (1 do 10):
    </p>
    <img src="../static/weighted_mean.png" width="700">
    </div>
    <div id="implementation">
        <h2>📖 Implementacja w skrócie</h2>
        <img src="../static/implementation.png" width="700" style="border-radius: 10px;">
        <details id="model-architecture">
            <summary><strong>Architektura modelu</strong></summary>
            <p>
                Model NIMA używa architektury InceptionResNetV2 jako swojej podstawy.
                Ta architektura jest znana ze swojej wysokiej wydajności w zadaniach
                klasyfikacji obrazów.
            </p>
        </details>
        <details id="weights">
            <summary><strong>Wagi modelu</strong></summary>
            <p>
                Model korzysta z wcześniej wytrenowanych wag,
                wytrenowanych na dużym zbiorze danych (AVA dataset) obrazów
                ocenionych pod kątem ich jakości estetycznej.
                Narzędzie automatycznie pobiera wagi i przechowuje je
                w voluminie Docker do dalszego użytkowania.
            </p>
        </details>
        <details id="normalization">
            <summary><strong>Normalizacja obrazów</strong></summary>
            <p>
                Przed wprowadzeniem obrazów do modelu, są one normalizowane,
                aby upewnić się, że mają właściwy format i zakres wartości.
            </p>
        </details>
        <details id="predictions">
            <summary><strong>Przewidywanie przynależności do klas</strong></summary>
            <p>
                Model przetwarza obrazy i zwraca wektor 10 prawdopodobieństw,
                z których każde reprezentuje prawdopodobieństwo przynależności
                obrazu do jednej z 10 klas jakości estetycznej
                (od 1 dla najniższej jakości do 10 dla najwyższej jakości).
            </p>
        </details>
        <details id="mean-calculation">
            <summary><strong>Obliczanie średniej ważonej</strong></summary>
            <p>
                Ostateczny wynik estetyczny dla obrazu jest obliczany
                jako średnia ważona tych prawdopodobieństw,
                przy czym wyższe klasy mają większe wagi.
            </p>
        </details>
    </div>
    <div id="1vs2">
        <h2>✅ v1.0 vs v2.0</h2>
        <p>
            <code>PerfectFrameAI</code> to narzędzie stworzone na podstawie jednego z mikro serwisów mojego głównego projektu. 
            Określam tamtą wersję jako <code>v1.0</code>.
        </p>
        <table>
            <tr>
                <th>Feature</th>
                <th>v1.0</th>
                <th>v2.0</th>
            </tr>
            <tr>
                <td>CLI</td>
                <td class="cross">❌</td>
                <td class="check">✅</td>
            </tr>
            <tr>
                <td>Zautomatyzowana instalacja</td>
                <td class="cross">❌</td>
                <td class="check">✅</td>
            </tr>
            <tr>
                <td>Szybki i Prosty Setup</td>
                <td class="cross">❌</td>
                <td class="check">✅</td>
            </tr>
            <tr>
                <td>Wydajność</td>
                <td>+0%</td>
                <td>+70%</td>
            </tr>
            <tr>
                <td>Rozmiar*</td>
                <td class="cross">12.6 GB</td>
                <td class="check">8.4 GB</td>
            </tr>
            <tr>
                <td>Open Source</td>
                <td class="cross">❌</td>
                <td class="check">✅</td>
            </tr>
        </table>
        <p>*v1.0 wszystkie zależności i model vs v2.0 docker image + model</p>
        <h3>Porównanie wydajności:</h3>
        <ul>
            <h4>Platforma:</h4>
            <li>RTX3070ti (8GB)</li>
            <li>i5-13600k</li>
            <li>32GB RAM</li>
        </ul>
        <img src="../static/performance.png" height="200">
    </div>
    <div id="build-with">
    <h2>🛠️ Użyte technologie</h2>
    <ul>
        <li>Python - główny język w którym jest napisany projekt.
            Zewnętrzna część <code>PerfectFrameAI</code> używa tylko standardowych biblotek Pythona dla ułatwienia instalacji i kofiguracji narzędzia.</li>
        <li>FastAPI - framework na którym została zbudowana główna część <code>PerfectFrameAI</code> (w v1.0 Flask).</li>
        <li>OpenCV - do manipulacji obrazami.</li>
        <li>numpy - do operacji na tablicach wielowymiarowych.</li>
        <li>FFMPEG - jako rozszerzenie do OpenCV, do dekodowania klatek video.</li>
        <li>CUDA - do umożliwienia wykonywania operacji na kartach graficznych.</li>
        <li>Tensorflow - wykorzystywana bibloteka do uczenia maszynowego (w v1.0 PyTorch).</li>
        <li>Docker - dla ułatwienia budowania skąplikowanego środowiska pracy dla <code>PerfectFrameAI</code>.</li>
        <li>pytest - framework w którym napisane są testy.</li>
        <li>docker-py - używany jedynie do testowania integracji Dockera z dołączonym managerem <code>PerfectFrameAI</code>.</li>
        <li>Poetry - do zażądzania zależnościami projektu.</li>
        <blockquote>Wszystkie używane zależności dostępne są w <a href="https://github.com/BKDDFS/PerfectFrameAI/blob/main/pyproject.toml">pyproject.toml.</a></blockquote>
    </ul>
    </div>
    <div id="tests">
        <h2>🧪 Testy</h2>
        <img src="../static/tests_passed.png">
        <p>
            Testy możesz uruchomić instalując zależności z <code>pyproject.toml</code>
            i wpisując w terminal w lokalizacj projektu - <code>pytest</code>.
        </p>
        <blockquote>
            Proszę zwrócić uwagę, że w projekcie są dwa foldery <code>tests/</code>.
            <code>extractor_service</code> i <code>service_initializer</code> mają testy osobno.
            W pliku common.py znajdują się pliki wpółdzielone przez testy i potrzebne do ich działania.
        </blockquote>
        <details id="unit">
            <summary>jednostkowe</summary>
            <p>
            Każdy moduł ma swoje testy jednostkowe.
            Testują one każdą z metod i funkcji dostępnych w modułach.
            Test coverage wynosi 100% (testy w całości pokrywają logikę biznesową).
            </p>
        </details>
        <details id="integration">
            <summary>integracyjne</summary>
            <ul>
                <li>Testowanie integracji docker_manager z Dockerem.</li>
                <li>Testowanie integracji z parserem.</li>
                <li>Testowanie integracji logiki biznesowej z modelem NIMA.</li>
                <li>Testowanie integracji z FastAPI.</li>
                <li>Testowanie integracji z OpenCV.</li>
                <li>Testowanie integracji z FFMPEG.</li>
                <li>Testowanie integracji modułów między sobą na różne sposoby...</li>
            </ul>
        </details>
        <details id="e2e">
            <summary>e2e</summary>
            <ul>
                <li>Testowanie działania extractor_service jako całość.</li>
                <li>Testowanie działania extractor_service+service_initializer jako całość.</li>
            </ul>
        </details>
    </div>
</div>
<div id="roadmap">
    <h2>🎯 Roadmapa</h2>
        <p>
            Poniżej znajduje się lista funkcji, które planujemy zaimplementować w nadchodzących wersjach.
            Zapraszamy do współpracy i sugestii społeczność.
        </p>
        <ul>
            <li>
                Implementacja Nvidia DALI.
                <ul>
                    <li>Umożliwi przeniesienie dekodowania klatek (obecnie najdłuższej części) na GPU.</li>
                    <li>Dodatkowo umożliwi operowanie od razu na obiektach Tensor bez dodatkowych konwersji.</li>
                </ul>
                Podsumowując, dodanie DALI powinno być kolejnym poważnym krokiem naprzód,
                jeśli chodzi o poprawę wydajności.
            </li>
            <li>Przetestowanie działania na starszych wersjach Pythona.</li>
            <li>
                Naprawienie spillingu danych podczas oceniania klatek. 
                Obecnie ocenianie ma delikatne spowolnienie w postaci problemu ze spillingiem.
            </li>
        </ul>
</div>
<div id="contributions">
    <h2>👋 Jak zostać Contributorem</h2>
    <p>
        Jeśli jesteś zainteresowany wkładem w ten projekt,
        proszę poświęć chwilę na przeczytanie naszego 
        <a href="https://github.com/BKDDFS/PerfectFrameAI/blob/main/.github/CONTRIBUTING.md">Przewodnika dla contributorów</a>.
        Zawiera on wszystkie informacje potrzebne do rozpoczęcia, takie jak:
    </p>
    <ul>
        <li>Jak zgłaszać błędy i składać prośby o nowe funkcje</li>
        <li>Nasze standardy i wytyczne dotyczące kodowania</li>
        <li>Instrukcje dotyczące konfiguracji środowiska developerskiego</li>
        <li>Proces składania pull requestów</li>
    </ul>
    <p>
        Twój wkład pomaga uczynić ten projekt lepszym, doceniamy twoje wysiłki. Dziękujemy za wsparcie!
    </p>
</div>
<div id="feedback">
    <h2>❤️ Feedback</h2>
    <p>
        Będę bardzo wdzięczny za feedback na temat jakości mojego kodu i tego projektu. 
        Jeśli masz jakieś sugestie, proszę:
    </p>
    <ul>
        <li>Zostaw komentarze na konkretnych liniach kodu za pomocą pull requestów.</li>
        <li>
            Stwórz <a href="https://github.com/BKDDFS/PerfectFrameAI/issues">Issue</a>,
            aby omówić większe zmiany lub ogólne sugestie.
        </li>
        <li>Weź udział w dyskusjach w sekcji „Dyskusje” tego repozytorium.</li>
    </ul>
    <blockquote>W celu bezpośredniej komunikacji, możesz skontaktować się ze mną pod adresem <a href="mailto:Bartekdawidflis@gmail.com">Bartekdawidflis@gmail.com</a>.</blockquote>
</div>
<div id="support">
    <h2>⭐️ Wsparcie</h2>
    <p>Nie zapomnij zostawić gwiazdki ⭐️.</p>
</div>
<div id="references">
    <h2>🗃️ Biografia</h2>
    Oryginalna publikacja Google Brains przedstawiająca NIMA:<br>
    <a href="https://research.google/blog/introducing-nima-neural-image-assessment/">https://research.google/blog/introducing-nima-neural-image-assessment/</a><br>
    Wagi do modelu:<br>
    <a href="https://github.com/titu1994/neural-image-assessment">https://github.com/titu1994/neural-image-assessment</a>
</div>
<div id="licence">
    <h2>📜 Licencja</h2>
    <p>
        PerfectFrameAI jest licencjonowany na podstawie licencji GNU General Public License v3.0.
        Więcej informacji znajdziesz w pliku <a href="https://github.com/BKDDFS/PerfectFrameAI/blob/main/LICENSE">LICENSE</a>.
    </p>
</div>
