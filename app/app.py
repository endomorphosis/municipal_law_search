#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
The FastAPI application that serves as an API for accessing American law documents.
"""
from __future__ import annotations
import __main__

from dotenv import load_dotenv
import json
from enum import StrEnum
from pathlib import Path
import sys
import traceback
from typing import Any, Callable, Optional, Union
from types import ModuleType
import logging

import smtplib
import ssl
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr, quote


from fastapi import Depends, FastAPI, HTTPException, Query, Request, File, UploadFile
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
import uvicorn


from configs import Configs, configs as project_configs
from logger import logger as module_logger


import paths.search as search
import paths.search_history as search_history
from schemas import LawItem
from schemas import ErrorResponse

from utils import get_html_db
from llm import AsyncLLMInterface, LLM
from app.read_only_database import Database, READ_ONLY_DB

# Load environment variables
load_dotenv()

import email
import ssl
import smtplib

from functools import cached_property
from pydantic import BaseModel, computed_field, PrivateAttr
import mimetypes
import magic


class Routes(StrEnum):
    BASE = "/"
    STATIC_FILES = "/src"
    FAVICON = "/favicon.ico"
    PUBLIC_FILES = "/public/{filename:path}"
    SIDE_MENU_FILES = "/side-menu/{filename:path}"
    SEARCH_SSE = "/api/search/sse"
    GET_LAW = "/api/law/{cid}"
    TALK_WITH_THE_LAW = "/api/talk_with_the_law"
    SEARCH_HISTORY = "/api/search-history"
    BLUEBOOK_CITATIONS = "/api/bluebook-citations"
    ACCOUNT_CREATE = "/api/account/create"
    ACCOUNT_DELETE = "/api/account/delete"
    ACCOUNT_PAGE = "/api/account/{account_id}"
    CONTACT = "/api/contact"
    CHROME_DEVTOOLS = "/.well-known/appspecific/com.chrome.devtools.json"
    UPLOAD_DOCUMENT = "/api/upload-document"


class Contact(StrEnum):
    GENERAL = "General Inquiry"
    SUPPORT = "Technical Support"
    FEEDBACK = "Feedback"
    PARTNER = "Partnership Opportunity"
    DATA = "Data Request"
    OTHER = "Other"


def _determine_mime_type(path_or_bytes: str | bytes | None) -> Optional[str]:
    """Determine the MIME type of a file.
    NOTE: Lifted from Omni-Converter Mk2 Repo
    
    Args:
        file_path: The path to the file.
        
    Returns:
        str: The MIME type of the file.
    """
    match path_or_bytes:
        case str():
            try:
                mime_type = magic.from_file(path_or_bytes, mime=True)
                # If magic returns generic type but extension suggests specific type, use mimetypes
                if mime_type == 'application/octet-stream':
                    guessed_type = mimetypes.guess_type(path_or_bytes)[0]
                    if guessed_type:
                        return guessed_type
                return mime_type
            except Exception:
                return mimetypes.guess_type(path_or_bytes)[0] or 'application/octet-stream'
        case bytes():
            try:
                return magic.from_buffer(path_or_bytes, mime=True)
            except (ImportError, Exception):
                return 'application/octet-stream'
        case _:
            return None



class Document(BaseModel):
    file: bytes

    _file_mime_type: str = PrivateAttr(default=None)
    _text_content: Optional[str] = PrivateAttr(default=None)
    _encoding: str = PrivateAttr(default='utf-8')

    @computed_field # type: ignore[prop-decorator]
    @property
    def text_content(self) -> str:
        """The text content of the file."""
        if self._text_content is None:
            try:
                self.text_content = self.file.decode(self._encoding)
            except UnicodeDecodeError as e:
                self.text_content = ''
        return self._text_content

    @computed_field # type: ignore[prop-decorator]
    @property
    def file_mime_type(self) -> str:
        """The MIME type of the file."""
        if self._file_mime_type is None:
            try:
                self._file_mime_type = _determine_mime_type(self.file)
            except (ImportError, Exception):
                self._file_mime_type = 'application/octet-stream'
        return self._file_mime_type


class Dictate:

    def __init__(self, *, 
                 configs: Configs = None, 
                 resources: dict[str, Any] = None
                ) -> None:
        self.configs = configs
        self.resources = resources

        self.llm: AsyncLLMInterface = resources['llm']

    def transcribe_audio(self, audio_file: bytes) -> str:
        """
        Transcribe an audio file to text using a speech-to-text model.
        """

class VoiceMode:

    def __init__(self, *, 
                 configs: Configs = None, 
                 resources: dict[str, Any] = None
                ) -> None:
        self.configs = configs
        self.resources = resources


class UploadMenu:

    def __init__(self, *, 
                 configs: Configs = None, 
                 resources: dict[str, Any] = None
                ) -> None:
        self.configs = configs
        self.resources = resources

    def add_photos_and_files(self, *args, **kwargs) -> None:
        """Upload photos and files from local device."""
        pass

    def add_from_google_drive(self, *args, **kwargs) -> None:
        """Upload photos and files from Google Drive."""
        pass

    def agent_mode(self, *args, **kwargs) -> None:
        """Let an AI agent perform a task autonomously."""
        pass

    def deep_research(self, *args, **kwargs) -> None:
        pass

    def connectors(self, *args, **kwargs) -> None:
        """Connect to third-party services like Dropbox, Google Drive, OneDrive, etc."""
        pass

    def web_search(self, *args, **kwargs) -> None:
        """Search the web for information."""
        pass


class SideMenu:
    def __init__(self, *, 
                 configs: Configs = None, 
                 resources: dict[str, Any] = None
                ) -> None:
        self.configs = configs
        self.resources = resources


class App:
    """
    The main application class that encapsulates the FastAPI app and its resources.

    This class is responsible for initializing and configuring the FastAPI application,
    managing shared resources like database connections and language models, and
    defining the API routes and their corresponding handler functions.

    Attributes:
        configs (Configs): Application configuration object.
        resources (dict): Dictionary of shared application resources.
        routes (Routes): Enum of application routes.
        db (Database): The read-only database instance.
        llm (AsyncLLMInterface): The language model interface instance.
        logger (logging.Logger): The application logger.
        fastapi (FastAPI): The FastAPI application instance.
        email (module): The email module.
        templates (Jinja2Templates): Jinja2 templates engine.
        side_menu (SideMenu): The side menu handler.
        upload_menu (UploadMenu): The upload menu handler.
        search_function (Callable): The function used for performing searches.
        frontend_path (Path): Path to the frontend source directory.
        static_file_dir (Path): Path to the static files directory.
        templates_path (Path): Path to the templates directory.
        favicon_path (Path): Path to the favicon file.
        index_name (str): The name of the index HTML file.

    Public Methods:
        get_app(): Configures and returns the FastAPI application instance.
        favicon(): Serves the favicon.ico file.
        serve_index(request): Serves the main index.html page.
        serve_public_files(filename): Serves files from the public directory.
        serve_side_menu_files(filename): Serves HTML files for the side menu.
        upload_document(file, client_cid): Handles document uploads.
        search_sse_response(q, page, per_page, client_id): Provides search results via SSE.
        get_law(cid): Retrieves a legal document by its CID.
        talk_with_the_law(q, page, per_page, client_id): Interacts with the law via natural language.
        contact(name, email, message, subject, organization): Handles contact form submissions.
        account_create(): Placeholder for account creation.
        account_delete(): Placeholder for account deletion.
        account_page(): Placeholder for account page.
    """
    TITLE = "American Law API"
    DESCRIPTION = "API for accessing American law database"


    def __init__(self, *, 
                 configs: Configs = None, 
                 resources: dict[str, Any] = None
                ) -> None:
        self.configs = configs
        self.resources = resources

        self.routes:          Routes            = Routes
        self.db:              Database          = resources['db'] # NOTE These classes are instantiated already.
        self.llm:             AsyncLLMInterface = resources['llm']
        self.logger:          logging.Logger    = resources['logger']
        self.fastapi:         FastAPI           = resources['fastapi']
        self.email:           email             = resources['email']
        self.templates:       Jinja2Templates   = resources['Jinja2Templates']
        self.side_menu:       SideMenu          = None # TODO implement side menu class
        self.upload_menu:     UploadMenu        = None # TODO implement upload menu class
        self.search_function: Callable          = resources['search_function']

        # Contact form email settings
        self._email_address: str = configs.ADMIN_EMAIL
        self._smtp_server: str = configs.EMAIL_SERVER
        self._smtp_port: int = configs.EMAIL_PORT
        self._smtp_username: str = configs.EMAIL_USERNAME
        self._smtp_password: str = configs.EMAIL_PASSWORD

        # Paths
        # TODO move to configs.py

        self.frontend_path    = configs.ROOT_DIR / 'src'
        self.static_file_dir  = self.frontend_path / 'static'
        self.templates_path   = self.frontend_path / 'templates'
        self.favicon_path     = self.static_file_dir / 'images' / 'favicon' / 'favicon.ico'
        self.index_name       = "index.html"

        self.templates = self.templates(directory=self.templates_path)


    @property
    def get_mappings(self) -> dict[Routes, tuple[Callable, dict[str, Any]]]:
        """
        Mappings for GET requests.
        
        Returns:
            dict: A dictionary mapping routes to handler functions and parameters.
        """
        mappings = {
            self.routes.BASE:                (self.serve_index, {"response_class": HTMLResponse, "include_in_schema": True}),
            self.routes.FAVICON:             (self.favicon, {"include_in_schema": False}),
            self.routes.PUBLIC_FILES:        (self.serve_public_files, {"include_in_schema": True}),
            self.routes.SIDE_MENU_FILES:     (self.serve_side_menu_files, {"include_in_schema": True}),
            self.routes.SEARCH_SSE:          (self.search_sse_response, {"include_in_schema": True}),
            # self.routes.TALK_WITH_THE_LAW: (talk_with_the_law, {"include_in_schema": True}),
            self.routes.GET_LAW:             (self.get_law, {"include_in_schema": True}),
            # self.routes.SEARCH_HISTORY:    (get_search_history, {"include_in_schema": True}),
        }
        return mappings

    @property
    def put_mappings(self):
        mappings = {}
        return mappings

    @property
    def delete_mappings(self):
        mappings = {}
        return mappings

    @property
    def post_mappings(self):
        mappings = {
            self.routes.TALK_WITH_THE_LAW: (self.talk_with_the_law, {"include_in_schema": True}),
            self.routes.CONTACT:           (self.contact, {"include_in_schema": True}),
        }
        return mappings

    @property
    def email_address(self):
        return self._email_address

    @property
    def index(self) -> str:
        return self.index_name

    async def favicon(self) -> FileResponse:
        """Serve the site favicon.ico file.
        
        This endpoint serves the favicon.ico file from the static images directory.
        It is marked as not included in the schema documentation.
        
        Returns:
            FileResponse: The favicon.ico file
        """
        # NOTE This cannot be a property because FastAPI requires a callable for route handlers.
        return FileResponse(self.favicon_path)

    async def serve_index(self, request: Request) -> HTMLResponse:
        """Serve the main index page of the application.
        
        This endpoint renders the main HTML template for the application,
        which is the entry point for the user interface.
        
        Args:
            request: The incoming request object
            
        Returns:
            HTMLResponse: The rendered index.html template
        """
        return self.templates.TemplateResponse(self.index, {"request": request})

    async def serve_public_files(self, filename: str) -> FileResponse:
        """Serve static files from the public templates directory.
        
        This endpoint allows direct access to files in the templates directory
        via the /public/ URL path.
        
        Args:
            filename: The path of the file to serve
            
        Returns:
            FileResponse: The requested file
        """
        public_files_path = self.templates_path / filename
        return FileResponse(public_files_path)

    async def serve_side_menu_files(self, filename: str) -> HTMLResponse:
        """Serve HTML files from the side-menu templates directory.

        This endpoint serves HTML files from the side-menu subdirectory.
        Files include:
         - about.html
         - contact.html
         - ourteam.html
         - disclaimer.html

        Args:
            filename: The name of the file to serve from the side-menu directory

        Returns:
            HTMLResponse: The requested HTML file
        """
        side_menu_path = self.templates_path / 'side-menu' / filename
        return FileResponse(side_menu_path)

    async def upload_document(
        self,
        file: UploadFile,
        client_cid: Optional[str] = None
    ) -> JSONResponse:
        """
        API endpoint to handle document uploads from the frontend.

    This method processes document uploads from the JavaScript frontend's uploadDocument
    function. It integrates with the existing document processing pipeline to:
    - Validate uploaded file format and size constraints
    - Extract text content from PDF, DOC, DOCX, TXT files.
    - Generate content identifiers (CIDs) for document tracking
    - Store document metadata and content in the database
    - Optionally associate uploads with client sessions for history tracking

        Args:
            file (UploadFile): The uploaded file object from FastAPI's multipart form data.
                Supported formats are .pdf, .doc, .docx, and .txt files.
            client_id (str, optional): Client CID for associating uploads
                with user sessions and maintaining upload history. Defaults to None.

        Returns:
            JSONResponse: A JSON response containing the upload status and metadata.

            Response:
                - status (str): Upload result status, set to "success" if successful, otherwise "error"
                - message (str): Human-readable description of successful upload or error details.
                - cid (str): Content identifier for the uploaded document. Set to empty string if upload failed.
                - filename (str): Original filename of the uploaded document. Set to empty string if upload failed.
                - file_size (int): Size of the uploaded file in bytes. Set to 0 if upload failed.
                - error_code (str): Machine-readable error identifier. Set to empty string if status is "success".
                - upload_timestamp (str): ISO timestamp of when upload completed or error occurred.

        Raises:
            HTTPException: 400 error for invalid file types, oversized files, or corrupted uploads
            HTTPException: 413 error if file exceeds maximum allowed size
            HTTPException: 415 error for unsupported media types
            HTTPException: 500 error for internal processing failures
            ValueError: If file content cannot be extracted or processed, or client ID is not a valid CID
            TypeError: If file or client ID types are incorrect
            IOError: If file cannot be read or temporary storage fails

        Examples:
            Frontend JavaScript usage:
            ```javascript
            const formData = new FormData();
            formData.append("file", file);
            const response = await fetch("/api/upload-document", {
                method: "POST",
                body: formData,
            });
            ```
            Success response format:
            ```json
            {
                "status": "success",
                "message": "File uploaded successfully",
                "cid": "bafkreihvwc5kg3estvqpicmmqghwiriti6mz5w3lk4k3app3guwk6onrq4",
                "filename": "document.pdf",
                "file_size": 1048576,
                "upload_timestamp": "2025-09-26T10:30:00Z"
            }
            ```
            Error response format:
            ```json
            {
                "status": "error",
                "message": "Upload failed: Invalid file type",
                "error_code": "INVALID_FILE_TYPE"
            }
            ```
        """

    async def search_sse_response(
        self,
        q: str = Query("", description="Search query"),
        page: int = Query(1, description="Page number"),
        per_page: int = Query(20, description="Items per page"),
        client_id: str = None #Depends(search_history.get_or_create_client_id),
    ) -> EventSourceResponse:
        """Server-Sent Events endpoint that streams search results incrementally.

        This endpoint implements Server-Sent Events (SSE) to provide a streaming
        interface for search results. It allows the client to receive results
        incrementally as they become available, providing a more responsive user
        experience for searches that may take time to complete.

        The event stream includes:
        - A "search_started" event when the search begins
        - Multiple "results_update" events as results are found
        - A "search_complete" event when the search is finished
        - An "error" event if any errors occur during the search

        This endpoint also saves search queries to the user's search history.

        Args:
            q: The search query string
            page: The page number to retrieve
            per_page: The number of results per page
            client_id: Client identifier for search history tracking

        Returns:
            EventSourceResponse: A streaming response that sends events to the client
            
        Example:
            ```javascript
            // Client-side JavaScript
            const eventSource = new EventSource('/api/search/sse?q=zoning laws');
            eventSource.addEventListener('results_update', (event) => {
            const results = JSON.parse(event.data);
            // Update UI with results
            });
            ```
        """
        self._validate_query_params(q, page, per_page, client_id)

        async def _event_generator():
            try:
                # Initial event to indicate the search has started
                yield {
                    "event": "search_started",
                    "data": json.dumps({
                        "message": "Search started",
                        "query": q
                    })
                }

                # Include client_id for search history tracking
                async for result in self.search_function(q=q, page=page, per_page=per_page, client_id=client_id, logger=self.logger, llm=self.llm):
                    # Send each result chunk as it becomes available
                    yield {
                        "event": "results_update",
                        "data": json.dumps(result)
                    }

                # Final event to indicate the search is complete
                yield {
                    "event": "search_complete",
                    "data": json.dumps({
                        "message": "Search completed",
                        "query": q
                    })
                }

            except Exception as e:
                self.logger.error(f"Error in SSE stream: {e}")
                traceback.print_exc()
                # Send error event
                yield {
                    "event": "error",
                    "data": json.dumps({
                        "message": str(e)
                    })
                }

        return EventSourceResponse(_event_generator())

    async def get_law(self, cid: str) -> dict[str, Any]:
        """API endpoint to retrieve a specific legal document by its content ID.
        
        This endpoint retrieves a single legal document by its unique content ID (CID).
        It returns the complete document including metadata and HTML content.
        
        The algorithm:
        1. Connect to the HTML database in read-only mode
        2. Execute a SQL query joining the citations and HTML tables
        3. Filter by the provided CID
        4. Format the result as a LawItem response
        5. Close database resources
        6. Return the document or a 404 error if not found
        
        Args:
            cid: The content identifier of the legal document to retrieve
            
        Returns:
            LawItem: The legal document with metadata and HTML content
            
        Raises:
            HTTPException: 404 error if the document is not found
            
        Example:
            ```
            GET /api/law/bafkreihvwc5kg3estvqpicmmqghwiriti6mz5w3lk4k3app3guwk6onrq4
            ```
        """
        law = None
        html_conn = get_html_db(read_only=True)
        html_cursor = html_conn.cursor()
        try:
            html_cursor.execute('''
            SELECT *
            FROM citations c
            JOIN html h ON c.cid = h.cid
            WHERE c.cid = ?
            ''', (cid,))
            
            law: dict = html_cursor.fetchdf().to_dict('records')[0]
        finally:
            html_cursor.close()
            html_conn.close()
        self.logger.debug(f"law: {law}")

        if law is not None:
            return {
                'cid': law['cid'],
                'title': law['title'],
                'chapter': law['chapter'],
                'place_name': law['place_name'],
                'state_name': law['state_name'],
                'date': law['date'],
                'bluebook_citation': law['bluebook_citation'],
                'html': law['html']
            }
        else:
            raise HTTPException(status_code=404, detail="Law not found")

    async def talk_with_the_law(
        self,
        q: str = Query("", description="Search query"),
        page: int = Query(1, description="Page number"),
        per_page: int = Query(20, description="Items per page"),
        client_id: str = None, #Depends(search_history.get_or_create_client_id),
    ) -> JSONResponse:
        """API endpoint to interact with the law using a natural language query.

        This endpoint allows users to ask questions about the law and receive
        responses based on the underlying legal documents. It uses a language
        model to interpret the query and generate a response.

        Args:
            q (str): The natural language query string. Default is an empty string.
            page (int): The page number to retrieve. Default is 1.
            per_page (str): The number of results per page Default is 20.
            client_id (str, optional): Client identifier for search history tracking. Default is None.

        Returns:
            JSONResponse: The generated response from the language model

        Example:
            ```
            GET /api/talk_with_the_law?q=What are the zoning laws in California?
            ```
        """
        self._validate_query_params(q, page, per_page, client_id)
        response: dict = await self.llm.query_to_sql(q)
        return JSONResponse(content=response)

    async def contact(
        self,
        name: str,
        email: str,
        message: str,
        subject: StrEnum,
        organization: Optional[str] = None,
    ) -> JSONResponse:
        """
        API endpoint to submit a contact form.

        Args:
            name: Full name of the contact
            email: Email address of the contact
            message: Message content from the contact
            subject: Subject category from predefined enum
            organization: Optional organization name

        Returns:
            JSONResponse: Response indicating success/failure of form submission

        Raises:
            ValueError: If subject is not in valid Contact enum values
            ValidationError: If string inputs fail validation
        """
        # Validate subject first (fail fast)
        if subject not in Contact:
            raise ValueError(f"Invalid subject: {subject}. Must be one of {[s.value for s in Contact]}")

        # Validate string inputs
        string_validations = [
            (name, 'name', False), (email, 'email', False),  (message, 'message', False), (subject, 'subject', False), (organization, 'organization', True)
        ]
        cleaning_dict = {}

        for value, field_name, can_be_none in string_validations:
            self._validate_string(value, field_name, skip_if_value_is_none=can_be_none)
            # Quote the string to prevent injection attacks
            cleaning_dict[field_name] = f'"{quote(value.strip())}"' if value is not None else None

        name = cleaning_dict['name']
        email = cleaning_dict['email']
        message = cleaning_dict['message']
        subject = cleaning_dict['subject']
        organization = cleaning_dict.get('organization', None)

        # Construct subject line
        org_part = f" ({organization})" if organization else ""
        subject_line = f"{self.TITLE}[Form Submission] {subject.value} - {name}{org_part}"

        # Construct email body
        email_body = f"""
Subject: {subject.value}
Name: {name}
Organization: {organization or "N/A"}
Time: {datetime.now().astimezone().isoformat()}
Email: {email}

Message:
{message}
"""
        # Create email message
        msg = MIMEMultipart()
        msg['From'] = formataddr((name, email))
        msg['To'] = self.email_address
        msg['Subject'] = subject_line
        msg['Reply-To'] = email

        # Attach the body
        msg.attach(MIMEText(email_body.strip(), 'plain', 'utf-8'))
        error_tuple = None

        try:
            # Create SMTP connection with SSL
            context = ssl.create_default_context()

            with smtplib.SMTP(self._smtp_server, self._smtp_port) as server:
                server.starttls(context=context)
                server.login(self._smtp_username, self._smtp_password)

                # Send email
                server.send_message(msg)

            return JSONResponse({
                "status": "success", 
                "message": "Contact form submitted successfully"
            })

        except smtplib.SMTPAuthenticationError as e:
            error_tuple = (f"Authentication failed.", f"\n{e}", 500)
        except smtplib.SMTPRecipientsRefused as e:
            error_tuple = (f"Invalid recipient email address", f"\n{e}", 400)
        except smtplib.SMTPException as e:
            error_tuple = (f"Failed to send email.", f"\n{e}", 500)
        except ConnectionError as e:
            error_tuple = (f"Unable to connect to email server.", f"\n{e}", 503)
        except Exception as e:
            error_tuple = (f"An unexpected {type(e).__name__} error occurred.", f"\n{e}", 500)
        finally:
            if error_tuple is not None:
                if "unexpected" in error_tuple[0].lower():
                    self.logger.exception(f"Unexpected error sending contact form: {e}")
                else:
                    self.logger.error(f"Contact form error: {error_tuple[0]}{error_tuple[1]}") 
                return JSONResponse(
                    {"status": "error",
                     "message": error_tuple[0] + " Please try again later.\n" + error_tuple[1]},
                     status_code=error_tuple[2]
                )

    async def account_create(self):
        pass

    async def account_delete(self):
        pass

    async def account_page(self):
        pass

    @staticmethod
    def _validate_string(value: Any, var_name: str, skip_if_value_is_none: bool = False) -> None:
        if skip_if_value_is_none and value is None:
            return
        if not isinstance(value, str):
            raise TypeError(f"'{var_name}' must be an str, got {type(value).__name__} instead.")
        if not value.strip():
            raise ValueError(f"'{var_name}' must be a non-empty string, got {value}.")

    @staticmethod
    def _validate_integer(value: Any, var_name: str, skip_if_value_is_none: bool = False) -> None:
        if skip_if_value_is_none and value is None:
            return
        if not isinstance(value, int):
            raise TypeError(f"'{var_name}' must be an integer, got {type(value).__name__} instead.")
        if value < 1:
            raise ValueError(f"'{var_name}' must be a positive integer, got {value}.")


    def _validate_query_params(self, q: str, page: int, per_page: int, client_id: str) -> None:
        """Validate query parameters for search endpoints.
        
        This method checks the types and values of the query parameters
        to ensure they meet the expected criteria. It raises appropriate
        exceptions if any parameter is invalid.
        
        Args:
            q: The search query string
            page: The page number to retrieve
            per_page: The number of results per page
            client_id: Client identifier for search history tracking
            
        Raises:
            TypeError: If any parameter is of the wrong type
            ValueError: If any parameter has an invalid value
        """
        string_params = [(q, 'q'),(client_id, 'client_id')]
        integer_params = [(per_page, 'per_page'), (page, 'page')]

        for arg, name in string_params:
            self._validate_string(arg, name, skip_if_value_is_none=True)

        for arg, name in integer_params:
            self._validate_integer(arg, name)


    def _map_static_files(self, app: FastAPI) -> FastAPI:
        """Mount static files to the FastAPI app."""
        app.mount(
            self.routes.STATIC_FILES, 
            StaticFiles(directory=self.static_file_dir), 
            name=self.routes.STATIC_FILES.value.lstrip('/')
        )
        return app

    @staticmethod
    def _add_middleware(app: FastAPI) -> FastAPI:
        """Add middleware to the FastAPI app."""
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        return app

    def get_app(self) -> FastAPI:
        app = FastAPI(title=self.TITLE, description=self.DESCRIPTION)

        app = self._add_middleware(app)
        app = self._map_static_files(app)

        for route, (func, params) in self.get_mappings.items():
            if func is None:
                continue
            if not callable(func):
                raise TypeError(f"Function for route '{route}' is not callable.")
            app.get(route, **params)(func)

        return app


def get_upload_menu(mock_resources: Optional[dict] = None, mock_configs: Optional[BaseModel] = None) -> UploadMenu:
    configs = mock_configs or project_configs
    _resources = mock_resources or {}
    resources = {
        "db": _resources.pop('db', READ_ONLY_DB),
        "llm": _resources.pop("llm", LLM),
        "logger": _resources.pop("logger", module_logger),
        "fastapi": _resources.pop("fastapi", FastAPI),
        "email": _resources.pop("email", email),
    }
    upload_menu_instance = UploadMenu(configs=configs, resources=resources)
    return upload_menu_instance


def get_side_menu(mock_resources: Optional[dict] = None, mock_configs: Optional[BaseModel] = None) -> SideMenu:
    configs = mock_configs or project_configs
    _resources = mock_resources or {}
    resources = {
        "db": _resources.pop('db', READ_ONLY_DB),
        "llm": _resources.pop("llm", LLM),
        "logger": _resources.pop("logger", module_logger),
        "fastapi": _resources.pop("fastapi", FastAPI),
        "email": _resources.pop("email", email),
    }
    side_menu_instance = SideMenu(configs=configs, resources=resources)
    return side_menu_instance


def get_app(mock_resources: Optional[dict] = None, mock_configs: Optional[BaseModel] = None) -> FastAPI:
    configs = mock_configs or project_configs
    _resources = mock_resources or {}
    resources = {
        "db": _resources.pop('db', READ_ONLY_DB),
        "llm": _resources.pop("llm", LLM),
        "logger": _resources.pop("logger", module_logger),
        "fastapi": _resources.pop("fastapi", FastAPI),
        "Jinja2Templates": _resources.pop("Jinja2Templates", Jinja2Templates),
        "email": _resources.pop("email", email),
        "side_menu": _resources.pop("side_menu", get_side_menu()),
        "upload_menu": _resources.pop("upload_menu", get_upload_menu()),
        "search_function": _resources.pop("search_function", search.function),
    }
    app_instance = App(configs=configs, resources=resources)
    return app_instance.get_app()


# Set up the FastAPI app
app = get_app()


if __name__ == '__main__':
    try:
        uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)
    finally:
        if READ_ONLY_DB is not None:
            READ_ONLY_DB.exit()
        module_logger.info("Server stopped.")
        sys.exit(0)