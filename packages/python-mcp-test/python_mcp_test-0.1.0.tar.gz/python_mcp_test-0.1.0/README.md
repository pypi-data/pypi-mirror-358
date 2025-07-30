# Python MCP Test Server

A Model Context Protocol (MCP) server with ClickUp integration.

## Features

- **add**: Add two numbers together
- **getTask**: Retrieve task information from ClickUp API

## Setup

### 1. Install Dependencies

```bash
uv sync
```

### 2. Environment Variables

1. Copy the example environment file:
   ```bash
   copy .env.example .env
   ```

2. Edit `.env` and add your ClickUp API token:
   ```
   CLICKUP_API_TOKEN=pk_your_actual_clickup_token_here
   ```

### 3. Getting Your ClickUp API Token

1. Go to your ClickUp settings
2. Navigate to "Apps" section
3. Generate a new API token
4. Copy the token that starts with `pk_`

## Running the Server

```bash
python main.py
```

## Security Notes

- Never commit your `.env` file to version control
- The `.env` file is already added to `.gitignore`
- Share the `.env.example` file with team members as a template
- In production, set environment variables through your deployment platform

## Usage

The server exposes two tools:
- `add(a: int, b: int)` - Adds two numbers
- `getTask(taskID: str)` - Retrieves ClickUp task information