# Use the official Ubuntu 22.04 as a base image
FROM ubuntu:22.04

# Set a non-interactive frontend for package installations to avoid prompts
ENV DEBIAN_FRONTEND=noninteractive

# Update package lists and install necessary software
# - iputils-ping provides the 'ping' command
# - iproute2 provides the modern 'ip addr' command
# - net-tools provides the legacy 'ifconfig' command
RUN apt-get update && apt-get install -y \
    nano \
    curl \
    git \
    python3 \
    python3-pip \
    python-is-python3 \
    build-essential \
    iputils-ping \
    iproute2 \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

# FIX: Remove the file that enables the 'externally-managed' environment error
RUN find /usr/lib/ -name "EXTERNALLY-MANAGED" -exec rm {} \;

# Create a non-root user 'student' for security
RUN useradd -m student

# Switch to the 'student' user to install Rust in their home directory
USER student
WORKDIR /home/student

# Install the Rust toolchain (rustc, cargo, etc.) using the official rustup installer
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

# Add Cargo's bin directory to the PATH environment variable.
ENV PATH="/home/student/.cargo/bin:${PATH}"

# The command to run when the container starts.
CMD ["/bin/bash"]
