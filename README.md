<table>
<tr>
<td><img src="img/Icon.png" alt="Logo of Easy eCoC" title="Easy eCoC Logo" width="100"></td>
<td>

# Easy eCoC Community Edition

The Easy eCoC (Electronic Certificate of Conformity) application facilitates the automated processing and submission of vehicle data to the Statens Vegvesen eCOC service. It's designed to streamline the workflow for vehicle pre-registration processes, integrating functionalities like XML parsing, database management, and secure communication with Vegvesen's APIs.

</td>
</tr>
</table>



## Features

- **XML Processing**: Parse and manipulate IVI XML files for vehicle data submission.
- **Data Submission**: Automate the process of sending vehicle data to Vegvesen and handling responses.
- **Environment Switching**: Toggle between Test (`synt.utv.vegvesen.no`) and Production (`vegvesen.no`) environments from the Settings tab, with separate credentials stored per environment.
- **Secure Communication**: Utilize OAuth2 tokens for authenticated requests to Vegvesen.
- **Local Data Storage**: Store application settings and response data securely using SQLite.
- **User Interface**: A GUI built with ttkbootstrap, providing a user-friendly experience for managing vehicle registrations.
- **Certificate Import**: Import .p12/.pfx certificates directly from the GUI, extracting private key, public key, and full certificate chain.

## Installation

This application requires Python 3.11 or newer. Dependencies are managed using [uv](https://docs.astral.sh/uv/).

1. Clone the repository to your local machine:

```bash
git clone https://github.com/TheOldHook/Easy-eCoC-CE.git
cd easy-ecoc-ce
```

2. Install dependencies:
```bash
uv sync
```

3. Run the application:
```bash
uv run python ecoc-gui.py
```

Follow the GUI prompts to load XML files, enter vehicle information, and submit data to Vegvesen.

You need to add your company certificate to be able to auth with Samarbeidsportalen and Vegvesen.
The easiest way is to use the **Certificate Import** tab to import a .p12/.pfx file directly — this will extract:
- `private_key.pem` — Your company private key
- `public_key.pem` — Your company public key
- `virksomhet.cer` — Full certificate chain (base64 DER, no BEGIN/END lines)

Alternatively, you can provide these files manually.

## Building Executables

### Automated Build (GitHub Actions)

The project includes a GitHub Actions workflow that automatically builds executables for **Windows, Linux, and macOS**:

- **On every push to main/master**: Creates build artifacts for all platforms
- **On tagged releases** (e.g., `v1.0.0`): Creates a GitHub release with executables for all platforms
- **Manual trigger**: Can be run manually from the Actions tab

To create a release:
```bash
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

The executables will be available in the GitHub Releases section:
- `Easy-eCoC-Windows.exe` - Windows executable
- `Easy-eCoC-Linux` - Linux executable

### Local Build

To build the executable locally on your platform:

1. Install development dependencies:
```bash
uv sync --group dev
```

2. Build using PyInstaller:
```bash
uv run pyinstaller easy-ecoc.spec
```

**Windows users** can simply run:
```bash
build.bat
```

The executable will be created in the `dist/` directory.

**Note**: The spec file (`easy-ecoc.spec`) ensures all resources (images) are bundled with the executable and works across all platforms.

## Contributing
Contributions are welcome! Feel free to open issues for any bugs or feature requests, or submit pull requests for improvements.

License
This project is licensed under the MIT License - see the LICENSE file for details.

Acknowledgements
ttkbootstrap for the GUI components.
The Python cryptography library for secure data handling.


