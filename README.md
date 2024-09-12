<p align="center">
    <h1 align="center">FREETUNES</h1>
</p>
<p align="center">
    <em><code>❯ An alternative to Spotify</code></em>
</p>
<p align="center">
	<img src="https://img.shields.io/github/license/NikantYadav/FreeTunes?style=flat&logo=opensourceinitiative&logoColor=white&color=0080ff" alt="license">
	<img src="https://img.shields.io/github/last-commit/NikantYadav/FreeTunes?style=flat&logo=git&logoColor=white&color=0080ff" alt="last-commit">
	<img src="https://img.shields.io/github/languages/top/NikantYadav/FreeTunes?style=flat&color=0080ff" alt="repo-top-language">
	<img src="https://img.shields.io/github/languages/count/NikantYadav/FreeTunes?style=flat&color=0080ff" alt="repo-language-count">
</p>
<p align="center">
		<em>Built with the tools and technologies:</em>
</p>
<p align="center">
	<img src="https://img.shields.io/badge/precommit-FAB040.svg?style=flat&logo=pre-commit&logoColor=black" alt="precommit">
	<img src="https://img.shields.io/badge/JavaScript-F7DF1E.svg?style=flat&logo=JavaScript&logoColor=black" alt="JavaScript">
	<img src="https://img.shields.io/badge/Prettier-F7B93E.svg?style=flat&logo=Prettier&logoColor=black" alt="Prettier">
	<img src="https://img.shields.io/badge/HTML5-E34F26.svg?style=flat&logo=HTML5&logoColor=white" alt="HTML5">
	<img src="https://img.shields.io/badge/YAML-CB171E.svg?style=flat&logo=YAML&logoColor=white" alt="YAML">
	<img src="https://img.shields.io/badge/Chai-A30701.svg?style=flat&logo=Chai&logoColor=white" alt="Chai">
	<img src="https://img.shields.io/badge/Mocha-8D6748.svg?style=flat&logo=Mocha&logoColor=white" alt="Mocha">
	<img src="https://img.shields.io/badge/PowerShell-5391FE.svg?style=flat&logo=PowerShell&logoColor=white" alt="PowerShell">
	<img src="https://img.shields.io/badge/ESLint-4B32C3.svg?style=flat&logo=ESLint&logoColor=white" alt="ESLint">
	<br>
	<img src="https://img.shields.io/badge/Coveralls-3F5767.svg?style=flat&logo=Coveralls&logoColor=white" alt="Coveralls">
	<img src="https://img.shields.io/badge/SemVer-3F4551.svg?style=flat&logo=SemVer&logoColor=white" alt="SemVer">
	<img src="https://img.shields.io/badge/Python-3776AB.svg?style=flat&logo=Python&logoColor=white" alt="Python">
	<img src="https://img.shields.io/badge/tsnode-3178C6.svg?style=flat&logo=ts-node&logoColor=white" alt="tsnode">
	<img src="https://img.shields.io/badge/TypeScript-3178C6.svg?style=flat&logo=TypeScript&logoColor=white" alt="TypeScript">
	<img src="https://img.shields.io/badge/Express-000000.svg?style=flat&logo=Express&logoColor=white" alt="Express">
	<img src="https://img.shields.io/badge/Markdown-000000.svg?style=flat&logo=Markdown&logoColor=white" alt="Markdown">
	<img src="https://img.shields.io/badge/JSON-000000.svg?style=flat&logo=JSON&logoColor=white" alt="JSON">
</p>

<br>

#####  Table of Contents

- [ Overview](#-overview)
- [ Features](#-features)
- [ Repository Structure](#-repository-structure)
- [ Modules](#-modules)
- [ Getting Started](#-getting-started)
    - [ Prerequisites](#-prerequisites)
    - [ Installation](#-installation)
    - [ Usage](#-usage)
    - [ Tests](#-tests)
- [ Project Roadmap](#-project-roadmap)
- [ Contributing](#-contributing)
- [ License](#-license)
- [ Acknowledgments](#-acknowledgments)

---

##  Overview

FreeTunes is a streaming music platform designed to offer a unique and engaging music discovery experience. The project aims to provide users with a diverse range of music while enhancing their enjoyment through personalized recommendations.

The platform allows users to access songs from YouTube and features a backend that ensures smooth and secure operation. To improve music recommendations, FreeTunes combines different methods for suggesting songs, including analyzing song content and leveraging user preferences.

Additionally, the system categorizes songs based on their mood and develops sophisticated models to tailor recommendations to individual users. Overall, FreeTunes seeks to deliver a personalized and enjoyable music experience, differentiating itself from traditional streaming services.




---



##  Repository Structure

```sh
└── FreeTunes/
    ├── FreeTunes-main
    │   └── server
    ├── dataset
    │   ├── Collaborative Filtering
    │   ├── archive.zip
    │   ├── mxm_dataset_test.txt.zip
    │   ├── mxm_dataset_to_db.py
    │   ├── mxm_dataset_train.txt.zip
    │   ├── test.txt
    │   └── train.txt
    └── hybrid-model
        ├── collaborative.py
        ├── content.py
        ├── databasecreate.py
        └── hybrid.py
```

##  Getting Started

###  Prerequisites

**Python**, **JavaScript** 

###  Installation

Build the project from source:

1. Clone the FreeTunes repository:
```sh
❯ git clone https://github.com/NikantYadav/FreeTunes
```

2. Navigate to the project directory:
```sh
❯ cd FreeTunes
```

3. Install the required dependencies:
```sh
❯ npm install
```

###  Usage

To run the project, execute the following command:

```sh
❯ node app.js
```

###  Tests

Execute the test suite using the following command:

```sh
❯ npm test
```

---


##  Contributing

Contributions are welcome! Here are several ways you can contribute:

- **[Report Issues](https://github.com/NikantYadav/FreeTunes/issues)**: Submit bugs found or log feature requests for the `FreeTunes` project.
- **[Submit Pull Requests](https://github.com/NikantYadav/FreeTunes/blob/main/CONTRIBUTING.md)**: Review open PRs, and submit your own PRs.
- **[Join the Discussions](https://github.com/NikantYadav/FreeTunes/discussions)**: Share your insights, provide feedback, or ask questions.

<details closed>
<summary>Contributing Guidelines</summary>

1. **Fork the Repository**: Start by forking the project repository to your github account.
2. **Clone Locally**: Clone the forked repository to your local machine using a git client.
   ```sh
   git clone https://github.com/NikantYadav/FreeTunes
   ```
3. **Create a New Branch**: Always work on a new branch, giving it a descriptive name.
   ```sh
   git checkout -b new-feature-x
   ```
4. **Make Your Changes**: Develop and test your changes locally.
5. **Commit Your Changes**: Commit with a clear message describing your updates.
   ```sh
   git commit -m 'Implemented new feature x.'
   ```
6. **Push to github**: Push the changes to your forked repository.
   ```sh
   git push origin new-feature-x
   ```
7. **Submit a Pull Request**: Create a PR against the original project repository. Clearly describe the changes and their motivations.
8. **Review**: Once your PR is reviewed and approved, it will be merged into the main branch. Congratulations on your contribution!
</details>

<details closed>
<summary>Contributor Graph</summary>
<br>
<p align="left">
   <a href="https://github.com{/NikantYadav/FreeTunes/}graphs/contributors">
      <img src="https://contrib.rocks/image?repo=NikantYadav/FreeTunes">
   </a>
</p>
</details>

