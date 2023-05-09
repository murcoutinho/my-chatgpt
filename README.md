# ChatGPT Web App with Audio Functionality

## Overview

My-ChatGPT is a web-based ChatGPT application that enables users to interact with OpenAI's GPT models (e.g., GPT-3.5-turbo and GPT-4) through a user-friendly interface. This powerful solution allows you to access the advanced features of GPT-4 on demand using an API key, without needing to pay for a $20 subscription. Users can type or use their voice to ask questions, and the application will respond with the generated answer. The app saves all previous conversations in your computer so that you can easily access or export it to other solutions.

Additionally, this project implements the SmartGPT model ([see this video](https://www.youtube.com/watch?v=wVzuvf9D9BU&t=866s)), which is capable of improve answers given by chatgpt by automatically using multiple clever prompts and techniques like reflection.

## Features

- Interact with OpenAI's GPT models (GPT-3.5-turbo and GPT-4) through a simple web interface.
- Use SmartGPT design with GPT-3.5-turbo or GPT-4.
- Access GPT-4 on demand using an API key, without paying for a subscription.
- Type or use your voice to ask questions.
- Automatic logging of previous conversations.
- Audio recording and transcribing functionality using the OpenAI Whisper API.
- Responsive textareas that resize automatically based on content.

## Prerequisites

To set up and run the ChatGPT Web App, you need the following:

- Python 3.6 or higher
- Flask and Flask-SocketIO packages
- OpenAI API key (obtain one from [OpenAI's website](https://beta.openai.com/signup/))

## Installation

1. Clone the repository:

```
git clone https://github.com/murcoutinho/my-chatgpt.git
```

2. Change into the project directory:

```
cd my-chatgpt
```

3. Install the required packages:

```
pip install -r requirements.txt
```
or
```
pip3 install -r requirements.txt
```

4. Set your OpenAI API key as environment variables. To securely set up the API key, follow the guide on [best practices for API key safety](https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety).


## Usage

1. Run the Flask application:

```
python3 app.py
```

2. Open a web browser and navigate to `http://localhost:5000`.

3. Choose a GPT model from the dropdown menu. Keep in mind that SmartGPT queries the API multiple times, thus it will be more expensive and slower to answer.

4. Type or use your voice to ask questions. Click the "Ask with audio: start" button to start recording your voice, and click the "Stop recording" button to stop recording and transcribe your question.

5. The application will display the generated response in the "Answer" section.

## License

This project is released under the [MIT License](LICENSE).
