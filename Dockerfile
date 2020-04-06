FROM mcr.microsoft.com/dotnet/core/sdk:3.1 AS build
WORKDIR /src
COPY server/src .
RUN dotnet publish DpWeb -c Release -o /app --self-contained --runtime=linux-x64

FROM python:3.8-slim
WORKDIR /app
# Python dependencies
RUN pip install opencv-python torch torchvision
# .NET Core dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libicu63 \
    && rm -rf /var/lib/apt/lists/*
# Configure web servers to bind to port 80 when present
ENV ASPNETCORE_URLS=http://+:80 \
    # Enable detection of running in a container
    DOTNET_RUNNING_IN_CONTAINER=true
COPY python_demo/inout.py .
COPY python_demo/key_frame_selection.py .
COPY --from=build /app .
CMD ./DpWeb