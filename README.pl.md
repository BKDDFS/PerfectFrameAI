<div id="logo">
    <img src="static/banner.png">
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
        <a href="#key-features">Funkcje</a> &nbsp;&bull;&nbsp;
        <a href="#installation">Instalacja</a> &nbsp;&bull;&nbsp;
        <a href="#usage">Jak używać</a> &nbsp;&bull;&nbsp;
        <a href="#contributions">Contributions</a> &nbsp;&bull;&nbsp;
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
    <img src="static/demo.gif" width="1000">
    <p>Full video: <a href="https://youtu.be/FX1modlxeWA">https://youtu.be/FX1modlxeWA</a></p>
</div>
<div id="key-features">
    <h2>🔑 Kluczowe funkcje:</h2>
    <details>
        <summary>
            <strong>Best Frames Extraction 🎞️➜🖼️</strong>
            <blockquote>Wybieranie najlepszych klatek z plików video.</blockquote>
        </summary>
        <img src="static/start_frames.png" width="350">
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
        <img src="static/start_images.png" width="350">
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
        <img src="static/install.png" width="300">
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
                    <td>Zmiana portu na którym będzie działał service</td>
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
        <code>python start.py best_frames_extractor -p &lt;your_port_here&gt; -i &lt;your_input_dir_here&gt; -o &lt;your_output_dir_here&gt; --build</code><br>
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
            <li>Uruchom service: <br><code>docker-compose up --build -d</code></li>
            <li>Wyślij zapytanie pod wybrany endpoint.
            <p><strong>Przykładowe zapytania:</strong></p>
                <ul>
                    <li>Best Frames Extraction:<br><code>POST http://localhost:8100/extractors/best_frames_extractor</code></li>
                    <li>Top Frames Extraction:<br><code>POST http://localhost:8100/extractors/top_images_extractor</code></li>
                    <li>Current working extractor:<br><code>GET http://localhost:8100/</code></li>
                </ul>
            </li>
            Możesz ewentualnie edytować docker-compose.yaml, jeśli nie chcesz korzystać z ustawień domyślnych.
        </ol>
    </details>
</div>
<div id="about">
    <h2>💡O projekcie:</h2>
    <div id="contents">
        <h3>Table of Contents:</h3>
        <a href="#1vs2">v1.0 vs v2.0</a><br>
        <a href="#key-features">Funkcje</a><br>
        <a href="#installation">Instalacja</a><br>
        <a href="#usage">Jak używać</a><br>
        <a href="#contributions">Contributions</a><br>
        <a href="#feedback">Feedback</a><br>
        <a href="#licence">Licencja</a><br>
    </div>
    <div id="1vs2">
        <h3>v1.0 vs v2.0</h3>
        <p>
            <code>PerfectFrameAI</code> to narzędzie stworzone na podstawie jednego z mikro serwisów mojego głównego projektu. 
            Określam tamtą wersję jako <code>v1.0</code>.
        </p>
        <img src="static/1vs2.png">
    </div>
    <div id="build-with">
    <h3>🛠️ Build with</h3>
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
        <blockquote>Wszystkie używane zależności dostępne są w <a href="pyproject.toml">pyproject.toml.</a></blockquote>
    </ul>
    </div>
    <div id="uml">
    <h3># TODO</h3>
    </div>
    <div id="tests">
    <h3>Tests</h3>
    Testy możesz uruchomić instalując zależności z pyproject.toml i wpisując w testminal w lokalizacj projektu:
    pytest
    Testy są podzielone na testy extractor_service i testy dla service_manager.
    W pliku common.py znajdują się pliki wpółdzielone przez testy i potrzebne do ich działania.
    <p>
    Każdy moduł ma swoje testy jednostkowe.
    Testują one każdą z metod i funkcji dostępnych w modułach.
    </p>
    <details>
        <summary></summary>
    </details>
</div>
    <div id="performance">
    <h3># TODO</h3>
    </div>
    <div id="references">
    <h3># TODO</h3>
</div>
</div>
<div id="roadmap">
    <h2>🎯 Roadmap</h2>
        <p>
            Below is a list of features that we are planning to implement in the upcoming releases.
            We welcome contributions and suggestions from the community.
        </p>
        <ul>
            <li>
                Implementacja Nvidia DALI.
                <ul>
                    <li>Umożliwi przeniesienia dekodowania klatek (obecnie najdłuższej części) na GPU.</li>
                    <li>Dodatkowo umożliwi operowanie od razu na obiektach Tensor bez dodatkowych konwersji.</li>
                </ul>
                Podsumowując dodanie DALI powinno być kolejny poważnym krokiem naprzód,
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
    <h2>👋 How to Contribute</h2>
    <p>
        We welcome contributions from the community!
        If you're interested in contributing to this project,
        please take a moment to read our <a href=".github/CONTRIBUTING.md">Contribution Guide</a>. It includes all the information you need to get started, such as:
    </p>
    <ul>
        <li>How to report bugs and submit feature requests</li>
        <li>Our coding standards and guidelines</li>
        <li>Instructions for setting up your development environment</li>
        <li>The process for submitting pull requests</li>
    </ul>
    <p>
        Your contributions help make this project better, and we appreciate your efforts. Thank you for your support!
    </p>
</div>
<div id="feedback">
    <h2>❤️ How to Give Feedback</h2>
    <p>I am looking for feedback on the code quality and design of this project. If you have any suggestions on how to improve the code, please feel free to:</p>
    <ul>
        <li>Leave comments on specific lines of code via pull requests.</li>
        <li>Open an issue to discuss larger changes or general suggestions.</li>
        <li>Participate in discussions in the 'Discussions' section of this repository.</li>
    </ul>
    <p>Your insights are invaluable and greatly appreciated as they will help improve the project and my skills as a developer.</p>
    <blockquote>For more direct communication, you can reach me at <a href="Bartekdawidflis@gmail.com">Bartekdawidflis@gmail.com</a>.</blockquote>
</div>
<div id="support">
    <h2>⭐️ Support</h2>
    <p>Don't forget to leave a star ⭐️.</p>
</div>
<div id="licence">
    <h2>📜 Licencja</h2>
    <p>
        PerfectFrameAI is licensed under the GNU General Public License v3.0.
        See the <a href="/LICENSE">LICENSE</a> file for more information.
    </p>
</div>