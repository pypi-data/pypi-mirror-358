# Getting Started

Welcome to the MPX GenAI Python SDK! 

This SDK provides a simple interface for interacting with the MPX GenAI API. To get started, first visit the [MPX Developer Portal](https://developers.masterpiecex.com) and create an account.  You will also find the API documentation and instructions for getting your API key.

To get started using the MPX Python SDK, you will need to install the SDK and configure your environment. This guide will walk you through the process of installing the SDK and setting up your environment.

## Installation

To use these examples, first create a virtual environment and the required packages using the requirements.txt. This will vary depending on your operating system.

On Windows:

```bash
python -m venv venv
venv/scripts/activate
pip install -r requirements.txt
```
On Linux or MacOS:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configuration

To use the mpx-genai-sdk package, you will need an API key.  If you haven't already, please visit the [MPX Developer Portal](https://developers.masterpiecex.com/apps) to create an application and get your API key.

Once you have your API key you can add it to your environment variables. We use dotenv to manage environment variables but you can use any method you prefer.

Create a file called `.env` in the root of your project and add the following line:

```bash
MPX_SDK_BEARER_TOKEN=your-api-key
```

## Usage

Once you have setup the virtual environment, installed the packages and configured the .env file with your API key, you can run the examples using the following command:

```bash
python examples/one_prompt.py
```

## Additional Documentation

For additional documentation on the api as well as code examples for each endpoint, please visit the [MPX Developer Portal](https://developers.masterpiecex.com/docs).