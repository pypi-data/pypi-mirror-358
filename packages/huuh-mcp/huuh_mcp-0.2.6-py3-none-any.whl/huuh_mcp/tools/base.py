"""Base management MCP tools."""
import logging
from typing import Dict, Any

from fastmcp import Context

from ..huuh.auth import auth_client
from ..huuh.client import api_client

logger = logging.getLogger(__name__)


async def create_base(
        base_name: str,
        base_description: str,
        ctx: Context = None
) -> Dict[str, Any]:
    """
    Create a new base for a user.

    Args:
        base_name: Name of the base
        base_description: Description of the base

    Returns:
        A dictionary containing the result of the base creation.
    """
    logger.info(f"create_base called with  base_name='{base_name}'")

    try:
        await ctx.info(f"Creating base '{base_name}'...")
        await ctx.report_progress(0, 3)

        # Authenticate
        valid = await auth_client.validate_token()
        if not valid:
            await ctx.error("Authentication failed")
            return {"error": "Authentication failed. Please check your credentials."}

        # Validate inputs
        if not base_name or not base_description:
            await ctx.error(
                "Missing required parameters: user_id, base_name, and base_description must be provided.")
            return {
                "error": "Missing required parameters: user_id, base_name, and base_description must be provided."}

        await ctx.report_progress(1, 3)

        try:
            data = {
                "course_name": base_name,
                "course_description": base_description
            }
            headers = {"Content-Type": "application/json"}
            response = await api_client.request(
                method="POST",
                endpoint="/mcp/create_course",
                json=data,
                headers=headers
            )

            await ctx.report_progress(3, 3)
            await ctx.info("Base created successfully")

            return response
        except ValueError as e:
            await ctx.error(f"Error creating base: {str(e)}")
            return {"error": f"Error creating base: {str(e)}"}
    except Exception as e:
        logger.exception("Unexpected error in create_base")
        await ctx.error("An unexpected error occurred")
        return {"error": f"An unexpected error occurred: {str(e)}"}


async def assign_base_to_space(
        space_id: str,
        base_id: str,
        ctx: Context = None
) -> Dict[str, Any]:
    """
    Assign a base to a space.

    Args:
        space_id: ID of the space to assign the base to
        base_id: ID of the base to assign

    Returns:
        A dictionary containing the result of the assignment.
    """
    logger.info(f"assign_base_to_space called with space_id='{space_id}', base_id='{base_id}'")

    try:
        await ctx.info(f"Assigning base '{base_id}' to space '{space_id}'...")
        await ctx.report_progress(0, 3)

        # Authenticate
        valid = await auth_client.validate_token()
        if not valid:
            await ctx.error("Authentication failed")
            return {"error": "Authentication failed. Please check your credentials."}

        # Validate inputs
        if not space_id or not base_id:
            await ctx.error(
                "Missing required parameters: space_id and base_id must be provided.")
            return {
                "error": "Missing required parameters: space_id and base_id must be provided."}

        await ctx.report_progress(1, 3)

        try:
            data = {
                "space_id": space_id,
                "base_id": base_id
            }
            headers = {"Content-Type": "application/json"}
            response = await api_client.request(
                method="POST",
                endpoint="/mcp/assign_base_to_space",
                json=data,
                headers=headers
            )

            await ctx.report_progress(3, 3)
            await ctx.info("Base assigned to space successfully")

            return response
        except ValueError as e:
            await ctx.error(f"Error assigning base to space: {str(e)}")
            return {"error": f"Error assigning base to space: {str(e)}"}
    except Exception as e:
        logger.exception("Unexpected error in assign_base_to_space")
        await ctx.error("An unexpected error occurred")
        return {"error": f"An unexpected error occurred: {str(e)}"}
