# bielik.ai
#Dwie opcje instalacji:
#1.setup.sh
#2.W folderze docker wpisac: docker-compose up --build
#Powinien zaciągnąć automatycznie wszystkie potrzebne paczki.
#Uruchamianie worker.py z argumentem gpt2 lub qwen, ładuje odpowiedni model.
#ALternatywnie można wyeksportować export MODEL_NAME=gpt2/qwen


#In case docker does not run, try refresh container:
#docker-compose down -v
##docker system prune -a # will require to redownload all libraries
#docker-compose up --build


########################################################################################################################
Jakby pierwsza opcja nie zadziałała, to następnie przejść do opcji drugiej (jeśli już docker się uruchamia)
zainstalować condę według instrukcji i wtedy spróbować uruchomic dockera a następnie publisher, result_consumer i worker 
w osobnych termilach. Można zalogować się do rabbit-mq i zobaczyć czy są jakieś kolejki.
Ważne, aby się upewnić czy cuda działa po instalacji, ja musiałem przeinstalowywać cuda 12.1 i pytorch.

Jeszzcze brakuje  automatycznej konfiguracji pracy w sieci. Trzeba będzie to jakoś dodać.
Setup.sh, póki co chyba jest niepotrzebny, trzeba będzie się zastanowić nad może jedną wersją instalacji, ale 
taką która działa w większości przypadków :).
#WORKS over network:) 

########################################################################################################################
# bielik.ai

A text generation service with multiple model options (GPT-2 or Qwen) using a RabbitMQ message queue architecture.

## System Overview

bielik.ai consists of:
- **RabbitMQ**: Message broker for task distribution (can be run via Docker or installed natively).
- **Worker**: Processes text generation tasks using supported models (can be run via Docker or directly on the host).
- **Publisher**: Sends tasks to the worker (can be run via Docker or directly on the host).
- **Result Consumer**: Retrieves and displays completed task results (can be run via Docker or directly on the host).

## Installation Options

### Option 1: Full Docker Installation (Recommended)

This method runs all components (RabbitMQ, Worker, Publisher, Consumer) in Docker containers.

1.  **Prerequisites**:
    *   [Docker](https://docs.docker.com/get-docker/)
    *   [Docker Compose](https://docs.docker.com/compose/install/)

2.  **Build and run the containers**:
    Navigate to the `docker` directory in your terminal.
    ```bash
    cd docker
    docker-compose up --build -d # Use -d to run in detached mode (background)
    ```
    *Note: The initial build might take some time.*

3.  **Selecting a model for the Worker**:
    You can choose which model the worker container uses by setting the `MODEL_NAME` environment variable in the `docker-compose.yml` file before building/running, or by setting it in your environment *before* running `docker-compose up`:
    ```bash
    export MODEL_NAME=gpt2  # or 'qwen'
    cd docker
    docker-compose up --build -d
    ```

4.  **Running Publisher/Consumer (within Docker - Optional):**
    If you want to run the publisher or consumer *within* the Docker network (e.g., for testing without host setup):
    ```bash
    # Example: Run publisher inside a temporary container on the same network
    docker-compose run publisher python publisher.py "Your prompt here"

    # Example: Run result consumer inside a temporary container
    docker-compose run result_consumer python result_consumer.py
    ```
    *Note: The default `docker-compose.yml` might need adjustments to define `publisher` and `result_consumer` services if they aren't already set up for `docker-compose run`.*

5.  **Troubleshooting Docker issues**:
    If you encounter issues with the Docker containers:
    ```bash
    cd docker
    docker-compose down -v # Stop and remove containers and volumes
    # For a complete Docker system reset (use with caution):
    # docker system prune -a
    docker-compose up --build -d # Try starting again
    ```
### Option 2: Manual Host Installation with Conda + RabbitMQ (Docker)

This method runs RabbitMQ in Docker but the Worker, Publisher, and Consumer directly on your host machine using a Conda environment.

1.  **Start RabbitMQ using Docker**:
    Navigate to the `docker` directory and start *only* the RabbitMQ service:
    ```bash
    cd docker
    docker-compose up -d rabbitmq # Start only rabbitmq in detached mode
    ```
    Verify it's running: `docker ps` (you should see `docker_rabbitmq_1`).

2.  **Create and activate a Conda environment**:
    ```bash
    conda create -n bielik python=3.9 -y
    conda activate bielik
    ```

3.  **Install PyTorch with Conda (Matching Your GPU Driver)**:
    *   **Check your driver's CUDA capability**: Open a terminal and run `nvidia-smi`. Look for the "CUDA Version" listed in the top right corner (e.g., `11.8`, `12.1`, `12.6`).
    *   **Go to the official PyTorch website**: [https://pytorch.org/get-started/locally/](https://pytorch.org/get-started/locally/)
    *   **Use the configuration tool**: Select:
        *   PyTorch Build: Stable
        *   Your OS: Linux
        *   Package: Conda
        *   Language: Python
        *   Compute Platform: Choose a **CUDA version** that is **less than or equal to** the version reported by `nvidia-smi`. For example, if `nvidia-smi` shows `12.6`, choose `CUDA 12.1`. If it shows `11.8`, choose `CUDA 11.8` or `CUDA 11.7`.
    *   **Run the generated command**: Copy the command provided by the website and run it in your activated `bielik` environment. It will look similar to one of these:

        ```bash
        # Example command for CUDA 12.1 (Use the one from the website!)
        conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia

        # Example command for CUDA 11.8 (Use the one from the website!)
        # conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia
        ```
    *   **CPU Only (Alternative)**: If you don't have an NVIDIA GPU or don't want GPU support:
        ```bash
        # conda install pytorch torchvision torchaudio cpuonly -c pytorch
        ```
    *   **Why this matters**: Installing a PyTorch version built for a CUDA version compatible with your NVIDIA driver is crucial for GPU acceleration to work correctly.

4.  **Install other dependencies using pip**:
    ```bash
    # Ensure pip is up-to-date
    pip install --upgrade pip

    # Install required packages
    pip install pika==1.2.1 vllm==0.7.2 transformers accelerate==1.0.1 qwen_vl_utils python-dotenv
    ```
    *Note: We use the latest compatible `transformers` version.*

5.  **Run the components on the Host**:
    Open separate terminals for each component *after* activating the `bielik` conda environment (`conda activate bielik`).

    *   **Terminal 1: Start the Worker**
        ```bash
        # Select the model using an environment variable
        export MODEL_NAME=gpt2  # or 'qwen'

        # Run the worker script (ensure you are in the project's root directory)
        python worker.py
        ```

    *   **Terminal 2: Run the Publisher**
        ```bash
        # Run the publisher script (ensure you are in the project's root directory)
        # Add your prompt as an argument
        python publisher.py "Translate the following English text to French: 'Hello, world!'"
        ```

    *   **Terminal 3: Run the Result Consumer**
        ```bash
        # Run the result consumer script (ensure you are in the project's root directory)
        python

### Option 3: Direct Installation using setup.sh (Potentially Less Stable)

*This method attempts to install dependencies directly using a shell script. It might be less reliable than Conda or Docker due to system variations.*

1.  **Run the setup script**:
    ```bash
    chmod +x setup.sh
    ./setup.sh
    ```
    *You may need to manually install RabbitMQ separately if not handled by the script.*

2.  **Selecting a model and running**:
    ```bash
    export MODEL_NAME=gpt2  # or 'qwen'
    # Start RabbitMQ if installed manually
    # Then run the python scripts as shown in Option 2 (step 5)
    python worker.py
    # python publisher.py ...
    # python result_consumer.py ...
    ```

## Usage (Manual Host Installation Example)

1.  Ensure RabbitMQ is running (e.g., via `docker-compose up -d rabbitmq`).
2.  Activate your conda environment (`conda activate bielik`).
3.  Start the worker in one terminal: `export MODEL_NAME=qwen && python worker.py`.
4.  Start the result consumer in another terminal: `python result_consumer.py`.
5.  Send a task using the publisher in a third terminal: `python publisher.py "Generate a short story about a robot learning to paint."`.
6.  Observe the output in the result consumer's terminal.

## Notes

- GPU acceleration (CUDA) is highly recommended for significantly better performance with the AI models.
- The RabbitMQ management console (if using Docker) is available at http://localhost:15672 (default credentials: guest/guest).
- Ensure the `RABBITMQ_HOST` and `RABBITMQ_PORT` environment variables are correctly set or defaulted to `localhost` and `5672` respectively in the Python scripts if not using the default Docker setup.