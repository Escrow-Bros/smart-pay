import reflex as rx

class GlobalState(rx.State):

    """The global state for the SmartPay application."""

    user_mode: bool = True

    current_user: str | None = None

    job_description: str = ""

    uploaded_image: str = ""

    client_uploaded_images: list[str] = []

    @rx.var

    def mode_label(self) -> str:

        """Returns the string representation of the current mode."""

        return "Client Mode" if self.user_mode else "Worker Mode"

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

    def create_job(self):

        """Handles the creation of a new job."""

        print(f"Creating job: {self.job_description}")

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

