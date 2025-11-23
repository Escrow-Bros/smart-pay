import reflex as rx
import httpx
import asyncio
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Backend API configuration
API_BASE_URL = "http://localhost:8000"

# Wallet addresses from .env
CLIENT_ADDR = os.getenv("CLIENT_ADDR", "")
WORKER_ADDR = os.getenv("WORKER_ADDR", "")

class GlobalState(rx.State):

    """The global state for the GigShield application."""

    # Landing page state
    show_landing: bool = True
    
    user_mode: bool = True
    
    # Navigation state
    current_view: str = "create"  # "create", "jobs", "wallet"

    current_user: str | None = None
    
    # Wallet address (full address)
    wallet_address: str = ""

    job_description: str = ""

    uploaded_image: str = ""

    client_uploaded_images: list[str] = []
    
    # Wallet state
    wallet_balance: float = 0.0
    is_loading_balance: bool = False
    
    # Job state
    available_jobs: list[dict] = []
    client_jobs: list[dict] = []
    worker_jobs: list[dict] = []
    current_job: Optional[dict] = None
    worker_stats: dict = {}
    is_loading_jobs: bool = False
    
    # Job creation state
    job_amount: float = 5.0
    is_creating_job: bool = False
    
    # IPFS URLs for uploaded images
    client_ipfs_urls: list[str] = []

    @rx.var

    def mode_label(self) -> str:

        """Returns the string representation of the current mode."""

        return "Client Mode" if self.user_mode else "Worker Mode"

    @rx.event
    async def select_role(self, is_client: bool):
        """Selects user role and navigates to app."""
        self.user_mode = is_client
        self.show_landing = False
        
        # Auto-connect wallet based on role
        if is_client:
            self.current_user = "Alice"
            self.wallet_address = CLIENT_ADDR
            print(f"🔵 CLIENT MODE - Address: {self.wallet_address}")
        else:
            self.current_user = "Bob"
            self.wallet_address = WORKER_ADDR
            print(f"🟢 WORKER MODE - Address: {self.wallet_address}")
        
        print(f"📍 Current User: {self.current_user}")
        print(f"📍 Wallet Address: {self.wallet_address}")
        
        # Fetch initial data (consume generators)
        async for _ in self.fetch_wallet_balance():
            pass
        if is_client:
            async for _ in self.fetch_client_jobs():
                pass
        else:
            async for _ in self.fetch_available_jobs():
                pass
            async for _ in self.fetch_worker_data():
                pass
        
        return rx.redirect("/app")

    @rx.event
    def navigate_to(self, view: str):
        """Navigate to a different view."""
        self.current_view = view
    
    @rx.event
    def copy_address(self):
        """Copy wallet address to clipboard."""
        return rx.set_clipboard(self.wallet_address)

    @rx.event

    def set_worker_mode(self, is_worker: bool):

        """Sets the user mode based on the worker toggle (True = Worker, False = Client)."""

        self.user_mode = not is_worker

    @rx.event

    def set_job_description(self, value: str):

        """Sets the job description."""

        self.job_description = value

    @rx.event

    def set_current_user(self, value: str):

        """Sets the currently connected wallet user."""

        self.current_user = value

    @rx.event
    def set_job_amount(self, value: str):
        """Sets the job amount in GAS."""
        try:
            self.job_amount = float(value)
        except ValueError:
            self.job_amount = 5.0

    @rx.event
    async def fetch_wallet_balance(self):
        """Fetch wallet balance from backend API."""
        if not self.wallet_address:
            print("❌ No wallet address set!")
            return
        
        print(f"🔄 Fetching balance for: {self.wallet_address}")
        self.is_loading_balance = True
        try:
            async with httpx.AsyncClient() as client:
                url = f"{API_BASE_URL}/api/wallet/balance/{self.wallet_address}"
                print(f"📡 API URL: {url}")
                response = await client.get(url, timeout=5.0)
                print(f"📥 Response Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    self.wallet_balance = data.get("balance", 0.0)
                    print(f"💰 Balance fetched: {self.wallet_balance} GAS")
                else:
                    print(f"❌ Failed to fetch balance: {response.text}")
        except Exception as e:
            print(f"❌ Error fetching balance: {e}")
            yield rx.toast.error("Failed to fetch wallet balance")
        finally:
            self.is_loading_balance = False

    @rx.event
    async def fetch_available_jobs(self):
        """Fetch available jobs from backend API."""
        self.is_loading_jobs = True
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{API_BASE_URL}/api/jobs/available",
                    timeout=5.0
                )
                if response.status_code == 200:
                    data = response.json()
                    self.available_jobs = data.get("jobs", [])
        except Exception as e:
            print(f"Error fetching jobs: {e}")
            yield rx.toast.error("Failed to fetch available jobs")
        finally:
            self.is_loading_jobs = False

    @rx.event
    async def fetch_client_jobs(self):
        """Fetch client's jobs from backend API."""
        if not self.wallet_address:
            return
        
        self.is_loading_jobs = True
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{API_BASE_URL}/api/jobs/client/{self.wallet_address}",
                    timeout=5.0
                )
                if response.status_code == 200:
                    data = response.json()
                    self.client_jobs = data.get("jobs", [])
        except Exception as e:
            print(f"Error fetching client jobs: {e}")
            yield rx.toast.error("Failed to fetch your jobs")
        finally:
            self.is_loading_jobs = False

    @rx.event
    async def fetch_worker_data(self):
        """Fetch worker's current job, history, and stats."""
        if not self.wallet_address:
            return
        
        self.is_loading_jobs = True
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{API_BASE_URL}/api/jobs/worker/{self.wallet_address}",
                    timeout=5.0
                )
                if response.status_code == 200:
                    data = response.json()
                    self.current_job = data.get("current_job")
                    self.worker_jobs = data.get("history", [])
                    self.worker_stats = data.get("stats", {})
        except Exception as e:
            print(f"Error fetching worker data: {e}")
            yield rx.toast.error("Failed to fetch worker data")
        finally:
            self.is_loading_jobs = False

    async def _upload_to_ipfs_helper(self, filename: str) -> Optional[str]:
        """Upload image to IPFS via backend API (helper method)."""
        try:
            upload_dir = rx.get_upload_dir()
            file_path = upload_dir / filename
            
            if not file_path.exists():
                return None
            
            async with httpx.AsyncClient() as client:
                with open(file_path, 'rb') as f:
                    files = {'file': (filename, f, 'image/jpeg')}
                    response = await client.post(
                        f"{API_BASE_URL}/api/upload/proof",
                        files=files,
                        timeout=30.0
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        return data.get("ipfs_url")
        except Exception as e:
            print(f"Error uploading to IPFS: {e}")
        
        return None

    @rx.event
    async def create_job(self):
        """Handles the creation of a new job via backend API."""
        if not self.current_user:
            yield rx.toast.error("Please connect wallet first")
            return
        
        if not self.job_description:
            yield rx.toast.error("Please enter job description")
            return
        
        if not self.client_uploaded_images:
            yield rx.toast.error("Please upload at least one reference photo")
            return
        
        self.is_creating_job = True
        yield rx.toast.info("Uploading images to IPFS...")
        
        try:
            # Upload all images to IPFS
            ipfs_urls = []
            for filename in self.client_uploaded_images:
                ipfs_url = await self._upload_to_ipfs_helper(filename)
                if ipfs_url:
                    ipfs_urls.append(ipfs_url)
                else:
                    yield rx.toast.warning(f"Failed to upload {filename}")
            
            if not ipfs_urls:
                yield rx.toast.error("Failed to upload images to IPFS")
                return
            
            self.client_ipfs_urls = ipfs_urls
            
            # Create job on blockchain + database
            yield rx.toast.info("Creating job on blockchain...")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{API_BASE_URL}/api/jobs/create",
                    json={
                        "client_address": self.current_user,
                        "description": self.job_description,
                        "reference_photos": ipfs_urls,
                        "amount": self.job_amount
                    },
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    yield rx.toast.success(f"Job created! ID: {data['job']['job_id']}")
                    
                    # Clear form
                    self.job_description = ""
                    self.client_uploaded_images = []
                    self.client_ipfs_urls = []
                    self.job_amount = 5.0
                    
                    # Refresh client jobs
                    await self.fetch_client_jobs()
                else:
                    error_data = response.json()
                    yield rx.toast.error(f"Failed to create job: {error_data.get('detail', 'Unknown error')}")
        
        except Exception as e:
            print(f"Error creating job: {e}")
            yield rx.toast.error(f"Error: {str(e)}")
        finally:
            self.is_creating_job = False

    @rx.event
    async def claim_job(self, job_id: int):
        """Worker claims an available job."""
        if not self.current_user:
            yield rx.toast.error("Please connect wallet first")
            return
        
        try:
            yield rx.toast.info("Claiming job...")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{API_BASE_URL}/api/jobs/assign",
                    json={
                        "job_id": job_id,
                        "worker_address": self.current_user
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    yield rx.toast.success("Job claimed successfully!")
                    
                    # Refresh worker data
                    await self.fetch_worker_data()
                    await self.fetch_available_jobs()
                else:
                    error_data = response.json()
                    yield rx.toast.error(f"Failed to claim job: {error_data.get('detail', 'Unknown error')}")
        
        except Exception as e:
            print(f"Error claiming job: {e}")
            yield rx.toast.error(f"Error: {str(e)}")

    @rx.event
    async def submit_proof(self, job_id: int):
        """Submit proof for current job."""
        if not self.uploaded_image:
            yield rx.toast.error("Please upload proof photo first")
            return
        
        try:
            yield rx.toast.info("Uploading proof to IPFS...")
            
            # Upload proof to IPFS
            ipfs_url = await self._upload_to_ipfs_helper(self.uploaded_image)
            if not ipfs_url:
                yield rx.toast.error("Failed to upload proof to IPFS")
                return
            
            # Submit proof for verification
            yield rx.toast.info("Submitting proof for AI verification...")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{API_BASE_URL}/api/jobs/submit",
                    json={
                        "job_id": job_id,
                        "proof_photos": [ipfs_url]
                    },
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        yield rx.toast.success("Work approved! Payment released 🎉")
                    else:
                        yield rx.toast.error(f"Work rejected: {data.get('message', 'Unknown reason')}")
                    
                    # Clear uploaded image
                    self.uploaded_image = ""
                    
                    # Refresh worker data
                    await self.fetch_worker_data()
                else:
                    error_data = response.json()
                    yield rx.toast.error(f"Failed to submit proof: {error_data.get('detail', 'Unknown error')}")
        
        except Exception as e:
            print(f"Error submitting proof: {e}")
            yield rx.toast.error(f"Error: {str(e)}")

    @rx.event
    async def start_polling(self):
        """Start polling for real-time updates (every 10 seconds)."""
        if self.wallet_address:
            async for _ in self.fetch_wallet_balance():
                pass
            
            if self.user_mode:  # Client mode
                async for _ in self.fetch_client_jobs():
                    pass
            else:  # Worker mode
                async for _ in self.fetch_worker_data():
                    pass
                async for _ in self.fetch_available_jobs():
                    pass

    @rx.event

    async def handle_upload(self, files: list[rx.UploadFile]):

        """Handle file upload for worker proof."""

        if not files:

            return

        upload_dir = rx.get_upload_dir()

        upload_dir.mkdir(parents=True, exist_ok=True)

        file = files[0]

        upload_data = await file.read()

        outfile = upload_dir / file.name

        with outfile.open("wb") as file_object:

            file_object.write(upload_data)

        self.uploaded_image = file.name

        yield rx.toast.success(f"Proof uploaded: {file.name}")

    @rx.event

    async def auto_upload_files(self, files: list[rx.UploadFile] = None):

        """Automatically trigger upload when files are selected or dropped."""

        # When on_drop is used with uploadFiles handler, files are already uploaded via XHR
        # We just need to track the filenames in our state

        if not files:

            return

        uploaded_files = []

        for file in files:

            try:

                # Get the filename from the uploaded file

                filename = file.name if hasattr(file, 'name') else str(file)

                if filename and filename not in self.client_uploaded_images:

                    self.client_uploaded_images.append(filename)

                    uploaded_files.append(filename)

            except Exception as e:

                print(f"Error processing file: {e}")

                continue

        # Update state to trigger reactivity

        if uploaded_files:

            self.client_uploaded_images = list(self.client_uploaded_images)

            # Clear selected files after upload

            yield rx.clear_selected_files("job_images_upload")

            if len(uploaded_files) == 1:

                yield rx.toast.success(f"Image uploaded: {uploaded_files[0]}")

            else:

                yield rx.toast.success(f"{len(uploaded_files)} images uploaded successfully")

    @rx.event

    async def handle_client_upload(self, files: list[rx.UploadFile]):

        """Handle file upload for client job images."""

        if not files:

            return

        upload_dir = rx.get_upload_dir()

        upload_dir.mkdir(parents=True, exist_ok=True)

        uploaded_files = []

        for file in files:

            upload_data = await file.read()

            outfile = upload_dir / file.name

            with outfile.open("wb") as file_object:

                file_object.write(upload_data)

            uploaded_files.append(file.name)

            # Add to the list if not already present

            if file.name not in self.client_uploaded_images:

                self.client_uploaded_images.append(file.name)

        # Create a new list to trigger reactivity

        self.client_uploaded_images = list(self.client_uploaded_images)

        # Clear selected files after upload

        yield rx.clear_selected_files("job_images_upload")

        if len(uploaded_files) == 1:

            yield rx.toast.success(f"Image uploaded: {uploaded_files[0]}")

        else:

            yield rx.toast.success(f"{len(uploaded_files)} images uploaded successfully")

    @rx.event

    def delete_client_image_by_index(self, index: int):

        """Delete an uploaded client image by index."""

        # Convert to list to work with index

        images_list = list(self.client_uploaded_images)

        if 0 <= index < len(images_list):

            filename = images_list[index]

            images_list.pop(index)

            # Update the state with the new list

            self.client_uploaded_images = images_list

            # Optionally delete the file from disk

            try:

                upload_dir = rx.get_upload_dir()

                file_path = upload_dir / filename

                if file_path.exists():

                    file_path.unlink()

            except Exception as e:

                print(f"Error deleting file {filename}: {e}")

            yield rx.toast.info(f"Image {filename} removed")

    @rx.event

    def delete_client_image(self, filename: str):

        """Delete an uploaded client image by filename."""

        if filename in self.client_uploaded_images:

            self.client_uploaded_images.remove(filename)

            # Create a new list to trigger reactivity

            self.client_uploaded_images = list(self.client_uploaded_images)

            # Optionally delete the file from disk

            try:

                upload_dir = rx.get_upload_dir()

                file_path = upload_dir / filename

                if file_path.exists():

                    file_path.unlink()

            except Exception as e:

                print(f"Error deleting file {filename}: {e}")

            yield rx.toast.info(f"Image {filename} removed")

