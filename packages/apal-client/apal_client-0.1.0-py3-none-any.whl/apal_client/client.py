import httpx
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import UUID
import os
from apal_client.exceptions import (
    APALError,
    ValidationError,
    AuthenticationError,
    MessageError,
    APIError
)

class APALClient:
    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or os.getenv("APAL_API_KEY")
        self.email = email or os.getenv("APAL_EMAIL")
        self.password = password or os.getenv("APAL_PASSWORD")
        self.access_token = None
        self.client = httpx.AsyncClient(base_url=base_url)
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
        
    async def close(self):
        await self.client.aclose()
        
    async def authenticate(self) -> None:
        """Authenticate with the API using email and password"""
        if not self.email or not self.password:
            raise AuthenticationError("Email and password are required for authentication")
            
        try:
            response = await self.client.post(
                "/auth/token",
                data={"username": self.email, "password": self.password}
            )
            response.raise_for_status()
            data = response.json()
            self.access_token = data["access_token"]
            self.client.headers["Authorization"] = f"Bearer {self.access_token}"
        except httpx.HTTPError as e:
            raise AuthenticationError(f"Authentication failed: {str(e)}")
            
    async def register(
        self,
        email: str,
        password: str,
        business_name: str
    ) -> Dict[str, Any]:
        """Register a new business account"""
        try:
            # import pdb; pdb.set_trace()
            response = await self.client.post(
                "/auth/register",
                json={
                    "email": email,
                    "password": password,
                    "business_name": business_name
                }
            )
            # pdb.set_trace()
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            if e.response is not None:
                try:
                    error_detail = e.response.json()
                    raise APIError(e.response.status_code, f"Registration failed: {error_detail}")
                except json.JSONDecodeError:
                    raise APIError(e.response.status_code, f"Registration failed: {e.response.text}")
            raise APIError(500, f"Registration failed: {str(e)}")
            
    async def send_message(
        self,
        receiver_id: UUID,
        content: Dict[str, Any],
        message_type: str = "notification"
    ) -> Dict[str, Any]:
        """Send a message to another business"""
        if not self.access_token:
            await self.authenticate()
            
        try:
            # Get current user info to get sender_id
            response = await self.client.get("/auth/me")
            response.raise_for_status()
            current_user = response.json()
            
            # Prepare message data
            message_data = {
                "sender_id": current_user["id"],
                "receiver_id": str(receiver_id),
                "content": content,
                "message_type": message_type
            }
            
            # Send message
            response = await self.client.post(
                "/messages/send",
                json=message_data
            )
            
            if response.status_code == 400:
                try:
                    error_detail = response.json()
                    raise MessageError(f"Failed to send message: {error_detail}")
                except json.JSONDecodeError:
                    raise MessageError(f"Failed to send message: {response.text}")
                    
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            if e.response is not None:
                try:
                    error_detail = e.response.json()
                    raise MessageError(f"Failed to send message: {error_detail}")
                except json.JSONDecodeError:
                    raise MessageError(f"Failed to send message: {e.response.text}")
            raise MessageError(f"Failed to send message: {str(e)}")
            
    async def receive_message(self, message_id: UUID) -> Dict[str, Any]:
        """Receive a specific message"""
        if not self.access_token:
            await self.authenticate()
            
        try:
            response = await self.client.get(f"/messages/receive/{message_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise MessageError(f"Failed to receive message: {str(e)}")
            
    async def list_messages(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """List all messages for the authenticated business"""
        if not self.access_token:
            await self.authenticate()
            
        try:
            response = await self.client.get(
                "/messages/list",
                params={"skip": skip, "limit": limit}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise MessageError(f"Failed to list messages: {str(e)}")
            
    async def get_message_status(self, message_id: UUID) -> Dict[str, Any]:
        """Get the status of a specific message"""
        if not self.access_token:
            await self.authenticate()
            
        try:
            response = await self.client.get(f"/messages/status/{message_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise MessageError(f"Failed to get message status: {str(e)}")
            
    async def refresh_api_key(self) -> Dict[str, Any]:
        """Refresh the API key for the authenticated business"""
        if not self.access_token:
            await self.authenticate()
            
        try:
            response = await self.client.post("/auth/refresh-api-key")
            response.raise_for_status()
            data = response.json()
            self.api_key = data["api_key"]
            return data
        except httpx.HTTPError as e:
            raise APIError(e.response.status_code, str(e)) 