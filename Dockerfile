# Use the official Ubuntu 22.04 as a base image
FROM ubuntu:22.04

# Set a non-interactive frontend for package installations to avoid prompts
ENV DEBIAN_FRONTEND=noninteractive

# Update package lists and install necessary software
# - openssh-server is added for SSH capability
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
    openssh-server \
    && rm -rf /var/lib/apt/lists/*

# Configure SSH Server to allow password authentication
RUN mkdir /var/run/sshd
RUN sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config
RUN sed -i 's/PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config

# Expose the SSH port (good practice)
EXPOSE 22

# FIX: Remove the file that enables the 'externally-managed' environment error
RUN find /usr/lib/ -name "EXTERNALLY-MANAGED" -exec rm {} \;

# Create a non-root user 'student' for security
RUN useradd -m student

# Set a default password for the 'student' user
# The default password is set to 'student'. You can change it here.
RUN echo 'student:student' | chpasswd

# Switch to the 'student' user to perform user-specific installations (Rust)
USER student
WORKDIR /home/student

# Install the Rust toolchain (rustc, cargo, etc.) as the student user
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

# Switch back to root before setting the final CMD
USER root

# Add Cargo's bin directory to the student's PATH by adding it to their bash profile
RUN echo 'export PATH="/home/student/.cargo/bin:${PATH}"' >> /home/student/.bashrc

# The command to run when the container starts:
# 1. Start the SSH daemon service as root.
# 2. Switch to the 'student' user and launch their default login shell.
CMD service ssh start && su - student

