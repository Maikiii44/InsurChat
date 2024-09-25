# Chatbot README

## Overview

This project contains a chatbot built using FastAPI, and it is designed to serve two different types of products: **B2B (Business-to-Business)** and **B2C (Business-to-Consumer)**. The distinction between these products is reflected in the structure of the project.

### Project Structure

Within the `rag` folder, you'll find two main applications:
- **`app_b2b`**: This is the FastAPI application designed for B2B interactions, with endpoints specific to B2B use cases.
- **`app_b2c`**: This is the FastAPI application designed for B2C interactions, with endpoints specific to B2C use cases.

### Dummy Application

In order to facilitate development without incurring costs (such as charges for API calls to OpenAI or using VectorDB), the project includes a **dummy application**. This dummy app mirrors the same endpoints as the main applications but does not connect to OpenAI or VectorDB.

The dummy app is located in the `rag` folder, which simulates the same behavior as the actual B2B and B2C applications but without generating costs. You can use it to test your code and workflows locally.

## How to Build and Run the Application

This project uses Docker for containerization, allowing you to quickly build and run the desired app. However, before building the Docker image, you need to configure which application will be used (B2B, B2C, or Dummy).

### Steps to Build and Run

1. **Choose the Application**:  
Go to the `Dockerfile` and locate the part where the application is specified. This will look something like:

Modify this line to point to the desired application. Here are the available options:
- For **B2B**: Change to `rag.app_b2b:app`
- For **B2C**: Change to `rag.app_b2c:app`
- For **Dummy B2B**: Use `rag.dummy_app_b2b:app`
- For **Dummy B2C**: Use `rag.dummy_app_b2c:app`

2. **Build the Docker Image**:  
After selecting the appropriate app in the `Dockerfile`, you can build the Docker image:
```bash
docker build -t chatbot-image .
