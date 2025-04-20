# Customer Support Assistant Backend

A FastAPI backend for a customer support assistant that handles user authentication, support tickets, and integrates with Groq AI for generating responses.

## Architecture

This project follows a service-oriented architecture with clean separation of concerns:

### Key Components

- **API Layer**: FastAPI endpoints that handle HTTP requests and responses
- **Service Layer**: Business logic encapsulated in service classes
- **Repository Layer**: Data access abstraction for database operations
- **Model Layer**: SQLAlchemy ORM models for database entities
- **Schema Layer**: Pydantic models for data validation and serialization

### Design Patterns Used

1. **Repository Pattern**: Abstracts data access logic to make it testable and maintainable.
   - Implementation: Each entity has its own repository (e.g., `UserRepository`, `TicketRepository`)
   - Benefit: Easy to swap database implementations or add caching

2. **Dependency Injection**: Services and repositories are injected as dependencies.
   - Implementation: FastAPI's built-in dependency injection system
   - Benefit: Improved testability and loose coupling between components

3. **Service Pattern**: Business logic encapsulated in dedicated service classes.
   - Implementation: `AuthService`, `TicketService`, and `AIService`
   - Benefit: Reusable business logic, separate from API endpoints

4. **Factory Pattern**: Used for creating database sessions.
   - Implementation: `get_db` function creates and manages database sessions
   - Benefit: Centralized creation and management of resources

## Setup Instructions

### Prerequisites

- Docker and Docker Compose
- Poetry (for local development)
- Groq API key

### Environment Variables

Create a `.env` file based on the provided `.env.example`:

```
# Security
SECRET_KEY=CUSTOMER_SUPPORT_SECRET_KEY

# PostgreSQL
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=support_assistant

# Groq API
GROQ_API_KEY=GROQ_API_KEY
GROQ_MODEL=llama-3.3-70b-versatile
```

### Using Docker

1. Build and start the services:
   ```bash
   docker-compose up -d --build
   ```

2. The API will be available at `http://localhost:8000`

### Local Development

1. Install dependencies:
   ```bash
   poetry install
   ```

2. Start a PostgreSQL database (or use Docker):
   ```bash
   docker-compose up -d db
   ```

3. Run the API:
   ```bash
   poetry run uvicorn app.main:app --reload
   ```

## Swagger UI Documentation

### API Documentation
The API documentation is available at `http://localhost:8000/docs`.

## API Endpoints

### Authentication

- **POST /auth/signup** - Register a new user
  - Request body: `{ "email": "user@example.com", "password": "password" }`
  
- **POST /auth/login** - Login and get JWT token
  - Request body: `{ "username": "user@example.com", "password": "password" }`

### Tickets

- **GET /tickets** - List user's tickets
  - Headers: `Authorization: Bearer {token}`
  
- **POST /tickets** - Create a new ticket
  - Headers: `Authorization: Bearer {token}`
  - Request body: `{ "title": "Issue title", "description": "Detailed description" }`
  
- **GET /tickets/{ticket_id}** - Get a specific ticket with messages
  - Headers: `Authorization: Bearer {token}`
  
- **POST /tickets/{ticket_id}/messages** - Add a message to a ticket
  - Headers: `Authorization: Bearer {token}`
  - Request body: `{ "content": "Message content" }`
  
- **GET /tickets/{ticket_id}/ai-response** - Stream an AI response (SSE)
  - Headers: `Authorization: Bearer {token}`

## Database Schema

The database consists of the following tables:

- **users**: Store user information and credentials
- **tickets**: Support tickets created by users
- **messages**: Messages within tickets from both users and AI

## Challenges and Solutions

1. **Streaming AI Responses**: Implementing Server-Sent Events (SSE) for streaming AI responses was challenging. The solution was to use FastAPI's `StreamingResponse` and yield chunks of data as they arrive from the Groq API.

2. **Authentication**: Implementing JWT-based authentication and ensuring proper user authorization was complex. I created a dedicated `AuthService` with clear separation of authentication logic.

3. **Repository Pattern**: Implementing a generic repository pattern that works with SQLAlchemy was challenging. I created a base repository class with generic types to solve this.

## Future Improvements

With more time, these are the areas I would improve:

1. **Unit and Integration Tests**: Add comprehensive test coverage for all components
2. **Error Handling**: Implement more detailed error handling and logging
3. **Caching**: Add Redis caching for frequently accessed data
4. **Webhooks**: Add webhook support for external integrations
5. **Message Attachments**: Support file attachments in messages
6. **Rate Limiting**: Implement rate limiting for API endpoints
7. **AI Model Fallback**: Implement fallback mechanisms if Groq API is unavailable
8. **Monitoring and Telemetry**: Add observability with Prometheus and Grafana
9. **Pagination**: Improve endpoint pagination for large datasets
10. **Real-time Notifications**: Add WebSocket support for real-time notifications