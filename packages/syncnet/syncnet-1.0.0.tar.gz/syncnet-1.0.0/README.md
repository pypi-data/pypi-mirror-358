<div id="top">

<!-- HEADER STYLE: CONSOLE -->
<div align="center">

```console
 ████  ██  ██ ██   ██  ████  ██   ██ ██████ ██████ 
██      ████  ███  ██ ██     ███  ██ ██       ██   
 ████    ██   ██ █ ██ ██     ██ █ ██ ████     ██   
    ██   ██   ██  ███ ██     ██  ███ ██       ██   
█████    ██   ██   ██  ████  ██   ██ ██████   ██   


```

</div>

<!-- BADGES -->
<img src="https://img.shields.io/github/license/jtenorio-dev/syncnet?style=flat-square&logo=opensourceinitiative&logoColor=white&color=8a2be2" alt="license">
<img src="https://img.shields.io/github/last-commit/jtenorio-dev/syncnet?style=flat-square&logo=git&logoColor=white&color=8a2be2" alt="last-commit">
<img src="https://img.shields.io/github/languages/top/jtenorio-dev/syncnet?style=flat-square&color=8a2be2" alt="repo-top-language">
<img src="https://img.shields.io/github/languages/count/jtenorio-dev/syncnet?style=flat-square&color=8a2be2" alt="repo-language-count">

<em>Built with the tools and technologies:</em>

<img src="https://img.shields.io/badge/TOML-9C4121.svg?style=flat-square&logo=TOML&logoColor=white" alt="TOML">
<img src="https://img.shields.io/badge/Python-3776AB.svg?style=flat-square&logo=Python&logoColor=white" alt="Python">

</div>
<br>

## 💧 Table of Contents

<details>
<summary>Table of Contents</summary>

- [💧 Table of Contents](#-table-of-contents)
- [🌊 Overview](#-overview)
- [🔵 Project Structure](#-project-structure)
    - [🔷 Project Index](#-project-index)
- [💠 Getting Started](#-getting-started)
    - [🅿️ Prerequisites](#-prerequisites)
    - [🌀 Installation](#-installation)
    - [🔹 Usage](#-usage)
    - [❄ ️ Testing](#-testing)
- [🧊 Roadmap](#-roadmap)
- [⚪ Contributing](#-contributing)
- [⬜ License](#-license)
- [✨ Acknowledgments](#-acknowledgments)

</details>

---

## 🌊 Overview

<strong>Syncnet</strong> is a lightweight multiplayer library for python games, designed to simplify real-time networking by handling synchronization of game state and communication between clients and server with minimal setup and overhead.

---

## 🔵 Project Structure

```sh
└── syncnet/
    ├── License.txt
    ├── README.md
    ├── __init__.py
    ├── docs
    │   └── README.md
    ├── examples
    │   ├── __init__.py
    │   ├── client.py
    │   └── server.py
    ├── pyprojet.toml
    ├── src
    │   └── syncnet
    ├── tests
    │   ├── __init__.py
    │   └── test_server.py
    └── utils
        ├── __init__.py
        └── logger.py
```

### 🔷 Project Index

<details open>
	<summary><b><code>SYNCNET/</code></b></summary>
	<!-- __root__ Submodule -->
	<details>
		<summary><b>__root__</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ __root__</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/jtenorio-dev/syncnet/blob/master/pyprojet.toml'>pyprojet.toml</a></b></td>
					<td style='padding: 8px;'>Code>❯ Rroject's metadata, dependencies, and build system requirements.</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/jtenorio-dev/syncnet/blob/master/License.txt'>License.txt</a></b></td>
					<td style='padding: 8px;'>Code>❯ MIT License</code></td>
				</tr>
			</table>
		</blockquote>
	</details>
	<!-- utils Submodule -->
	<details>
		<summary><b>utils</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ utils</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/jtenorio-dev/syncnet/blob/master/utils/logger.py'>logger.py</a></b></td>
					<td style='padding: 8px;'>Code>❯ Use for debugging the library.</code></td>
				</tr>
			</table>
		</blockquote>
	</details>
	<!-- examples Submodule -->
	<details>
		<summary><b>examples</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ examples</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/jtenorio-dev/syncnet/blob/master/examples/client.py'>client.py</a></b></td>
					<td style='padding: 8px;'>Code>❯ Example of client implementation</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/jtenorio-dev/syncnet/blob/master/examples/server.py'>server.py</a></b></td>
					<td style='padding: 8px;'>Code>❯ Example of server implementation.</code></td>
				</tr>
			</table>
		</blockquote>
	</details>
	<!-- src Submodule -->
	<details>
		<summary><b>src</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ src</b></code>
			<!-- syncnet Submodule -->
			<details>
				<summary><b>syncnet</b></summary>
				<blockquote>
					<div class='directory-path' style='padding: 8px 0; color: #666;'>
						<code><b>⦿ src.syncnet</b></code>
					<table style='width: 100%; border-collapse: collapse;'>
					<thead>
						<tr style='background-color: #f8f9fa;'>
							<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
							<th style='text-align: left; padding: 8px;'>Summary</th>
						</tr>
					</thead>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/jtenorio-dev/syncnet/blob/master/src/syncnet/server.py'>server.py</a></b></td>
							<td style='padding: 8px;'>Code>❯ Server to handle client connection and process requests</code></td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/jtenorio-dev/syncnet/blob/master/src/syncnet/endpoint.py'>endpoint.py</a></b></td>
							<td style='padding: 8px;'>Code>❯ Defines routes handling specific client's requests and responses.</code></td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/jtenorio-dev/syncnet/blob/master/src/syncnet/listener.py'>listener.py</a></b></td>
							<td style='padding: 8px;'>Code>❯ Client's connection to the server.</code></td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/jtenorio-dev/syncnet/blob/master/src/syncnet/channel.py'>channel.py</a></b></td>
							<td style='padding: 8px;'>Code>❯ server-representation-of-a-client.</code></td>
						</tr>
					</table>
				</blockquote>
			</details>
		</blockquote>
	</details>
</details>

---

## 💠 Getting Started

### 🅿️ Prerequisites

This project requires the following dependencies:

- **Programming Language:** Python 3.12

### 🌀 Installation

Build syncnet from the source and intsall dependencies:

1. **Clone the repository:**

    ```sh
    ❯ git clone https://github.com/jtenorio-dev/syncnet
    ```

2. **Navigate to the project directory:**

    ```sh
    ❯ cd syncnet
    ```

3. **Or install using pip:**

	```sh
	pip install syncnet
	```

### 🔹 Usage

Run the project with:
```python
import syncnet
```

### ❄️ Testing

Syncnet uses the __unittest__ test framework. Run the test suite with:
```sh
python -m unittest discover
```

---

## 🧊 Roadmap

- [ ] **`Tests cases`**: Write more test cases.
- [ ] **`Examples`**: Write more examples and documentation about its usage.
- [ ] **`Refactoring`**: Refactor the code and remove the unecessary loggings.

---

## ⚪ Contributing

- **💬 [Join the Discussions](https://github.com/jtenorio-dev/syncnet/discussions)**: Share your insights, provide feedback, or ask questions.
- **🐛 [Report Issues](https://github.com/jtenorio-dev/syncnet/issues)**: Submit bugs found or log feature requests for the `syncnet` project.
- **💡 [Submit Pull Requests](https://github.com/jtenorio-dev/syncnet/blob/main/CONTRIBUTING.md)**: Review open PRs, and submit your own PRs.

<details closed>
<summary>Contributing Guidelines</summary>

1. **Fork the Repository**: Start by forking the project repository to your github account.
2. **Clone Locally**: Clone the forked repository to your local machine using a git client.
   ```sh
   git clone https://github.com/jtenorio-dev/syncnet
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
   <a href="https://github.com{/jtenorio-dev/syncnet/}graphs/contributors">
      <img src="https://contrib.rocks/image?repo=jtenorio-dev/syncnet">
   </a>
</p>
</details>

---

## ⬜ License

Syncnet is protected under the [LICENSE](https://choosealicense.com/licenses) License. For more details, refer to the [LICENSE](https://choosealicense.com/licenses/) file.

---

## ✨ Acknowledgments

- Credit `contributors`, `inspiration`, `references`, etc.

<div align="right">

[![][back-to-top]](#top)

</div>


[back-to-top]: https://img.shields.io/badge/-BACK_TO_TOP-151515?style=flat-square


---
