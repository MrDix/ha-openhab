"""Data update coordinator for integration openHAB."""
from __future__ import annotations

from typing import Any
import asyncio
import aiohttp
import json
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.debounce import Debouncer

from .api import ApiClientException, OpenHABApiClient
from .const import DATA_COORDINATOR_UPDATE_INTERVAL, DOMAIN, LOGGER


class OpenHABDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, api: OpenHABApiClient) -> None:
        """Initialize."""
        self.api = api
        self.platforms: list[str] = []
        self.version: str = ""
        self.is_online = False
        self.ha_items = {}
        self._sse_listener_task = None
        self._stop_sse = False
        self._sse_session = None
        self._sse_started = False
        
        # Debouncer to prevent too many refreshes
        self._refresh_debouncer = Debouncer(
            hass,
            LOGGER,
            cooldown=0.5,  # Wait 0.5 seconds after last event before refreshing
            immediate=False,
            function=self._async_refresh_debounced,
        )

        super().__init__(
            hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=DATA_COORDINATOR_UPDATE_INTERVAL,
        )

    async def _async_refresh_debounced(self) -> None:
        """Debounced refresh function."""
        await self.async_request_refresh()

    def _start_sse_after_first_refresh(self) -> None:
        """Start SSE listener after first successful refresh."""
        if not self._sse_started and self.api._base_url:
            self._sse_started = True
            # Create task but don't await it - runs in background
            self._sse_listener_task = self.hass.async_create_background_task(
                self._listen_sse_events(),
                name="openhab_sse_listener"
            )
            LOGGER.info("SSE listener started for real-time updates")

    async def _listen_sse_events(self) -> None:
        """Listen to openHAB SSE events manually using aiohttp."""
        sse_url = f"{self.api._rest_url}/events"
        
        # Prepare headers
        headers = {}
        if self.api._auth_type == "token" and self.api._auth_token:
            headers["X-OPENHAB-TOKEN"] = self.api._auth_token
        
        retry_delay = 5
        
        while not self._stop_sse:
            try:
                # Create auth if using basic auth
                auth = None
                if self.api._auth_type == "OAuth2" and self.api._username:
                    auth = aiohttp.BasicAuth(self.api._username, self.api._password)
                
                # Create session if needed
                if not self._sse_session:
                    self._sse_session = aiohttp.ClientSession()
                
                LOGGER.debug("Connecting to SSE endpoint: %s", sse_url)
                
                async with self._sse_session.get(
                    sse_url,
                    headers=headers,
                    auth=auth,
                    timeout=aiohttp.ClientTimeout(total=None, sock_read=300)
                ) as response:
                    
                    if response.status != 200:
                        error_text = await response.text()
                        LOGGER.error(
                            "SSE connection failed with status %s: %s",
                            response.status,
                            error_text
                        )
                        await asyncio.sleep(retry_delay)
                        continue
                    
                    LOGGER.info("SSE connection established")
                    
                    # Read SSE stream line by line
                    event_data = {}
                    
                    async for line in response.content:
                        if self._stop_sse:
                            break
                        
                        try:
                            decoded = line.decode('utf-8').strip()
                            
                            if not decoded:
                                # Empty line marks end of event
                                if event_data:
                                    event_type = event_data.get('type', '')
                                    topic = event_data.get('topic', '')
                                    
                                    # Only log user-initiated commands (not periodic sensor updates)
                                    if event_type == 'ItemCommandEvent':
                                        LOGGER.debug("Command received: %s", topic)
                                    
                                    # Check if it's an item event (any type)
                                    if 'Item' in event_type and 'items/' in topic:
                                        # Use debouncer to batch ALL item updates into one refresh
                                        await self._refresh_debouncer.async_call()
                                    
                                    event_data = {}
                                continue
                            
                            # Parse SSE field
                            if ':' in decoded:
                                field, _, value = decoded.partition(':')
                                field = field.strip()
                                value = value.strip()
                                
                                if field == 'data':
                                    # Parse JSON data
                                    try:
                                        data = json.loads(value)
                                        event_data.update(data)
                                    except json.JSONDecodeError:
                                        pass
                                elif field == 'event':
                                    event_data['event'] = value
                                elif field == 'id':
                                    event_data['id'] = value
                        
                        except Exception as err:
                            LOGGER.debug("Error processing SSE line: %s", err)
            
            except asyncio.CancelledError:
                LOGGER.info("SSE listener cancelled")
                break
            
            except Exception as err:
                if not self._stop_sse:
                    LOGGER.warning(
                        "SSE connection error: %s (retrying in %s seconds)",
                        err,
                        retry_delay
                    )
                    await asyncio.sleep(retry_delay)
        
        LOGGER.info("SSE listener stopped")

    async def async_shutdown(self) -> None:
        """Shutdown the coordinator and stop SSE listener."""
        LOGGER.info("Shutting down openHAB coordinator")
        self._stop_sse = True
        
        # Cancel debouncer
        await self._refresh_debouncer.async_shutdown()
        
        # Cancel SSE listener task
        if self._sse_listener_task and not self._sse_listener_task.done():
            self._sse_listener_task.cancel()
            try:
                await self._sse_listener_task
            except asyncio.CancelledError:
                pass
        
        # Close session
        if self._sse_session:
            await self._sse_session.close()
            self._sse_session = None

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via library."""
        try:
            if self.version is None or len(self.version) == 0:
                self.version = await self.api.async_get_version()

            items = await self.api.async_get_items()
            self.is_online = bool(items)
            
            # Start SSE listener after first successful fetch
            if items and not self._sse_started:
                self._start_sse_after_first_refresh()
            
            return items

        except ApiClientException as exception:
            raise UpdateFailed(exception) from exception
