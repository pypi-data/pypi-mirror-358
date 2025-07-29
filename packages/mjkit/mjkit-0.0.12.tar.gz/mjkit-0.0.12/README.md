# mjkit

---

## Usage 

```zsh
pip install mjkit
```

## Project Structure

```sh
└── /
    ├── LICENSE
    ├── README.md
    ├── assets
    ├── build.sh
    ├── dist
    │   ├── mjkit-0.0.2-py3-none-any.whl
    │   └── mjkit-0.0.2.tar.gz
    ├── mjkit
    │   ├── __init__.py
    │   ├── errors
    │   ├── huggingface
    │   ├── support
    │   └── utiles
    ├── poetry.lock
    ├── poetry.toml
    ├── pyproject.toml
    ├── ruff.toml
    └── test.py
```

### Project Index

<details open>
	<summary><b><code>/</code></b></summary>
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
					<td style='padding: 8px;'><b><a href='/LICENSE'>LICENSE</a></b></td>
					<td style='padding: 8px;'>License the project under the MIT License to allow for open-source distribution and modification.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/pyproject.toml'>pyproject.toml</a></b></td>
					<td style='padding: 8px;'>- Define the purpose and usage of the mjkit project within the codebase architecture<br>- Highlight its role in managing Python versions and dependencies, emphasizing its compatibility with specific Python versions<br>- Additionally, stress its integration with the holidays package and the twine tool for development tasks.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/test.py'>test.py</a></b></td>
					<td style='padding: 8px;'>Enhances project architecture by integrating functionality from readmeai.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/build.sh'>build.sh</a></b></td>
					<td style='padding: 8px;'>- Automates the build process for the project by handling dependencies, updating locks, building packages, and uploading to PyPI<br>- Ensures Poetry availability, Python version compatibility, and valid PyPI API token for successful package deployment<br>- Streamlines the packaging workflow for seamless distribution.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/ruff.toml'>ruff.toml</a></b></td>
					<td style='padding: 8px;'>Define exclusion rules for commonly ignored directories in the project structure to maintain code cleanliness and focus on relevant files.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/poetry.toml'>poetry.toml</a></b></td>
					<td style='padding: 8px;'>Enable project-specific virtual environments for local development.</td>
				</tr>
			</table>
		</blockquote>
	</details>
	<!-- mjkit Submodule -->
	<details>
		<summary><b>mjkit</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ mjkit</b></code>
			<!-- utiles Submodule -->
			<details>
				<summary><b>utiles</b></summary>
				<blockquote>
					<div class='directory-path' style='padding: 8px 0; color: #666;'>
						<code><b>⦿ mjkit.utiles</b></code>
					<table style='width: 100%; border-collapse: collapse;'>
					<thead>
						<tr style='background-color: #f8f9fa;'>
							<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
							<th style='text-align: left; padding: 8px;'>Summary</th>
						</tr>
					</thead>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='/mjkit/utiles/get_folder_path.py'>get_folder_path.py</a></b></td>
							<td style='padding: 8px;'>- Define functions to locate and manage project directories based on specific indicators like <code>.venv</code>, <code>.git</code>, etc<br>- These functions help determine the project root, handle assets folder paths, and create subfolders within the assets directory<br>- The code facilitates easy access and organization of project resources.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='/mjkit/utiles/financial_dates.py'>financial_dates.py</a></b></td>
							<td style='padding: 8px;'>- Generate financial business days excluding weekends and holidays within a specified date range<br>- The code determines if a given date falls on a weekend or a holiday, filtering out non-business days<br>- This functionality is crucial for financial and securities markets to calculate valid trading days effectively.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='/mjkit/utiles/format_elapsed_time.py'>format_elapsed_time.py</a></b></td>
							<td style='padding: 8px;'>- Format elapsed time in seconds to a human-readable string<br>- Handles conversions from seconds to minutes, hours, and days<br>- Provides a clear representation of time intervals for better readability<br>- The function is versatile and can be easily integrated into various projects for time-related functionalities.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='/mjkit/utiles/get_logger.py'>get_logger.py</a></b></td>
							<td style='padding: 8px;'>- Create a custom logger with emoji tags for improved readability<br>- The <code>get_logger</code> function generates independent loggers for modules, enhancing logging with emoji-tagged messages<br>- The <code>EmojiFormatter</code> class adds emojis to log messages based on their severity levels<br>- Test examples demonstrate the loggers functionality.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='/mjkit/utiles/suppress_stdout.py'>suppress_stdout.py</a></b></td>
							<td style='padding: 8px;'>- Enable temporary suppression of standard output during code execution by utilizing the <code>suppress_stdout</code> context manager<br>- This functionality ensures that any print statements or stdout logs generated within the enclosed code block are discarded<br>- The context manager redirects output to the operating systems null device, effectively silencing any output intended for stdout.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='/mjkit/utiles/timeit.py'>timeit.py</a></b></td>
							<td style='padding: 8px;'>- Generate a decorator to measure and log execution time for functions and methods<br>- The decorator captures start time, executes the function, calculates elapsed time, and logs the result<br>- It supports both standalone functions and class methods, providing insightful timing information for various processes within the codebase architecture.</td>
						</tr>
					</table>
				</blockquote>
			</details>
			<!-- support Submodule -->
			<details>
				<summary><b>support</b></summary>
				<blockquote>
					<div class='directory-path' style='padding: 8px 0; color: #666;'>
						<code><b>⦿ mjkit.support</b></code>
					<table style='width: 100%; border-collapse: collapse;'>
					<thead>
						<tr style='background-color: #f8f9fa;'>
							<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
							<th style='text-align: left; padding: 8px;'>Summary</th>
						</tr>
					</thead>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='/mjkit/support/get_exp_save_path.py'>get_exp_save_path.py</a></b></td>
							<td style='padding: 8px;'>- Generate experiment save paths based on date and trial ID, ensuring organized storage for optimization experiments using Optuna<br>- The function creates directories, assigns unique IDs, and returns the path for saving the best model<br>- It offers flexibility for custom trial IDs or generates them automatically if not provided.</td>
						</tr>
					</table>
				</blockquote>
			</details>
			<!-- huggingface Submodule -->
			<details>
				<summary><b>huggingface</b></summary>
				<blockquote>
					<div class='directory-path' style='padding: 8px 0; color: #666;'>
						<code><b>⦿ mjkit.huggingface</b></code>
					<table style='width: 100%; border-collapse: collapse;'>
					<thead>
						<tr style='background-color: #f8f9fa;'>
							<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
							<th style='text-align: left; padding: 8px;'>Summary</th>
						</tr>
					</thead>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='/mjkit/huggingface/create_readme.py'>create_readme.py</a></b></td>
							<td style='padding: 8px;'>- Generate README markdown for creating Hugging Face Dataset/Card README.md files<br>- The code in create_readme.py constructs README content based on provided metadata like tags, datasets, and descriptions<br>- It ensures a structured YAML header and body sections, including dataset information, usage examples, and last update timestamp<br>- The script simplifies README generation for Hugging Face projects, enhancing project documentation and visibility.</td>
						</tr>
					</table>
				</blockquote>
			</details>
			<!-- errors Submodule -->
			<details>
				<summary><b>errors</b></summary>
				<blockquote>
					<div class='directory-path' style='padding: 8px 0; color: #666;'>
						<code><b>⦿ mjkit.errors</b></code>
					<table style='width: 100%; border-collapse: collapse;'>
					<thead>
						<tr style='background-color: #f8f9fa;'>
							<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
							<th style='text-align: left; padding: 8px;'>Summary</th>
						</tr>
					</thead>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='/mjkit/errors/error.py'>error.py</a></b></td>
							<td style='padding: 8px;'>- Define a custom error class, NoDataReceivedError, to handle cases where no data is returned during a query<br>- This class is crucial for managing scenarios where expected data is missing, ensuring robust error handling within the projects architecture.</td>
						</tr>
					</table>
				</blockquote>
			</details>
		</blockquote>
	</details>
</details>

---

## License

This project is licensed under a **Custom Non-Commercial License**.  
- ✔️ Free for non-commercial, personal, and academic use  
- ❌ Commercial use is prohibited without prior permission  
- 📎 Must credit the original author ([devmjun](https://github.com/devmjun/tor-request))

See [LICENSE](./LICENSE) for full details.

Copyright (c) 2025 minjun ju (dev.mjun@gmail.com)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to use,
copy, and modify the Software solely for **non-commercial** and **educational** purposes,
subject to the following conditions:

1. **Non-commercial Use Only**: This Software may not be used, in whole or in part,
   for commercial advantage or monetary compensation without explicit prior written permission
   from the author. This includes use in products, services, or any revenue-generating activities.

2. **Attribution Required**: Any use of the Software must include proper attribution by:
   - Clearly stating the original author: *minjun ju*
   - Including a link to the original repository: https://github.com/devmjun/tor-request
   - Indicating whether any modifications were made

3. The above copyright notice and this permission notice shall be included
   in all copies or substantial portions of the Software.

4. **No Endorsement**: You may not use the name of the author or contributors to promote
   derived products or services without prior written consent.

5. **Modification**: You may modify and adapt the Software for non-commercial use, but any
   distribution of modified versions must also comply with the above conditions.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.