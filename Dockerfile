# Use the official Ubuntu 24.04 as a base image
FROM ubuntu:24.04

# Set a non-interactive frontend for package installations to avoid prompts
ENV DEBIAN_FRONTEND=noninteractive

# Update package lists and install necessary software
# - build-essential is required for Rust and other compiled languages
# - python-is-python3 allows using the 'python' command
# - python3-pip provides the 'pip' command
RUN apt-get update && apt-get install -y \
    nano \
    curl \
    git \
    python3 \
    python3-pip \
    python-is-python3 \
    build-essential \
    gradio \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user 'student' for security
RUN useradd -m student

# Switch to the 'student' user to install Rust in their home directory
USER student
WORKDIR /home/student

# Install the Rust toolchain (rustc, cargo, etc.) using the official rustup installer
# The '-y' flag automates the installation process
RUN curl --proto '=https' --tlsv1.2 -sSf [https://sh.rustup.rs](https://sh.rustup.rs) | sh -s -- -y

# Add Cargo's bin directory to the PATH environment variable.
# This makes 'rustc' and 'cargo' commands available in the shell.
ENV PATH="/home/student/.cargo/bin:${PATH}"

# The command to run when the container starts. It will launch a bash shell
# as the 'student' user with the updated PATH.
CMD ["/bin/bash"]

