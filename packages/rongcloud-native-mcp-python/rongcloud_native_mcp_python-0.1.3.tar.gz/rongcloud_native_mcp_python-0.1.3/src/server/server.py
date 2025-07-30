"""
MCP IM Server - Engine Wrapper

This server implements the MCP protocol and directly connects to the IM SDK for message sending and receiving.

"""
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, List
import click
from mcp.server.fastmcp import FastMCP

# Get project root directory
PROJECT_ROOT = str(Path(__file__).parent.parent.parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.lib.rcim_client import RcimConversationType_Group, RcimConversationType_Private
from src.imsdk import default_sdk

# Configure logging
from src.utils.mcp_utils import logger

# Global variables
APP_KEY = ""
TOKEN = ""
NAVI_URL = ""
AREA_CODE = -1
STATS_URL = ""

app = FastMCP("rongcloud-native-mcp-python")

@app.tool()
def send_private_text_message(
    user_id: str = "",
    content: str = "",
    ext_content: dict = {}
) -> Dict[str, Any]:
    """
    Send IM message to specified user
    
    Args:
        user_id: Message recipient's ID. User_ID or Target_ID
        content: Message content to send
        ext_content: Extended content dictionary for additional message data
        
    Returns:
        Failure: Dictionary containing code and error
        Success: Dictionary containing code, message_id and message
    """
    logger.info(f"Sending private message to {user_id}: {content}")

    # Step 1: Check if IM engine is initialized
    result = check_engine_initialized()
    if result.get("code", -1) != 0:
        return result
    
    # Step 2: Send message
    result = default_sdk.send_text_message(user_id, content, RcimConversationType_Private, ext_content)
    return result
    
@app.tool()
def send_group_text_message(
    group_id: str = "",
    content: str = "",
    ext_content: dict = {}
) -> Dict[str, Any]:
    """
    Send IM message to specified group

    Args:
        group_id: Group ID or Target_ID
        content: Message content to send
        ext_content: Extended content dictionary for additional message data
        
    Returns:
        Failure: Dictionary containing code and error
        Success: Dictionary containing code, message_id and message
    """
    logger.info(f"Sending group message to {group_id}: {content}")

    # Step 1: Check if IM engine is initialized
    result = check_engine_initialized()
    if result.get("code", -1) != 0:
        return result
    
    # Step 2: Send message
    result = default_sdk.send_text_message(group_id, content, RcimConversationType_Group, ext_content)
    return result

@app.tool()
def get_private_messages(
    user_id: str = "",
    order_asc: bool = False,
    count: int = 10,
) -> List[Dict[str, Any]]:
    """
    Get historical messages with specified user(User_ID)
    
    Args:
        user_id: User ID to get historical messages with
        order_asc: Whether to sort in ascending order, default is descending
        count: Number of messages to retrieve, default is 10
        
    Returns:
        Failure: Dictionary containing code and error
        Success: Dictionary containing code and message array
    """

    # Step 1: Check if IM engine is initialized
    result = check_engine_initialized()
    if result.get("code", -1) != 0:
        return result
    
    # Step 2: Get historical messages
    return get_messages(user_id, RcimConversationType_Private, order_asc, count)

@app.tool()
def get_group_messages(
    group_id: str = "",
    order_asc: bool = False,
    count: int = 10,
) -> List[Dict[str, Any]]:
    """
    Get historical messages with specified group(Group_ID)
    
    Args:
        group_id: Group ID to get historical messages with
        order_asc: Whether to sort in ascending order, default is descending
        count: Number of messages to retrieve, default is 10
        
    Returns:
        Failure: Dictionary containing code and error
        Success: Dictionary containing code and message array
    """

    # Step 1: Check if IM engine is initialized
    result = check_engine_initialized()
    if result.get("code", -1) != 0:
        return result
    
    return get_messages(group_id, RcimConversationType_Group, order_asc, count)

@app.tool()
def send_private_image_message(
    user_id: str = "",
    local_path: str = "Without quote",
    ext_content: dict = {}
) -> Dict[str, Any]:
    """
    Send private image message
    
    Args:
        user_id: Recipient user ID
        local_path: Local image file path
        ext_content: Extended content dictionary for additional message data
        
    Returns:
        Failure: Dictionary containing code and error
        Success: Dictionary containing code, message_id and message
    """
    
    # Step 1: Check if IM engine is initialized
    result = check_engine_initialized()
    if result.get("code", -1) != 0:
        return result
    
    return default_sdk.send_image_message(user_id, local_path, RcimConversationType_Private, ext_content)

@app.tool()
def send_group_image_message(
    group_id: str = "",
    local_path: str = "Without quote",
    ext_content: dict = {}
) -> Dict[str, Any]:
    """
    Send group image message
    
    Args:
        group_id: Recipient group ID
        local_path: Local image file path
        ext_content: Extended content dictionary for additional message data
        
    Returns:
        Failure: Dictionary containing code and error
        Success: Dictionary containing code, message_id and message
    """
    
    # Step 1: Check if IM engine is initialized
    result = check_engine_initialized()
    if result.get("code", -1) != 0:
        return result
    
    return default_sdk.send_image_message(group_id, local_path, RcimConversationType_Group, ext_content)

@app.tool()
def recall_message(
    message_dict: dict = {"whole message object":"Like : {'message_id':'MESSAGE_ID', 'conversation_type':0, 'target_id':'TARGET_ID', ...}"}
) -> Dict[str, Any]:
    """
    Recall message
    
    Args:
        message_dict: Complete message object containing message_id, conversation_type, target_id, etc.
        
    Returns:
        Failure: Dictionary containing code and error
        Success: Dictionary containing code and message
    """
    result = check_engine_initialized()
    if result.get("code", -1) != 0:
        return result
    
    return default_sdk.recall_message(message_dict)

def init_and_connect(
    timeout_sec: int = 30
) -> Dict[str, Any]:
    """
    Initialize IM engine and connect to IM server
    
    Args:
        timeout_sec: Connection timeout in seconds

    Returns:
        Dictionary containing code, message, init_success(bool) and connect_success(bool)
    """
    logger.info(f"Initializing and connecting to IM server, AppKey: {APP_KEY}, token length: {len(TOKEN)}, timeout: {timeout_sec}s")
    
    # Step 1: Initialize IM engine
    if default_sdk.engine:
        logger.info(f"IM engine already exists")
    else:
        app_key_str = str(APP_KEY) if APP_KEY is not None else ""
        device_id_str = str(get_device_id())
                    
        # Initialize engine using IMSDK's initialize method
        init_result = default_sdk.engine_build(app_key_str, device_id_str, AREA_CODE, NAVI_URL, STATS_URL)
        if init_result.get("code", -1) != 0:
            logger.error(f"IM engine initialization failed: {init_result}")
            return init_result
                
        logger.info(f"IM engine initialization successful: {init_result}")
    
    # Step 2: Connect to IM server
    connect_result = default_sdk.engine_connect(TOKEN, timeout_sec)
    if connect_result.get("code", -1) != 0:
        logger.error(f"IM server connection failed: {connect_result}")
        return {
            **connect_result,
            "init_success": True,
            "connect_success": False
        }
            
    logger.info(f"IM server connection successful: {connect_result}")
    
    return {
        **connect_result,
        "init_success": True,
        "connect_success": True
    }
    
def check_engine_initialized() -> Dict[str, Any]:
    """Check if IM engine is initialized"""
    if not default_sdk.engine:
        result = init_and_connect()
        if result.get("code", -1) != 0:
            return result
    return {"code": 0}


def get_messages(
    target_id: str = "",
    conversation_type: int = RcimConversationType_Private,
    order_asc: bool = False,
    count: int = 10,
) -> List[Dict[str, Any]]:
    
    logger.info(f"Getting {count} historical messages with target_id: {target_id}, conver_type: {conversation_type}, order_asc: {order_asc}")

    # Step 1: Check if IM engine is initialized
    result = check_engine_initialized()
    if result.get("code", -1) != 0:
        return result
    
    # Step 2: Get historical messages
    messages = default_sdk.get_history_messages(target_id, conversation_type, count, order=order_asc)
    return messages

def disconnect() -> Dict[str, Any]:
    """
    Disconnect from IM server
    
    Returns:
        Dictionary containing code and message
    """
    try:
        logger.info("Disconnecting from IM server")
        result = default_sdk.engine_disconnect()
        return result
    except Exception as e:
        logger.error(f"Error occurred while disconnecting: {e}")
        return {"code": -1, "message": str(e)}

def close():
    """Close IM engine"""
    default_sdk.destroy()

def get_device_id():
    """Get device ID"""
    try:
        import json
        import uuid
        import os

        # Get package.json file path
        package_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "package.json")
        
        # Read package.json
        if os.path.exists(package_path):
            with open(package_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                device_id = config.get("device_id")
        else:
            config = {}
            device_id = None
            
        # If no device_id, generate a new one
        if not device_id:
            device_id = str(uuid.uuid4())
            config["device_id"] = device_id
            # Save to package.json
            with open(package_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
                
        logger.info(f"Using device_id: {device_id}")
    except Exception as e:
        logger.error(f"Error occurred while processing device_id: {e}")
        device_id = "mcp_demo"  # Use default value
    return device_id

def get_env(key: str, value_type: type = str, default_value: Any = "") -> Any:
    """Get environment variable with type conversion

    Args:
        key: Environment variable key
        value_type: Type to convert to (str, int, etc)
        default_value: Default value if not found

    Returns:
        Converted value or default value
    """
    value = os.getenv(key)
    if not value or value is None:
        try:
            package_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
            if os.path.exists(package_path):
                with open(package_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    value = config.get(key, default_value)
            else:
                value = default_value
        except Exception as e:
            logger.error(f"Failed to read {key} from package.json: {e}")
            value = default_value
    
    if not value or value is None or value == "":
        return default_value
        
    try:
        return value_type(value)
    except (ValueError, TypeError):
        logger.error(f"Failed to convert {key}={value} to type {value_type}")
        return default_value

def main():
    """Start IM MCP Server"""
    global APP_KEY, TOKEN, NAVI_URL, AREA_CODE, STATS_URL
    
    # Set environment variables
    APP_KEY = get_env("APP_KEY")
    TOKEN = get_env("TOKEN")
    AREA_CODE = get_env("AREA_CODE", int, -1)  # Convert to int, default -1
    NAVI_URL = get_env("NAVI_URL", str, "")
    STATS_URL = get_env("STATS_URL", str, "")

    if not APP_KEY or not TOKEN:
        logger.error("Environment variables not set, please set APP_KEY and TOKEN")
        sys.exit(1)

    # Start server
    app.run("stdio")

def version():
    """Display version information"""
    from src import __version__
    click.echo(f"rongcloud-native-mcp-python version {__version__}")

if __name__ == "__main__":
    main()