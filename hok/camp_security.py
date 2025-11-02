# hok/camp_security.py
import asyncio
import secrets
import orjson as json
from typing import List, Optional
from rich.progress import Progress, BarColumn, TextColumn

from hok.cache_manager import cache_manager
from hok.downloader import ensure_executable_exists, get_short_executable_path

class SecurityManager:
    """
    Manages the generation of dynamic security headers required by the HOK API.
    Lazily starts a background process to generate new parameters only when
    the persistent cache is exhausted.
    """
    _instance = None
    _proc: Optional[asyncio.subprocess.Process] = None
    _executable_path: Optional[str] = None
    _warmup_task: Optional[asyncio.Task] = None


    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SecurityManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, cluster_size: int = 2, pool_target: int = 100, low_water_mark: int = 20):
        if not hasattr(self, '_initialized'):
            self.cluster_size = cluster_size
            self.pool_target = pool_target
            self.low_water_mark = low_water_mark
            self._lock = asyncio.Lock()
            self._comm_lock = asyncio.Lock()
            self._is_warming_up = False
            self._initialized = True

    @staticmethod
    def _generate_traceparent() -> str:
        """Generates a W3C standard traceparent header."""
        trace_id = secrets.token_hex(16)
        span_id = secrets.token_hex(8)
        return f"00-{trace_id}-{span_id}-01"

    async def _start_daemon(self):
        """Starts the camp-security script as a long-lived daemon process."""
        async with self._lock:
            if self._proc and self._proc.returncode is None:
                return # Already running

            if not self._executable_path:
                self.__class__._executable_path = await ensure_executable_exists()

            print(f"🚀 Starting security daemon...")
            try:
                self._proc = await asyncio.create_subprocess_exec(
                    self._executable_path, 'server',
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                ready_signal = await self._proc.stdout.readline()
                if ready_signal.decode().strip() != "READY":
                    stderr = await self._proc.stderr.read()
                    raise RuntimeError(f"Daemon failed to start: {stderr.decode()}")
                print("✅ Security daemon is ready.")
            except Exception as e:
                self._proc = None
                raise RuntimeError(f"❌ Failed to create subprocess for camp-security: {e}")

    async def _fetch_new_params_from_daemon(self) -> List[str]:
        """
        Ensures the daemon is running and communicates with it to fetch new parameters.
        """
        async with self._comm_lock:
            if not self._proc or self._proc.returncode is not None:
                await self._start_daemon()

            try:
                command = f"cluster {self.cluster_size}\n"
                self._proc.stdin.write(command.encode())
                await self._proc.stdin.drain()

                output_line = await self._proc.stdout.readline()
                if not output_line:
                    stderr = await self._proc.stderr.read()
                    raise RuntimeError(f"Daemon closed pipe unexpectedly. Stderr: {stderr.decode().strip()}")

                # This avoids a potential decoding error if the output isn't perfect UTF-8
                json_start = output_line.find(b'[')
                if json_start == -1:
                    raise ValueError(f"Could not find JSON in daemon output: {output_line.decode()}")

                return json.loads(output_line[json_start:])
            except (BrokenPipeError, ConnectionResetError, RuntimeError, ValueError) as e:
                print(f"⚠️ Error communicating with daemon: {e}. Attempting restart on next call.")
                if self._proc:
                    try: self._proc.kill(); await self._proc.wait()
                    except ProcessLookupError: pass
                self._proc = None
                raise

    async def prime_daemon(self, warm_up: bool = False):
        """
        Optional: Explicitly starts the daemon ahead of time.
        """
        await self._start_daemon()
        if warm_up:
            self.trigger_warmup()

    def trigger_warmup(self):
        """Creates a background task to warm up the pool if one isn't already running."""
        if self._warmup_task and not self._warmup_task.done():
            return
        self._warmup_task = asyncio.create_task(self.warm_up_pool())

    async def warm_up_pool(self):
        """Warms up the parameter pool with a visual progress bar."""
        if self._is_warming_up: return
        self._is_warming_up = True

        try:
            with Progress(
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("({task.completed}/{task.total})")
            ) as progress:

                initial_uses = await cache_manager.get_available_param_uses_count()
                task = progress.add_task(
                    "[yellow]Replenishing parameter pool...",
                    total=self.pool_target,
                    completed=min(initial_uses, self.pool_target)
                )

                while not progress.finished:
                    try:
                        new_params = await self._fetch_new_params_from_daemon()
                        if new_params:
                            await cache_manager.add_new_params(new_params)
                            progress.update(task, advance=len(new_params) * 2)
                    except (RuntimeError, ValueError) as e:
                        progress.console.print(f"⚠️ [yellow]Warm-up error: {e}. Retrying in 5s...[/yellow]")
                        await asyncio.sleep(5)
                progress.update(task, description="[green]Parameter pool is full!")
        finally:
            self._is_warming_up = False

    async def get_headers(self) -> dict[str, str]:
        """
        Provides required dynamic headers.
        """
        param = await cache_manager.get_and_update_available_param()

        if not param:
            print("⚠️ Emergency fetch: Pool empty. Fetching a new batch...")
            new_params = await self._fetch_new_params_from_daemon()
            if not new_params:
                raise RuntimeError("❌ Failed to replenish parameter pool during emergency.")
            await cache_manager.add_new_params(new_params)
            param = await cache_manager.get_and_update_available_param()
            if not param:
                raise RuntimeError("❌ Failed to get a parameter even after emergency replenishment.")

        available_uses = await cache_manager.get_available_param_uses_count()
        if available_uses < self.low_water_mark and not self._is_warming_up:
            if self._proc and self._proc.returncode is None:
                print(f"📉 Parameter pool is low ({available_uses} uses). Triggering background refill.")
                self.trigger_warmup()

        return {
            "specialencodeparam": param,
            "traceparent": self._generate_traceparent(),
        }

    async def close(self):
        """Terminates the background daemon process if it was started."""
        if self._warmup_task and not self._warmup_task.done():
            self._warmup_task.cancel()
            try: await self._warmup_task
            except asyncio.CancelledError: pass

        if self._proc and self._proc.returncode is None:
            print("🌙 Closing security daemon...")
            try:
                self._proc.terminate()
                await asyncio.wait_for(self._proc.wait(), timeout=3.0)
                print("✅ Daemon closed.")
            except asyncio.TimeoutError:
                self._proc.kill()
                await self._proc.wait()
            except ProcessLookupError:
                pass
        self._proc = None

# Singleton instance
security_manager = SecurityManager()
