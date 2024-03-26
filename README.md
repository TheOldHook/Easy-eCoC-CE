# Easy eCoC Community Edition

The Easy eCoC (Electronic Certificate of Conformity) application facilitates the automated processing and submission of vehicle data to the Statens Vegvesen eCOC service. It's designed to streamline the workflow for vehicle pre-registration processes, integrating functionalities like XML parsing, database management, and secure communication with Vegvesen's APIs.

## Features

- **XML Processing**: Parse and manipulate IVI XML files for vehicle data submission.
- **Data Submission**: Automate the process of sending vehicle data to Vegvesen and handling responses.
- **Secure Communication**: Utilize OAuth2 tokens for authenticated requests to Vegvesen.
- **Local Data Storage**: Store application settings and response data securely using SQLite.
- **User Interface**: A GUI built with ttkbootstrap, providing a user-friendly experience for managing vehicle registrations.

## Installation

This application requires Python 3.6 or newer. Dependencies are managed using `pip`.

1. Clone the repository to your local machine:

```bash
git clone https://github.com/TheOldHook/Easy-eCoC-CE.git
cd easy-ecoc-ce
```

Install requirements
```
pip install -r requirements.txt
```

Usage
```
python ecoc-gui.py
```

Follow the GUI prompts to load XML files, enter vehicle information, and submit data to Vegvesen.

You need to add your company certificate to be able to auth with Samarbeidsportalen and Vegvesen.
virksomhet.cer = Full certchain without --BEGIN, --END-- (remove the lines from the original key).
private_key.pem = Your company private key.


Contributing
Contributions are welcome! Feel free to open issues for any bugs or feature requests, or submit pull requests for improvements.

License
This project is licensed under the MIT License - see the LICENSE file for details.

Acknowledgements
ttkbootstrap for the GUI components.
The Python cryptography library for secure data handling.


