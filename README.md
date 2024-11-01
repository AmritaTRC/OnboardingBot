# Discord Bot for Club Management

This Discord bot is designed to help manage club activities, track user status updates, and provide notifications. It integrates with Google Sheets to log user interactions and tracks the consistency of status updates.

## Features

- Logs user status updates to individual Google Sheets.
- Sends notifications to mentors for user warnings.
- Automatically pauses tracking for specified roles.
- Kicks users who receive too many warnings for insufficient status updates.

## Requirements

- Python 3.10.12 or higher
- Required Python packages listed in `requirements.txt`

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/SANTHOSH-MAMIDISETTI/OnboardingBot.git
cd OnboardingBot
```

### 2. Set Up a Virtual Environment

To create a virtual environment and activate it, follow these steps:

#### For Windows:

```bash
python -m venv venv
.\venv\Scripts\activate
```

#### For macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

With the virtual environment activated, install the required packages:

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root of the project and add the following variables:

```plaintext
DISCORD_TOKEN=your_discord_bot_token
GOOGLE_SERVICE_ACCOUNT_DATA='your_google_service_account_json'
```

### 5. Running the Bot

To run the bot, execute the following command:

```bash
python onboarding.py
```

## Usage

- Use the `!pause` command to toggle the bot's status.
- The bot will log messages and track user status updates in Google Sheets.


## License

This project is licensed under the GNU General Public License v3.0 (GPL-3.0). See the `LICENSE` file for more details.