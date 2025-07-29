# Titanmind WhatsApp MCP

A WhatsApp marketing and messaging tool MCP (Model Control Protocol) service using [Titanmind](https://www.titanmind.so/). Handles free-form messages (24hr window) and template workflows automatically

## Overview

This service provides all the WhatsApp marketing and messaging functionalities using Titanmind. Includes features like template creation and registration with all components header, body, CTAs.., template broadcast to phone numbers in bulk. Read and send messages in a active conversation.

> This MCP utilizes Titanmind. Titanmind Account is a requirement to use this MCP. 
  

## Features

#### Conversation Management

**Get Recent Conversations**

- Retrieve all conversations with messages sent or received in the last 24 hours
    
- Returns conversation data with recent activity
    

**Get Conversation Messages**

- Fetch all messages from a specific conversation
    
- Requires: `conversation_id` (alphanumeric conversation identifier)
    

**Send WhatsApp Message**

- Send a message to an existing WhatsApp conversation
    
- Requires: `conversation_id` and `message` content
    

#### Template Management

**Create Message Template**

- Register new WhatsApp message templates for approval
    
- Configure template name (single word, underscores allowed only)
    
- Set language (default: "en") and category (MARKETING, UTILITY, AUTHENTICATION)
    
- Structure message components including:
    
    - **BODY** (required): Main text content
        
    - **HEADER** (optional): TEXT, VIDEO, IMAGE, or DOCUMENT format
        
    - **FOOTER** (optional): Footer text
        
    - **BUTTONS** (optional): QUICK_REPLY, URL, or PHONE_NUMBER actions
        

**Get Templates**

- Retrieve all created templates with approval status
    
- Optional filtering by template name
    

**Send Bulk Messages**

- Send messages to multiple phone numbers using approved templates
    
- Requires: `template_id` and list of contacts
    
- Contact format: country code alpha (e.g., "IN"), country code (e.g., "91"), and phone number
    

## Installation

### Prerequisites

- Python 3.10 or higher
    
- API Key and Business Code from [Titanmind](https://www.titanmind.so/)
    

### Install from PyPI

``` bash
pip install titan-mind-whatsapp-mcp

 ```

Or use `uv`:

``` bash
uv pip install titan-mind-whatsapp-mcp

 ```

### Manual Installation

1. Clone the repository:
    

```
git clone https://github.com/TitanmindAGI/titan-mind-whatsapp-mcp
cd titan-mind-whatsapp-mcp

 ```

2\. Install dependencies:

```
pip install -e .
# Or
uv pip install -e .

 ```

3\. Set the auth keys

```
export api-key="your-titanmind-api-key"
export bus-code="your-titanmind-business-code"

 ```

## Usage

### Run the service

In any MCP Client like Claude or Cursor, Titanmind whatsapp MCP config can be added following ways:

#### Remote Titanmind MCP server config

``` json
{
  "mcpServers": {
    "TitanMindMCP": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "http://mcp.titanmind.so/mcp/",
        "--header",
        "api-key:XXXXXXXXXXXXXXXXXXXXXXX",
        "--header",
        "bus-code:XXXXXX"
      ]
    }
  }
}

 ```

#### Local MCP project config

``` json
{
  "mcpServers": {
    "TitanMindMCP": {
      "type": "stdio",
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/path/titan-mind-mcp",
        "python",
        "main.py"
      ],
      "env": {
        "api-key": "XXXXXXXXXXXXXXXXXXXX",
        "bus-code": "XXXXXX"
      }
    }
  }
}

 ```

#### Python package Titanmind MCP

at [https://pypi.org/project/titan-mind-whatsapp-mcp/0.1.0/](https://pypi.org/project/titan-mind-whatsapp-mcp/0.1.0/)

## Development

For development:

``` bash
git clone https://github.com/TitanmindAGI/titan-mind-whatsapp-mcp
cd titan-mind-whatsapp-mcp
uv sync

 ```

# How it Works

TitanMind's WhatsApp messaging system operates under two distinct messaging modes based on timing and conversation status:

## Free-Form Messaging (24-Hour Window)

- **When Available**: Only after a user has sent a message within the last 24 hours
    
- **Content Freedom**: Any content is allowed without pre-approval
    
- **Use Case**: Ongoing conversations and immediate responses
    

## Template Messaging (Outside 24-Hour Window)

- **When Required**: For new conversations or when the 24-hour window has expired
    
- **Content Structure**: Pre-approved, structured message templates only
    
- **Use Case**: Initial outreach and re-engagement campaigns
    

## Messaging Workflow Process

1. **Check Messaging Window Status**
    
    - Verify if receiver's phone number is within the free-form messaging window
        
    - A receiver is eligible for free-form messaging if:
        
        - A conversation with their phone number already exists AND
            
        - The receiver has sent a message within the last 24 hours
            
2. **Choose Messaging Method**
    
    - **Free-Form**: Send directly if within 24-hour window
        
    - **Template**: Register and use approved template if outside window
        
3. **Template Approval Process** (if needed)
    
    - Submit template for WhatsApp approval
        
    - Wait for approval confirmation
        
    - Template becomes available for bulk messaging
        
4. **Send Message**
    
    - Execute message delivery using appropriate method
        
    - Monitor delivery status
        
5. **Verify Delivery**
    
    - Check conversation to confirm receiver successfully received the message
        
    - Track message status and engagement
        

## Usage Notes

- All tools integrate with Titanmind's WhatsApp channel messaging functionality
    
- Templates require approval before they can be used for bulk messaging
    
- For more help contact us through [https://www.titanmind.so/](https://www.titanmind.so/)
    

## License

MIT License - See LICENSE file