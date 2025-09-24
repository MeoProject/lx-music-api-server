English | [简体中文](README.md)

<div align="center">

![lx-music-api-server](https://socialify.git.ci/MeoProject/lx-music-api-server/image?description=1&forks=1&issues=1&logo=https%3A%2F%2Fraw.githubusercontent.com%2FMeoProject%2Flx-music-api-server%2Fmain%2Fres%2Ficon.png&owner=1&pulls=1&stargazers=1&theme=Auto)

![GitHub Repo Size](https://img.shields.io/github/repo-size/MeoProject/lx-music-api-server?style=for-the-badge)
[![GitHub License](https://img.shields.io/github/license/MeoProject/lx-music-api-server?style=for-the-badge)](https://github.com/MeoProject/lx-music-api-server/blob/main/LICENSE)

</div>

Any **account bans** or other consequences resulting from using this project **are not related to this project**

This project does not accept private customization. Issues arising from sources **not officially released by this project's GitHub** **are not related to this project**

PS: The main developer (@helloplhm-qwq) cannot maintain the project due to academic reasons. Before June 2026 (college entrance exam), please contact me (@ikun0014) first if needed. Meanwhile, we wish the main developer success in exams and admission to their ideal university.

## 💡 Feature Support

Main features:  
[x] Link retrieval (kw, kg, tx, wy, mg)  
[x] Details retrieval (kw, kg, tx, wy, mg)  
[x] Lyrics retrieval (kw, kg, tx, wy, mg)  
[x] Login refresh (kg, tx) (only these two require refresh)

[] Search (not planned)  
[] i18n (not planned)

Special features:  
[x] [Data deleted] encryption (version 2) decryption  
[x] Complete lyrics API adaptation (link retrieval, update, sponsorship, splash screen)

## 💻 Deployment Method

Environment requirements:  
≥Python 3.10  
≥Redis 6.0  
Red Hat-based systems not recommended, Debian-based systems and Windows recommended (most convenient)  
Optional: Node.js

1. Install poetry

   ```bash
   pip install poetry
   ```

2. Clone this project and enter the project directory

   ```bash
   git clone https://github.com/MeoProject/lx-music-api-server.git
   cd lx-music-api-server
   ```

3. Install dependencies

   ```bash
   poetry install --no-root
   ```

4. Start

   ```bash
   poetry run python app.py
   or
   npm run start
   ```

## 📄 Project License

This project is released under the [MIT](https://github.com/MeoProject/lx-music-api-server/blob/main/LICENSE) License. The following agreement supplements the original MIT agreement. In case of conflict, the following agreement shall prevail.

Term Definitions: In this agreement, "this project" refers to this music source project; "user" refers to the user who signs this agreement; "official music platforms" refers collectively to the official platforms of music sources built into this project, including KuWo, KuGou, Migu, etc.; "copyrighted data" refers to data owned by others, including but not limited to images, audio, names, etc.

1. The data source principle of this project is to pull data from the public servers of various official music platforms. After simple filtering and merging of the data, it is displayed. Therefore, this project is not responsible for the accuracy of the data.
2. Copyrighted data may be generated during the use of this project. This project does not own the ownership of such copyrighted data. To avoid infringement, users must clear the copyrighted data generated during the use of this project within **24 hours**.
3. The user is responsible for any direct, indirect, special, incidental, or consequential damages of any nature arising from the use of this project, including those arising from this agreement or from the use or inability to use this project (including but not limited to damages for loss of goodwill, work stoppage, computer failure or malfunction, or any and all other commercial damages or losses).
4. This project is completely free and open-source on GitHub for worldwide technical learning and exchange. This project does not guarantee that the technology within may not violate local laws and regulations. **It is prohibited to use this project in violation of local laws and regulations**. The user bears responsibility for any illegal actions resulting from using this project knowingly or unknowingly in violation of local laws. This project bears no direct, indirect, special, incidental, or consequential responsibility.

By using this project, you accept the above agreement.

Music platforms are not easy to maintain. Please respect copyright and support genuine versions.  
This project is only for exploring and researching technical feasibility and does not accept any commercial cooperation (including but not limited to advertising) or donations.  
If you have questions about this, please mail to:  
helloplhm-qwq+outlook.com  
folltoshe+foxmail.com  
ikun+ikunshare.com  
(Please replace `+` with `@`)

## ✨ Star History

[![Stargazers over time](https://starchart.cc/MeoProject/lx-music-api-server.svg)](https://starchart.cc/MeoProject/lx-music-api-server)

## ⚙️ Contributors

[![Contributor](https://contrib.rocks/image?repo=MeoProject/lx-music-api-server)](https://github.com/MeoProject/lx-music-api-server/graphs/contributors)
