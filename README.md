# Pydantic AI Conversational Agents

This repository contains a collection of conversational AI agents built using Pydantic AI. Each agent demonstrates different use cases and capabilities of the Pydantic AI framework.

## Agents

### 1. McDonald's Drive-Thru AI

A conversational McDonald's drive-thru ordering system that:
- Scrapes the actual McDonald's menu from their website
- Allows natural language ordering
- Handles item customization (sizes, special instructions)
- Manages orders and checkout

#### Setup Instructions

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Set your OpenAI API key:
```bash
export OPENAI_API_KEY=your_api_key_here
```

3. Run the agent:
```bash
python3 mcdonalds.py
```

#### Example Interactions

```
Welcome to McDonald's AI Drive-Thru!
I'll fetch the latest menu for you...
Menu loaded! You can ask me to show the menu, add items to your order, or checkout.
Type 'quit' to exit.

You: show me the menu
Assistant: Here's our menu:
[Menu items displayed by category]

You: I'd like a Big Mac and a large fries
Assistant: Added 1x Big Mac to your order
Added 1x World Famous Fries (large) to your order

You: what's in my order?
Assistant: Your current order:
- 1x Big Mac: $5.99
- 1x World Famous Fries (large): $3.29
Total: $9.28

You: I'd also like a medium coke
Assistant: Added 1x Coca-Cola (medium) to your order

You: checkout
Assistant: Thank you for your order! Your order has been completed. Please pull forward to the next window.
```

The agent can handle:
- Natural language requests
- Item size specifications
- Multiple items in one request
- Order modifications
- Checkout processing

## Requirements

- Python 3.8+
- OpenAI API key
- Dependencies listed in requirements.txt

## Contributing

Feel free to contribute new agents or improve existing ones! Please follow these steps:

1. Fork the repository
2. Create a new branch for your feature
3. Add your agent implementation
4. Update the README with instructions
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 