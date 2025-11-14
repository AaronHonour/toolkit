"""WebSocket endpoints for real-time updates."""

import asyncio
import json
from typing import Annotated

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from unistax.agents.api.dependencies import get_event_bus
from unistax.events import EventBus
from unistax.logging import get_logger

router = APIRouter(prefix="/ws", tags=["WebSocket"])
logger = get_logger(__name__)

# Active WebSocket connections
_connections: set[WebSocket] = set()


@router.websocket("/events")
async def websocket_events(websocket: WebSocket):
    """WebSocket endpoint for real-time event updates.

    Clients can subscribe to agent events and receive real-time updates about:
    - Agent state changes
    - Task assignments
    - Task completions/failures
    - Inter-agent messages
    - System events

    Example client usage:
        ```javascript
        const ws = new WebSocket('ws://localhost:8000/api/agents/ws/events');

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log('Event:', data.event_type, data.payload);
        };

        // Subscribe to specific event types
        ws.send(JSON.stringify({
            action: 'subscribe',
            event_types: ['task_assigned', 'task_completed', 'agent_message']
        }));
        ```
    """
    await websocket.accept()
    _connections.add(websocket)

    logger.info(f"WebSocket client connected. Total connections: {len(_connections)}")

    # Track subscribed event types
    subscribed_events: set[str] = set()

    try:
        # Send welcome message
        await websocket.send_json({
            "type": "connection",
            "message": "Connected to agent event stream",
            "timestamp": asyncio.get_event_loop().time(),
        })

        # Create event listener task
        event_task = asyncio.create_task(_stream_events(websocket, subscribed_events))

        # Handle incoming messages
        while True:
            try:
                # Receive messages from client
                data = await websocket.receive_text()
                message = json.loads(data)

                # Handle subscribe action
                if message.get("action") == "subscribe":
                    event_types = message.get("event_types", [])
                    subscribed_events.update(event_types)

                    await websocket.send_json({
                        "type": "subscription",
                        "message": f"Subscribed to {len(event_types)} event types",
                        "subscribed_events": list(subscribed_events),
                    })

                # Handle unsubscribe action
                elif message.get("action") == "unsubscribe":
                    event_types = message.get("event_types", [])
                    subscribed_events.difference_update(event_types)

                    await websocket.send_json({
                        "type": "subscription",
                        "message": f"Unsubscribed from {len(event_types)} event types",
                        "subscribed_events": list(subscribed_events),
                    })

                # Handle ping
                elif message.get("action") == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": asyncio.get_event_loop().time(),
                    })

            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON message",
                })
            except Exception as e:
                logger.error(f"Error processing WebSocket message: {e}")
                await websocket.send_json({
                    "type": "error",
                    "message": str(e),
                })

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        _connections.discard(websocket)
        event_task.cancel()
        logger.info(f"WebSocket client removed. Total connections: {len(_connections)}")


async def _stream_events(websocket: WebSocket, subscribed_events: set[str]):
    """Stream events to WebSocket client.

    Args:
        websocket: WebSocket connection
        subscribed_events: Set of event types client is subscribed to
    """
    while True:
        try:
            # In a real implementation, this would listen to the event bus
            # and forward events to the WebSocket client
            #
            # For now, send periodic heartbeat
            await asyncio.sleep(30)

            await websocket.send_json({
                "type": "heartbeat",
                "timestamp": asyncio.get_event_loop().time(),
                "subscribed_events": list(subscribed_events),
            })

        except WebSocketDisconnect:
            break
        except Exception as e:
            logger.error(f"Error streaming events: {e}")
            break


@router.websocket("/agents/{agent_id}")
async def websocket_agent(websocket: WebSocket, agent_id: str):
    """WebSocket endpoint for agent-specific updates.

    Subscribe to real-time updates for a specific agent.

    Example client usage:
        ```javascript
        const ws = new WebSocket('ws://localhost:8000/api/agents/ws/agents/engineer_001');

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log('Agent update:', data);
        };
        ```
    """
    await websocket.accept()

    logger.info(f"WebSocket client connected for agent: {agent_id}")

    try:
        await websocket.send_json({
            "type": "connection",
            "agent_id": agent_id,
            "message": f"Connected to agent {agent_id} event stream",
            "timestamp": asyncio.get_event_loop().time(),
        })

        # Stream agent-specific updates
        while True:
            # In real implementation, listen to agent events
            await asyncio.sleep(30)

            await websocket.send_json({
                "type": "heartbeat",
                "agent_id": agent_id,
                "timestamp": asyncio.get_event_loop().time(),
            })

    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected for agent: {agent_id}")
    except Exception as e:
        logger.error(f"WebSocket error for agent {agent_id}: {e}")


async def broadcast_event(event_type: str, payload: dict):
    """Broadcast event to all connected WebSocket clients.

    Args:
        event_type: Type of event
        payload: Event payload data
    """
    if not _connections:
        return

    message = {
        "type": "event",
        "event_type": event_type,
        "payload": payload,
        "timestamp": asyncio.get_event_loop().time(),
    }

    # Send to all connections (handle disconnections gracefully)
    disconnected = set()

    for connection in _connections:
        try:
            await connection.send_json(message)
        except Exception as e:
            logger.warning(f"Failed to send to WebSocket client: {e}")
            disconnected.add(connection)

    # Remove disconnected clients
    _connections.difference_update(disconnected)
