#!/usr/bin/env python3
"""Test URL button creation with updated protobuf bindings."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from anyagent import InlineButton, InlineButtonRow, InlineKeyboard
from anyagent.utils import _convert_inline_keyboard_pydantic
from anyagent.proto import agent_pb2

# Create test buttons using the helper methods
url_button = InlineButton.url_button("🌐 Website", "https://anyagent.app")
callback_button = InlineButton.callback_button("📊 Stats", "stats")

print("=== Testing URL Button Creation ===\n")

# Check Pydantic models
print("1. Pydantic Models:")
print(f"   URL Button: text='{url_button.text}', url='{url_button.url}', callback_data={url_button.callback_data}")
print(f"   Callback Button: text='{callback_button.text}', url={callback_button.url}, callback_data='{callback_button.callback_data}'")

# Create keyboard
keyboard = InlineKeyboard(rows=[
    InlineButtonRow(buttons=[url_button, callback_button])
])

# Convert to protobuf
grpc_keyboard = _convert_inline_keyboard_pydantic(keyboard)

print("\n2. Protobuf Conversion:")
for i, row in enumerate(grpc_keyboard.rows):
    print(f"   Row {i}:")
    for j, button in enumerate(row.buttons):
        action_type = button.WhichOneof("action")
        action_value = getattr(button, action_type) if action_type else None
        print(f"      Button {j}: text='{button.text}', action_type='{action_type}', action_value='{action_value}'")

# Test direct protobuf creation
print("\n3. Direct Protobuf Creation:")
pb_url_button = agent_pb2.InlineButton()
pb_url_button.text = "Direct URL Button"
pb_url_button.url = "https://example.com"

pb_callback_button = agent_pb2.InlineButton()
pb_callback_button.text = "Direct Callback Button"
pb_callback_button.callback_data = "callback_test"

print(f"   URL Button: text='{pb_url_button.text}', action='{pb_url_button.WhichOneof('action')}', value='{pb_url_button.url}'")
print(f"   Callback Button: text='{pb_callback_button.text}', action='{pb_callback_button.WhichOneof('action')}', value='{pb_callback_button.callback_data}'")

print("\n✅ Test completed successfully!")