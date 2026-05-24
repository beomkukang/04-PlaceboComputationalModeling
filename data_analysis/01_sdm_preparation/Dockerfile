FROM ubuntu:22.04

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies for SDM-PSI binaries
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libgl1-mesa-glx \
    libfontconfig1 \
    libxrender1 \
    libxi6 \
    libxcb1 \
    libx11-6 \
    libsm6 \
    libice6 \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libgtk-3-0 \
    libgbm1 \
    libasound2 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libpango-1.0-0 \
    libcairo2 \
    && rm -rf /var/lib/apt/lists/*

# Copy SDM Linux binary
COPY SdmPsiGui-linux64-v6.23/SdmPsiGui-linux64-v6.23/ /opt/sdm/

# Make all binaries executable
RUN chmod +x /opt/sdm/sdm \
    /opt/sdm/bin/linux64/sdm_parse \
    /opt/sdm/bin/linux64/sdm_core \
    /opt/sdm/bin/linux64/sdm_correct \
    /opt/sdm/bin/linux64/imgcalc \
    /opt/sdm/bin/linux64/sdmimage2nii 2>/dev/null; true

# Add SDM to PATH
ENV PATH="/opt/sdm:/opt/sdm/bin/linux64:${PATH}"

# Working directory for mounted data
WORKDIR /data
