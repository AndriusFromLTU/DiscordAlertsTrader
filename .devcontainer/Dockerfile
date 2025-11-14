# Use Python 3.11 slim image
FROM python:3.11-slim

# Avoid warnings by switching to noninteractive
ENV DEBIAN_FRONTEND=noninteractive

# Configure apt and install packages
RUN apt-get update \
    && apt-get -y install --no-install-recommends \
    # Common utilities
    git \
    curl \
    wget \
    ca-certificates \
    # Build essentials for compiling Python packages
    build-essential \
    gcc \
    g++ \
    # Qt dependencies for PySimpleGUIQt
    libqt6widgets6 \
    libqt6gui6 \
    libqt6core6 \
    qt6-base-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libxkbcommon-x11-0 \
    libdbus-1-3 \
    # X11 libraries for GUI support
    libx11-xcb1 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-xinerama0 \
    libxcb-xfixes0 \
    libxcb-shape0 \
    # Additional dependencies
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Switch to non-root user
USER $USERNAME

# Upgrade pip
RUN pip install --upgrade pip

# Set working directory
WORKDIR /workspace

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    QT_MAC_WANTS_LAYER=1 \
    QT_X11_NO_MITSHM=1 \
    DISPLAY=:0

# Switch back to dialog for any ad-hoc use of apt-get
ENV DEBIAN_FRONTEND=dialog
