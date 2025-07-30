import asyncio
import json
import os
from typing import Dict
from uuid import uuid4
from fastapi import APIRouter, FastAPI
from fastapi.responses import JSONResponse
import httpx
import fcntl
from datetime import datetime, timezone


class RequestsJournal:
    def __init__(
        self,
        max_requests_journal_size: int = 1000,
        journal_file_path: str = "/tmp/requests.journal.jsonl",
    ):
        assert max_requests_journal_size > 0
        self.journal_file_path = journal_file_path
        self.max_requests_journal_size = max_requests_journal_size

    def _rotate_journal(self):
        if not os.path.exists(self.journal_file_path):
            return

        with open(self.journal_file_path + ".lock", "w") as lock_f:
            fcntl.lockf(lock_f, fcntl.LOCK_EX)

            # Safe to rotate now
            with open(self.journal_file_path, "r") as f:
                lines = f.readlines()

            if len(lines) > self.max_requests_journal_size:
                lines = lines[-self.max_requests_journal_size :]
                with open(self.journal_file_path, "w") as f:
                    f.writelines(lines)

            fcntl.lockf(lock_f, fcntl.LOCK_UN)

    def add_journalling(self, app: FastAPI):
        router = APIRouter()
        router.add_api_route("/requests", self.list_requests, methods=["GET"])
        router.add_api_route(
            "/requests/replay_last/{n}", self.replay_last_n, methods=["POST"]
        )

        app.include_router(router=router)

        @app.on_event("startup")
        async def start_flusher():
            asyncio.create_task(self._periodic_rotate_journal_file())

        @app.middleware("http")
        async def record_requests(request, call_next):
            # don't keep track of those requests
            if request.url.path.startswith("/requests") or request.url.path.startswith(
                "/info"
            ):
                return await call_next(request)

            body = await request.body()
            req_id = str(uuid4())

            record = {
                "method": request.method,
                "url": str(request.url),
                "path": request.url.path,
                "headers": dict(request.headers),
                "body": body.decode("utf-8", errors="ignore"),
            }

            # journal request before running it
            self._journal_request(req_id, record)
            response = await call_next(request)
            return response

    def _journal_request(self, req_id: str, record: Dict):
        now = datetime.now(timezone.utc).isoformat()
        entry = {"id": req_id, "req_date": now, **record}

        with open(self.journal_file_path, "a") as f:
            fcntl.lockf(f, fcntl.LOCK_EX)
            f.write(json.dumps(entry) + "\n")
            f.flush()
            fcntl.lockf(f, fcntl.LOCK_UN)

    async def _periodic_rotate_journal_file(self):
        while True:
            await asyncio.sleep(60)
            self._rotate_journal()

    def _read_journal_tail(self, n: int):
        if not os.path.exists(self.journal_file_path):
            return []
        with open(self.journal_file_path, "r") as f:
            lines = f.readlines()
            lines = lines[-n:]
            return [json.loads(line) for line in lines]

    async def list_requests(self):
        recent = self._read_journal_tail(self.max_requests_journal_size)
        return recent

    async def replay_last_n(self, n: int):
        if n > self.max_requests_journal_size:
            return JSONResponse(
                status_code=400,
                content={"error": f"Max is {self.max_requests_journal_size}"},
            )

        entries = self._read_journal_tail(n)
        responses = []

        async with httpx.AsyncClient() as client:
            for entry in entries:
                response = await client.request(
                    method=entry["method"],
                    url=entry["url"],
                    headers=entry["headers"],
                    content=entry["body"],
                )
                responses.append(
                    {
                        "status_code": response.status_code,
                        "url": entry["url"],
                        "body": response.text,
                        "request_id": entry["id"],
                    }
                )

        return responses
